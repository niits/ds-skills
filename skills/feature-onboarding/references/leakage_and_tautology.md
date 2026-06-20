# Leakage and Tautology

Two distinct ways a feature "cheats". Both inflate offline metrics and both collapse
in production. The first is the one teams underweight.

```
        ┌─────────────────────────┐        ┌───────────────────────────┐
        │ 6a Temporal leakage     │        │ 6b Definitional tautology │
        │ uses information from   │        │ measures the label's own  │
        │ AFTER the cutoff        │        │ definition (same quantity)│
        └─────────────────────────┘        └───────────────────────────┘
```

---

## 6a. Temporal / point-in-time leakage — the common killer

The feature snapshot at cutoff `T` must be computable using **only data that existed
at or before T**. Violations are usually subtle and pass every correlation test.

### Draw the timeline, every time

```
   feature inputs        cutoff        embargo        label window
   ───────────────►        T        ──── g ────►      [T+g , T+g+h]
   (data <= T only)                                  (outcome observed here)
```

- **Cutoff `T`** — when the score would be produced in production.
- **Embargo `g`** — a deliberate gap. In credit, the outcome (e.g. 90+ days past due)
  needs time to materialize; in lead scoring the conversion happens days/weeks later.
  Without an embargo, features computed "at T" can quietly include the very early
  part of the outcome.
- **Label window `[T+g, T+g+h]`** — where the outcome is observed. Nothing from this
  window may touch the feature.

### Leak sources to check explicitly

1. **Future rows.** Any aggregation that accidentally includes rows with
   `event_date > T`. Filter the source to `<= T` **before** aggregating, not after.
2. **Late-arriving / restated data.** A row *dated* `T` but *written* after `T`
   (back-dated corrections, restatements, slowly-updated dimensions). If your table
   has an `as_of` / ingestion timestamp distinct from the business date, filter on
   the **ingestion** time too: only use what was *knowable* at T.
3. **Post-outcome fields.** Columns populated as a consequence of the outcome
   (e.g. `collections_flag`, `chargeoff_amount`, `won_date`). These are pure leakage.
4. **Entity-level joins to "current" dimensions.** Joining today's customer segment
   onto a historical snapshot imports the future. Use the dimension *as of T*.

### On a Delta lakehouse, an `ingested_at` filter is not enough

Delta tables **mutate in place**. A `MERGE`/`UPDATE` that backfills or restates an
SCD-1 dimension overwrites history — the old value is gone, and a plain `ingested_at`
column on the current row will *not* tell you what was knowable at T. Concretely:

- **Use bitemporal sources**: keep both a `business_date` (when it was true) and a
  commit/ingestion version (when it was recorded). Prefer **append-only / SCD-2**
  snapshots for any source that feeds features, so the as-of state is reconstructable.
- **Reconstruct "as of T" explicitly**, don't join to the current table:

```python
# Per-row AS-OF (point-in-time) join. Each population row carries its OWN cutoff
# (`cutoff_date`); for each, take the latest dimension row effective at/before it.
# A single global scalar cutoff gives a FIXED snapshot, not an as-of join -- wrong for
# multi-cutoff training sets and for recsys (every interaction has its own timestamp).
cand = (population.join(dim, "entity_id")                       # inequality / range join
        .filter(F.col("effective_date") <= F.col("cutoff_date")))
w = (Window.partitionBy("entity_id", "cutoff_date")
        .orderBy(F.col("effective_date").desc(),
                 F.col("commit_version").desc()))               # explicit tiebreaker ->
features = (cand.withColumn("rn", F.row_number().over(w))       # deterministic (Phase 11)
                .filter("rn = 1").drop("rn"))
# Range joins are costly: filter `population` to the needed entities/time span first,
# and lean on Databricks range-join optimization. For tight latency, Delta/feature-store
# point-in-time lookups (a declared timestamp_lookup_key) do this for you.
```

