# Optimizing Wide Join Chains for Modeling Datasets

Building a modeling dataset usually means: take a **label table**, left-join it to **many feature tables** (Feature Store on Unity Catalog + extra tables on Delta paths), run an MLlib `Pipeline`, and write the result to Delta. When the chain is wide (10+ joins) and the feature tables are large, the final `fit` + `transform` + `write` cell can run for hours.

Everything here is **query-level or session-level** — no `OPTIMIZE`, `ANALYZE TABLE`, or `ALTER TABLE`. A DS can apply all of it without admin rights (the Delta optimize-write option requires write access on the output table or your own scratch schema).

---

## How to diagnose it from the physical plan

Pull the full physical plan from the Spark UI SQL tab (it can be 100+ nodes). Read it per feature table, top to bottom:

| What to check | Where in the plan | What it means |
|---|---|---|
| Join type | `BroadcastHashJoin` vs `SortMergeJoin` | SMJ on the right side = full shuffle of that table |
| Rows / bytes shuffled | `ShuffleQueryStage` → `rowCount`, `sizeInBytes` | The actual cost; compare to label row count |
| Entity-key filter | scan `PushedFilters` | If only the time key is filtered, the entity key is not pruned |
| Dynamic Partition Pruning | `dynamicpruningexpression(... IN subquery)` in the scan | DPP active on that table |
| Stats sanity | `sizeInBytes` near the top of the chain | Values like `4.14E+94 B` = Catalyst stat error accumulated across joins |
| Repeated subtrees | identical scan subtrees appearing twice | The DAG is executed more than once (e.g. `fit` + `transform`) |

**The usual root cause:** right-side **over-shuffle**. Each feature table shuffles all rows in its static time range, even though only the entity keys present in the (small) label table can ever match. The largest table dominates total runtime.

---

## Worked example — before

```python
label_df = spark.table("uc.ml.labels")              # ~30M rows
feature_tables = {
    "A": spark.table("uc.fs.feature_a"),            # 374M rows / 177 GiB
    "B": spark.table("uc.fs.feature_b"),            # 374M rows /  83 GiB
    "C": spark.table("uc.fs.feature_c"),            # 240M rows /  63 GiB
    # ... D, E, F + 6 additional Delta-path tables
}

modeling_df = label_df
for name, feat in feature_tables.items():
    modeling_df = modeling_df.join(feat, on=["entity_key", "time_key"], how="left")

pipeline = Pipeline(stages=[...])
model = pipeline.fit(modeling_df)                                  # execution #1 of the whole chain
model.transform(modeling_df).write.format("delta") \
    .partitionBy("time_key").save(output_path)                     # execution #2 of the whole chain
```

Problems: ~400 GiB right-side shuffle, the chain runs twice (lazy `modeling_df`), 200 shuffle partitions over 400 GiB (~900 MiB each → spill/OOM), and DPP fires on only some tables.

---

## Worked example — after

```python
from pyspark.sql.functions import broadcast

# --- Session configs: size parallelism to the total shuffle volume ---
spark.conf.set("spark.sql.shuffle.partitions", 2000)                      # ~200 MiB/partition
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", 256 * 1024 * 1024)
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", True)
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", 3)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 100 * 1024 * 1024) # broadcast the entity-key list
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", True)      # needs write access on output

# --- Fix 1: semi-join pre-filter every feature table on the entity key ---
label_entities = label_df.select("entity_key").distinct()
for name, feat in feature_tables.items():
    feature_tables[name] = feat.join(broadcast(label_entities), on="entity_key", how="leftsemi")

# --- Fix 3: repartition the left side once, on the join keys ---
modeling_df = label_df.repartition(2000, "entity_key", "time_key")

# --- Fix 2: join smallest -> largest so AQE has stats before the biggest stage ---
for name in ["F", "E", "D", "C", "B", "A", *additional_tables]:   # ascending size
    modeling_df = modeling_df.join(feature_tables[name], on=["entity_key", "time_key"], how="left")

# --- Fix 5: materialize ONCE before MLlib so the chain doesn't run twice ---
modeling_df = modeling_df.localCheckpoint(eager=True)

model = pipeline.fit(modeling_df)
model.transform(modeling_df).write.format("delta") \
    .partitionBy("time_key").save(output_path)
```

