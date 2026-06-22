# Null Handling

The original convention was right in spirit but conflated two genuinely different
things: **structural absence** ("this entity has no such product, so the value cannot
exist") versus **unknown** ("the value exists but we don't have it"). Treating them
the same either fabricates signal or hides it.

---

## The core distinction

| Situation | Meaning | Right treatment |
|---|---|---|
| Entity holds no deposit account → `deposit_balance` is NaN | **Structural absence** — value genuinely is "none" | Fill 0 **and** add a `has_deposit` flag |
| Sensor/source missing for an entity that *does* have the product | **Unknown** | Leave NaN (GBM) / impute + flag (scorecard) |
| Lag pct_change with no prior period | **Genuinely unknown** (no baseline) | Leave NaN — do not invent a change |
| Lag absolute diff with no prior period | No prior = no change observed | Fill 0 |
| Ratio/share with zero denominator | Undefined, not zero | NaN, **not** 0 (see division guard) |

### Always pair "fill 0" with a missingness flag

If you fill 0 for structural absence, the model cannot tell "0 because absent" from
"0 because genuinely zero". Add an explicit indicator so the model can learn the
difference instead of you choosing for it:

```python
df = df.withColumn("has_deposit", F.col("deposit_balance").isNotNull().cast("int"))
df = df.withColumn("deposit_balance", F.coalesce("deposit_balance", F.lit(0.0)))
```

This is the single most common fix: the original "fill 0 for absence-based features"
rule is fine **only** when accompanied by the flag. Without it you are silently
asserting absence == zero behavior, which can fabricate or mask signal.

---

## Mode dependence

The whole convention changes with **Model Mode** (see SKILL.md):

### GBM mode
- Trees split on NaN natively — **leave genuine unknowns as NaN**. Imputing invents
  information and can bias splits.
- Structural-absence → `0 + flag` as above.
- Ratios with zero denominator → NaN (let the tree route them).

### Scorecard mode (WoE + logistic)
- Logistic regression has **no native NaN** — every value must be defined.
- Best practice: bin NaN into its **own WoE group** (the binner treats "missing" as a
  category and assigns it a WoE). This preserves the information in missingness
  without arbitrary imputation.
- If you must impute, impute **and** add a flag; never impute silently with the mean
  (it injects a fake central-tendency value and distorts monotonic bins).

---

## Division-by-zero and infinity guards

Ratio and per-unit features are the usual source of `inf`/`NaN` artifacts. Guard at
computation time, and verify in Phase 11 that no infinities survived.

```python
# Safe ratio: undefined when denominator is 0 -> NaN, never inf
df = df.withColumn(
    "dep_share",
    F.when(F.col("total_balance") > 0, F.col("deposit_balance") / F.col("total_balance"))
     .otherwise(F.lit(None))
)
# Verification (Phase 11 data-quality layer, NOT inside the compute function).
# The guarded ratio ABOVE cannot emit inf -- this check is a safety net for any
# *unguarded* ratio elsewhere in the pipeline. Spark float semantics (note: Spark SQL
# deliberately DIVERGES from pandas/IEEE-754):
#   col == float("inf")  -> works (inf compares equal)
#   col == float("nan")  -> in SPARK this is TRUE (Spark defines NaN = NaN so grouping/
#                           sorts are well-defined); in pandas/Python it is False.
#   -> Use F.isnan() regardless: it is the clear, portable way to catch NaN.
inf_rows = df.filter((F.col("dep_share") == float("inf")) |
                     (F.col("dep_share") == float("-inf")) |
                      F.isnan("dep_share"))
assert inf_rows.limit(1).count() == 0      # one-time check; keep eager counts out of
                                           # the production compute path (Anti-pattern #12)
```

> This inf/NaN assertion is a **one-time integration check** (Phase 11) or a job in a
> separate data-quality layer (e.g. Delta Live Tables expectations) — **not** a
> diagnostic count inside the feature-compute function, which must stay free of eager
> actions.

- `x / 0` → define as NaN (unknown), not 0 and not inf.
- `log(0)` / `log(negative)` → guard the domain before applying.
- pct_change from a 0 baseline → NaN, not a huge or infinite number.

---

## Document the convention per feature

In the module docstring, list each feature's null treatment and *why* it follows
absence vs unknown. Downstream consumers (and the next person re-binning for
scorecard) need to know whether a 0 means "none" or "genuinely zero".