- If the source is SCD-1 (overwritten), Delta **time travel** (`VERSION AS OF` /
  `TIMESTAMP AS OF`) or **Change Data Feed** is a **last resort, not a co-equal option**:
  - Time travel is bounded by `delta.logRetentionDuration` and
    `deletedFileRetentionDuration` (**default 30 days**), and **`VACUUM` permanently
    deletes** the old files. Training on a 12-month label horizon against a table that
    retains 30 days means the as-of reconstruction **silently falls back to current
    state** — reintroducing the leak.
  - CDF must be **enabled before** the writes you want to read; it cannot reconstruct
    history retroactively.
  - **The real fix is an append-only / SCD-2 snapshot** (preferred above). Treat
    time-travel/CDF as a stopgap and document the retention window you depend on.
- **SCD-1 backfill is a silent point-in-time killer**: a "current segment" joined onto
  a historical snapshot imports the future even though every timestamp looks fine.

### The decisive test

A feature can have **`|r| < 0.3` with a label proxy and still leak** — because the
leak is informational, not a simple linear association. Correlation tests do **not**
detect temporal leakage. Only the timeline audit does. Treat 6a as a code/data review,
not a statistic.

> Practical tell: a feature that is *individually* far stronger out-of-sample than any
> plausible business mechanism would suggest is leaking until proven otherwise.

---

## 6b. Definitional tautology

Here the feature is point-in-time clean but measures the **same underlying quantity**
the label is defined on.

### Three questions

1. **What defines the label?** Which metric, which threshold, which horizon?
   (e.g. "default = days-past-due ≥ 90 within 12 months").
2. **Does the feature directly measure that metric?**
   - feature ≈ `Δ(metric that defines the label)` → **tautological**.
   - feature = a derived/adjusted variant of that metric → **needs verification**.
3. **Causal direction:**

| Relationship | Verdict |
|---|---|
| feature → label (feature precedes and predicts) | OK |
| common root cause → feature + label (co-symptoms) | OK, but expect weaker, less stable signal |
| feature ≈ label (same quantity, different name) | **DROP** |

### Verification: correlate with a label proxy

Build a **direct proxy of the label-defining metric** (the continuous quantity the
threshold is applied to) and correlate the suspect feature against it:

```python
r = df[suspect_feature].corr(df[label_metric_proxy])   # Pearson or Spearman
```

| `|r|` vs label proxy | Conclusion |
|---|---|
| ≥ 0.8 | Essentially a proxy for the label → drop, or document with extreme care |
| [0.3, 0.8) | Investigate: mechanical (drop) vs behavioral (may keep) |
| < 0.3 | **Not flagged** by this test → keep — but see caveat |

> **Caveat — these are screening bands, not decision boundaries.** A low `|r|` does
> **not prove** a feature is non-tautological: the relationship may be non-linear (try
> Spearman too), or the proxy you built may be the wrong one. This test can only
> *flag* circularity, not *clear* it — exactly as temporal leakage (6a) cannot be
> cleared by correlation at all. Use these cutoffs to prioritize investigation, not to
> certify innocence.

### Key lesson

**High IV does not validate a feature.** An IV of 0.9 sourced from the label's own
definition is circular reasoning dressed as signal — worthless for prediction because
in production you won't have the label-derived quantity at scoring time (or if you do,
you don't need a model). This is exactly why any IV > 0.5 routes back to this check.

---

## Quick audit checklist

- [ ] Timeline drawn: cutoff, embargo, label window explicit.
- [ ] Source filtered to `business_date <= T` **and** `ingested_at <= T`.
- [ ] No post-outcome columns in the feature set.
- [ ] Dimensions joined *as of T*, not "current".
- [ ] Label definition written down (metric + threshold + horizon).
- [ ] Each high-IV feature correlated against a label-metric proxy.
- [ ] Any `|r| > 0.8` vs proxy resolved before Go/No-Go.
