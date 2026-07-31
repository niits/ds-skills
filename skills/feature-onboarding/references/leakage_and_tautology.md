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

The feature snapshot at cutoff `T` must be computable using only data available under
the declared cutoff convention. Batch snapshots may use a finalized closed period;
event-driven systems normally require records to precede the scoring transaction.

### Draw the timeline, every time

```
   feature inputs        cutoff          gap          label window
   ───────────────►        T        ──── g ────►      (T+g , T+g+h]
   (eligible at T only)                              (outcome observed here)
```

- **Cutoff `T`** — when the score would be produced in production.
- **Gap `g`** — optional and justified by the estimand, operational latency, or data
  latency. Outcome maturation determines when labels are complete; it does not by
  itself require delaying the start of the outcome window.
- **Label window `(T+g, T+g+h]` by default** — where the outcome is observed. A
  different non-overlapping convention requires a stable event-sequence rule. Nothing from this
  window may touch the feature.

### Leak sources to check explicitly

1. **Future rows.** Any aggregation that violates the ledger's declared boundary.
   Apply the cutoff predicate **before** aggregating: normally `< T` for event-driven
   scoring, or `<= T` only for a finalized closed-period convention.
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
# Per-row bitemporal AS-OF join. Each scoring row has a stable unique key and cutoff.
# A single global scalar cutoff gives a FIXED snapshot, not an as-of join -- wrong for
# multi-cutoff training sets and for recsys (every interaction has its own timestamp).
# `eligible_at_cutoff` implements the ledger's declared open/closed boundary. Use
# strict `< cutoff_ts` for event-driven scoring unless a sequence key proves ordering.
join_ok = ((population.entity_id == dim.entity_id) &
           eligible_at_cutoff(dim.effective_ts, population.cutoff_ts) &
           eligible_at_cutoff(dim.recorded_ts, population.cutoff_ts))
cand = population.join(dim, join_ok, "left")
w = (Window.partitionBy("population_row_id")
        .orderBy(F.col("effective_ts").desc(),
                 F.col("recorded_ts").desc(),
                 F.col("source_row_id").desc()))
features = (cand.withColumn("rn", F.row_number().over(w))
                .filter("rn = 1").drop("rn"))
# Range joins are costly: filter `population` to the needed entities/time span first,
# and lean on Databricks range-join optimization. For tight latency, Delta/feature-store
# point-in-time lookups (a declared timestamp_lookup_key) do this for you.
```

- If the source is SCD-1 (overwritten), Delta **time travel** (`VERSION AS OF` /
  `TIMESTAMP AS OF`) or **Change Data Feed** is a **last resort, not a co-equal option**:
  - Time travel is bounded by separately configured log and deleted-file retention.
    Verify actual table properties rather than assuming one default, and test that all
    required historical versions remain readable. `VACUUM` can permanently delete old
    files. Missing history must fail closed; never substitute current state.
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

Here the feature mechanically contains, reconstructs, or overlaps the realized
label-window quantity. A pre-cutoff history of the same kind of business measure is
not automatically tautological.

### Three questions

1. **What defines the label?** Which metric, which threshold, which horizon?
   (e.g. "default = days-past-due ≥ 90 within 12 months").
2. **Does the feature directly measure that metric?**
   - feature uses the realized label-window metric → **tautological**.
   - feature uses only pre-cutoff history of that metric → potentially valid; verify timing and intended use.
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
| ≥ 0.8 | Strong investigation trigger; inspect lineage, timing, and formula overlap |
| [0.3, 0.8) | Investigate: mechanical (drop) vs behavioral (may keep) |
| < 0.3 | Not flagged by this test; continue lineage, timing, and formula-overlap review |

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
- [ ] Historical values are reconstructable as known at each cutoff; both effective/event time and recorded/available time satisfy the declared boundary.
- [ ] No post-outcome columns in the feature set.
- [ ] Dimensions joined *as of T*, not "current".
- [ ] Label definition written down (metric + threshold + horizon).
- [ ] Each high-IV feature correlated against a label-metric proxy.
- [ ] Correlation flags are resolved through lineage and formula review before Go/No-Go; no threshold independently passes or fails a feature.