---

## What changes in the physical plan

The single long DAG splits into two:

- **DAG A (checkpoint):** label scan → 11 left-outer joins, each now preceded by a `BroadcastHashJoin (leftsemi)` pre-filter → write to executor-local storage. Runs **once**. Each `ShuffleQueryStage` is far smaller.
- **DAG B (fit + write):** scan from the checkpoint → MLlib stages → `WriteIntoDeltaCommand`. **No join chain at all.**

Representative before/after:

| Metric | Before | After |
|---|---|---|
| Total right-side shuffle | ~400 GiB | ~30–35 GiB (~92% ↓) |
| Largest table (A) shuffle | 177 GiB / 374M rows | ~14 GiB / ~30M rows |
| Shuffle partition size | ~900 MiB | ~200 MiB |
| Join-chain executions | 2 | 1 |
| Delta output | many small files | optimized write |

---

## Why each fix works

1. **Semi-join pre-filter (biggest win).** A left-outer join can only match the entity keys present in the label table. `leftsemi` against the broadcast key list drops the rest *before* the shuffle, while leaving outer-join semantics intact (unmatched labels still get nulls). See `join_strategies.md` §7.
2. **Smallest → largest join order.** AQE bases coalesce/skew decisions on runtime stats from completed stages. Finishing the cheap stages first gives it real numbers before it plans the most expensive stage.
3. **Repartition the left side once.** Distributing the label table evenly on the join keys up front prevents skew from compounding across a long chain.
4. **Shuffle-parallelism configs.** 200 partitions over hundreds of GiB means ~900 MiB/partition — past the 128–256 MiB range, causing disk spill and OOM risk. Raising `shuffle.partitions` and `advisoryPartitionSizeInBytes` keeps partitions in range; the skew-join settings handle entity-key hot spots.
5. **`localCheckpoint(eager=True)`.** `fit` and `transform`/`write` are separate actions; a lazy `modeling_df` recomputes the entire chain on each. Materializing once means both read cheap data. Local checkpoint is fast (no object-store round-trip) but not fault-tolerant — on stable clusters prefer it; on preemption-prone clusters use a Delta intermediate write instead.

---

## A note on Dynamic Partition Pruning (DPP)

DPP often fires inconsistently across a wide chain — frequently on only some tables. Common reasons Catalyst can't generate it:

- The join key is **composite** (entity key + time key), not the partition column alone.
- The optimizer prefers an existing **static** range predicate on the time key.

DPP is a Catalyst decision you can't force from query code, and chasing it table-by-table has limited payoff. The semi-join pre-filter (Fix 1) addresses the same problem more directly — it removes non-matching rows regardless of whether DPP triggers — so prioritize it over trying to coax DPP onto every table.

**Inflated `sizeInBytes`:** chaining many joins makes Catalyst accumulate statistics error, sometimes producing absurd estimates (e.g. `4.14E+94 B`). This does not affect correctness or execution, but it does make the optimizer distrust adaptive decisions. It's a signal that you've built a very deep join tree — another reason to pre-filter and to materialize partway through.

---

## When this pattern applies

- A small label/cohort table (≤ tens of millions of rows) joined to several large feature tables.
- The join is **left-outer** (enrichment) — the pre-filter is semantics-safe here. For an inner join the pre-filter is unnecessary (the join already drops non-matches); for a right/full outer join it is **not** safe.
- The downstream consumer is an MLlib `Pipeline` (or any code that triggers two actions on the same lazy DataFrame).
- You can read the physical plan and see large `SortMergeJoin` right-side stages with no entity-key filter.
