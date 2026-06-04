---
name: spark-query-optimization
description: Query and analyze data with Spark SQL and PySpark as a Data Scientist on Databricks. Use when exploring Delta Lake tables, building feature engineering pipelines, or preparing data for ML. Covers read-only profiling, predicate pushdown, join hints, semi-join pre-filtering, wide multi-table join chains for modeling datasets, MLlib double-execution avoidance, window aggregations, EDA patterns, sampling, and Pandas interoperability. Assumes no admin rights — does NOT cover OPTIMIZE, VACUUM, ALTER TABLE, or ANALYZE TABLE.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: ds-skills
    domain: general (with optional banking examples)
    adapted-for: Databricks Runtime 13+ (Spark 3.4+, Delta Lake, AQE enabled by default)
---

# Spark Querying for Data Scientists

## Overview

As a DS you are a **read-heavy user** of Spark. Your job is to write queries that are fast, correct, and reproducible — not to manage storage layout or cluster configuration. Those are data engineering concerns.

**What you can do without admin rights:**
- `DESCRIBE DETAIL / EXTENDED / HISTORY` — inspect any table you have SELECT on
- `EXPLAIN` — see the query plan before running
- `SELECT`, `WITH` (CTEs), temp views (`createOrReplaceTempView`)
- Join hints (`/*+ BROADCAST */`, `/*+ SKEW */`) — these are query-level, not admin
- `.cache()` / `.persist()` — memory management within your session
- Write to your own dev/scratch schema (if granted)
- Read from Delta, Parquet, CSV, JSON, JDBC

**What you cannot do (needs data engineer):**
- `OPTIMIZE`, `VACUUM`, `ZORDER` — require write access on the table
- `ANALYZE TABLE ... COMPUTE STATISTICS` — requires write access
- `ALTER TABLE ... CLUSTER BY` — requires ALTER privilege
- `CREATE TABLE` in production schemas — requires CREATE privilege

If a query is slow due to missing compaction or stale statistics, **note it and flag to your DE team** — do not try to fix it yourself.

---

## When to Use This Skill

- Exploring a new Delta table you've never touched before
- Writing a query against a large table (>10M rows) that needs to be fast
- Building feature engineering or ML preprocessing pipelines
- Doing EDA (distributions, null analysis, correlation) on large data
- Preparing training data: filtering, joining, aggregating, windowing
- Pulling data to Pandas for modeling (need to stay under memory limit)
- Debugging a slow query you own

---

## Workflow

### Step 1 — Profile the Table (Read-Only)

Never write a query against a table you haven't profiled. Two minutes of profiling saves two hours of debugging. All commands below are read-only.

```sql
-- What's in this table: partitioning, clustering keys, file count, size
DESCRIBE DETAIL schema.table_name;

-- Column data types and basic metadata
DESCRIBE EXTENDED schema.table_name;

-- What changed recently: merge operations, schema changes, writes
DESCRIBE HISTORY schema.table_name LIMIT 10;
```

**In PySpark (useful in notebooks):**

```python
# Schema + types
df = spark.table("schema.table_name")
df.printSchema()

# Quick stats: count, mean, stddev, min, max, quartiles
df.describe().show()        # string + numeric
df.summary().show()         # more percentiles (25%, 50%, 75%)

# Row count — cache first if you'll reuse the df
df.count()
```

**Key questions to answer before writing the query:**

```
[ ] How many rows? How many GB? (DESCRIBE DETAIL → sizeInBytes)
[ ] Partitioned by what? (partitionColumns in DESCRIBE DETAIL)
[ ] Liquid Clustering keys? (clusteringColumns in DESCRIBE DETAIL)
[ ] What column(s) does every query filter on? → use those for WHERE clauses
[ ] Is there a known skew? (one key value with 100x more rows than others)
[ ] Do I need all columns? → SELECT only what you need, never SELECT *
```

---

### Step 2 — Sample Before You Scale

When exploring an unknown table, always work on a sample first. Iterate fast, then run on full data once the logic is correct.

```python
# Fraction-based sample (approximate row count)
sample = df.sample(fraction=0.01, seed=42)   # ~1% of rows

# Limit-based (exact row count, takes first N partitions — fast but biased)
sample = df.limit(10_000)

# Stratified sample — preserve class distribution (critical for ML data prep)
fractions = {"class_A": 0.1, "class_B": 0.1, "class_C": 0.1}
sample = df.sampleBy("label_column", fractions=fractions, seed=42)

# Check schema + first rows without triggering full scan
df.show(5, truncate=False)
df.printSchema()
```

**Sampling rules:**
- Use `.sample()` for EDA — it distributes across all partitions
- Use `.limit()` only for quick schema checks — it reads the first partitions only
- Use `.sampleBy()` when building train/test splits or checking class balance
- Always set `seed` for reproducibility (required for ML pipelines)

---

### Step 3 — Write the Query: Filters First

The single highest-impact rule: **filter before joining, and filter on raw columns**.

**Predicate pushdown rules:**

```sql
-- Rule 1: Filter on raw column, not a derived expression
-- BAD: function wrapping prevents pushdown to Delta file statistics
WHERE YEAR(transaction_date) = 2025

-- GOOD: range filter pushes down to Delta file skipping
WHERE transaction_date >= '2025-01-01' AND transaction_date < '2026-01-01'

-- Rule 2: Most selective filter first
-- BAD: low-selectivity filter first (transaction_type has 3 values)
WHERE transaction_type = 'DEBIT' AND customer_id = 12345

-- GOOD: customer_id eliminates 99.999% of rows
WHERE customer_id = 12345 AND transaction_type = 'DEBIT'

-- Rule 3: Filter before joining, not after
-- BAD: full join then filter
SELECT * FROM transactions t JOIN customers c ON t.customer_id = c.id
WHERE t.transaction_date >= '2025-01-01'

-- GOOD: filter inside CTE before join
WITH recent AS (
    SELECT * FROM transactions
    WHERE transaction_date >= '2025-01-01'
      AND status != 'VOIDED'
)
SELECT r.*, c.segment FROM recent r
JOIN customers c ON r.customer_id = c.customer_id
```

**Filter checklist:**

```
[ ] Date range applied? (most important — skips whole files in Delta)
[ ] Status filter applied? (exclude nulls, cancelled, test records)
[ ] Only needed columns selected? (SELECT col1, col2 not SELECT *)
[ ] No function wrapping filter columns? (CAST, YEAR, MONTH, UPPER all break pushdown)
[ ] Large table filtered inside a CTE before the join?
```

---

### Step 4 — Choose Join Strategy

DS write a lot of joins: transactions to customer features, events to reference tables, etc. Wrong join strategy is the most common cause of slow queries.

**Decision by table sizes:**

| Left table | Right table | Strategy | How |
|---|---|---|---|
| Any size | < 30 MB | Broadcast | `/*+ BROADCAST(small_table) */` |
| Any size | 30 MB–2 GB | Broadcast (explicit) | Increase threshold or add hint |
| Both large, same partitioning | Both large | Sort-merge (AQE handles) | No hint needed |
| Known skew on join key | Any | Skew hint | `/*+ SKEW('table', 'column') */` |

**In PySpark:**

```python
from pyspark.sql.functions import broadcast

# Small reference table (product codes, country mappings, segment labels)
result = large_df.join(broadcast(small_df), on="join_key", how="left")

# Explicit SQL hint
spark.sql("""
    SELECT /*+ BROADCAST(ref) */ t.*, ref.label
    FROM transactions t
    LEFT JOIN reference_table ref ON t.code = ref.code
""")
```

**Common DS join patterns:**

```python
# Pattern 1: Enrich transactions with customer attributes
result = (
    transactions
    .filter("transaction_date >= '2024-01-01'")   # filter first
    .join(broadcast(customer_segments), on="customer_id", how="left")
)

# Pattern 2: Point-in-time join (feature values as-of a past date)
# Use AS OF syntax on Delta tables — reads the table at a historical timestamp
features_at_t = spark.sql("""
    SELECT * FROM feature_store.customer_features
    TIMESTAMP AS OF '2024-06-01T00:00:00'
    WHERE customer_id IN (SELECT DISTINCT customer_id FROM my_cohort)
""")

# Pattern 3: Self-join for computing lag/lead manually
from pyspark.sql import functions as F
from pyspark.sql.window import Window

w = Window.partitionBy("customer_id").orderBy("transaction_date")
df = df.withColumn("prev_amount", F.lag("amount", 1).over(w))
```

---

### Step 5 — Aggregations & Window Functions

**Aggregation — always use DataFrame API or Spark SQL:**

```python
# Fast: groupBy + agg with built-in functions
from pyspark.sql import functions as F

result = df.groupBy("customer_id", "month").agg(
    F.sum("amount").alias("total_amount"),
    F.count("*").alias("txn_count"),
    F.approx_percentile("amount", 0.95).alias("p95_amount"),  # 10x faster than percentile
    F.countDistinct("merchant_id").alias("unique_merchants"),
    F.max("transaction_date").alias("last_txn_date")
)
```

**Window functions — always PARTITION BY:**

```python
from pyspark.sql.window import Window
from pyspark.sql import functions as F

# Rolling 30-day sum — pre-aggregate to daily first on large tables
daily = df.groupBy("customer_id", "transaction_date").agg(
    F.sum("amount").alias("daily_total")
)

w_rolling = (Window
    .partitionBy("customer_id")
    .orderBy("transaction_date")
    .rowsBetween(-29, 0))   # ROWS BETWEEN is faster than RANGE BETWEEN

result = daily.withColumn("rolling_30d", F.sum("daily_total").over(w_rolling))
```

**Window function checklist:**

```
[ ] Every window has PARTITION BY? (global window = all data on one executor)
[ ] Using ROWS BETWEEN instead of RANGE BETWEEN where possible?
[ ] Pre-aggregated to daily/weekly BEFORE windowing on raw rows?
[ ] Avoided .groupByKey() in RDD API? (use groupBy().agg() instead)
```

---

### Step 6 — UDF Hierarchy (DS-Specific)

The most impactful DS-specific optimization. Python UDFs serialize every row — avoid them on large tables.

**Priority (fastest → slowest):**

```
1. Built-in SQL / DataFrame functions   → Catalyst-optimized, JVM-native, zero Python overhead
2. @pandas_udf (vectorized UDF)         → Arrow batch transfer, ~10x faster than Python UDF
3. Python UDF (@udf)                    → Last resort only
```

**When to use each:**

| Need | Use |
|---|---|
| String ops, date math, math | `regexp_replace`, `date_diff`, `round`, `abs` — built-in |
| Percentiles P50/P95/P99 | `approx_percentile(col, 0.95)` — built-in, 10x faster than exact |
| Custom feature transform (vectorizable) | `@pandas_udf` with Arrow — receives pandas Series |
| Stateful logic per row with external library | Python `@udf` — last resort |

**Pandas UDF pattern:**

```python
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import DoubleType
import pandas as pd

@pandas_udf(DoubleType())
def custom_feature(amount: pd.Series, days_since: pd.Series) -> pd.Series:
    # Entire partition arrives as pandas Series — use vectorized ops
    return (amount / (days_since.clip(lower=1))).clip(upper=1000.0)

df = df.withColumn("feature_x", custom_feature("amount", "days_since_last"))
```

**Anti-patterns to avoid:**

```python
# BAD: Python UDF on 100M-row table — serializes every row to Python
@udf("double")
def slow_score(amount, days):
    return float(amount) / (float(days) + 1)

# BAD: collect() inside a loop — pulls ALL data to driver
for customer_id in df.select("customer_id").distinct().collect():  # NEVER
    ...

# BAD: toPandas() on large table — crashes driver
df.toPandas()   # only safe after .limit() or .filter() down to manageable size

# BAD: exact percentile on 100M rows
F.percentile("amount", 0.95)        # exact — very slow
F.approx_percentile("amount", 0.95) # approximate — 10x faster, usually sufficient
```

---

### Step 7 — EDA Patterns

Common DS exploratory patterns on large tables. All read-only.

**Null analysis:**

```python
from pyspark.sql import functions as F

null_counts = df.select([
    F.count(F.when(F.col(c).isNull(), c)).alias(c)
    for c in df.columns
])
null_counts.show()

# Null rate as percentage
total = df.count()
null_rates = df.select([
    (F.count(F.when(F.col(c).isNull(), c)) / total * 100).alias(f"{c}_null_pct")
    for c in df.columns
])
null_rates.show()
```

**Distribution check (numeric columns):**

```python
# Fast percentile scan — use approx for large tables
numeric_cols = [f.name for f in df.schema.fields if str(f.dataType) in
                ("DoubleType", "FloatType", "LongType", "IntegerType")]

df.select([
    F.approx_percentile(c, [0.01, 0.25, 0.50, 0.75, 0.99]).alias(c)
    for c in numeric_cols
]).show()
```

**Value frequency (categorical columns):**

```python
# Top 20 values for a categorical column
df.groupBy("category_col").count().orderBy("count", ascending=False).show(20)

# Cardinality check across all string columns
string_cols = [f.name for f in df.schema.fields if str(f.dataType) == "StringType"]
df.select([F.countDistinct(c).alias(c) for c in string_cols]).show()
```

**Correlation matrix (numeric, DS-specific):**

```python
# PySpark native — works on Spark DataFrames without collecting
from pyspark.ml.stat import Correlation
from pyspark.ml.feature import VectorAssembler

assembler = VectorAssembler(inputCols=numeric_cols, outputCol="features")
vector_df = assembler.transform(df.select(numeric_cols).dropna())
corr_matrix = Correlation.corr(vector_df, "features").head()[0]
```

---

### Step 8 — Pandas Interoperability

Bringing data to Pandas for modeling or visualization. The key constraint: **Pandas runs on the driver — never pull more than fits in driver memory**.

```python
# Rule: Always limit/aggregate BEFORE toPandas()
# BAD: crashes driver on large tables
pandas_df = spark_df.toPandas()

# GOOD: filter down first
pandas_df = (spark_df
    .filter("customer_segment = 'HIGH_VALUE'")
    .filter("transaction_date >= '2024-01-01'")
    .select("customer_id", "feature_1", "feature_2", "label")
    .limit(500_000)   # explicit limit as safety
    .toPandas())

# GOOD: aggregate to small result, then pull
agg_df = (spark_df
    .groupBy("month", "product_type")
    .agg(F.avg("amount").alias("avg_amount"), F.count("*").alias("cnt"))
    .toPandas())
```

**Arrow optimization (enabled by default on Databricks):**

```python
# Verify Arrow is enabled — should already be true on Databricks
spark.conf.get("spark.sql.execution.arrow.pyspark.enabled")  # "true"

# For large toPandas() calls — Arrow batches transfer (10x faster than row-by-row)
# No extra code needed if Arrow is enabled
```

**Going back Spark → Pandas → Spark:**

```python
# Create Spark DataFrame from Pandas (for result upload or further processing)
result_spark = spark.createDataFrame(pandas_df)

# With explicit schema (more reliable)
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
schema = StructType([
    StructField("customer_id", StringType()),
    StructField("score", DoubleType()),
])
result_spark = spark.createDataFrame(pandas_df, schema=schema)
```

---

### Step 9 — Caching Strategy

Cache when you'll reuse the same DataFrame multiple times in one session.

**When to cache:**

```python
# Cache a filtered/joined base DataFrame used across multiple analyses
base = (spark.table("schema.transactions")
    .filter("transaction_date >= '2024-01-01'")
    .filter("status = 'SETTLED'")
    .join(broadcast(segments), on="customer_id", how="left")
    .cache())

# Force materialization (cache is lazy — triggered on first action)
base.count()

# Use it multiple times without recomputing
feature_1 = base.groupBy("customer_id").agg(...)
feature_2 = base.groupBy("customer_id", "merchant_category").agg(...)

# Always unpersist when done — free up cluster memory for others
base.unpersist()
```

**Cache level choice:**

| Data size | Use |
|---|---|
| Fits in executor memory | `.cache()` (MEMORY_AND_DISK — safe default) |
| Larger, accessed repeatedly | `.persist(StorageLevel.DISK_ONLY)` |
| Small, accessed very often | `.persist(StorageLevel.MEMORY_ONLY)` |

**Do not cache:**
- Tables you only read once
- Results of `.count()`, `.show()` — these are actions, not DataFrames
- Very large tables — cache eviction causes recomputation anyway

---

### Step 10 — Check the Plan, Then Validate

**Before running an expensive query, read the plan:**

```python
# Concise: shows Physical Plan only
df.explain()

# Verbose: Parsed → Analyzed → Optimized → Physical
df.explain(mode="extended")

# With cost estimates (useful to spot missing statistics)
df.explain(mode="cost")
```

**What to look for:**

```
GOOD signals:
  PushedFilters: [...] inside FileScan       → predicate pushed down
  BroadcastHashJoin                          → small table was broadcast
  AQE: isRuntime=true on statistics          → AQE active

BAD signals:
  No PushedFilters                           → add filter on partition/cluster column
  SortMergeJoin on known-small table         → add /*+ BROADCAST */ hint
  rowCount=N/A in cost plan                  → statistics missing (flag to DE team)
  CartesianProduct                           → missing join condition — fix immediately
```

**While query is running (in a new cell):**

```python
# Check active jobs and stage progress without cancelling the query
tracker = spark.sparkContext.statusTracker()

for job_id in tracker.getActiveJobIds():
    job = tracker.getJobInfo(job_id)
    print(f"Job {job_id}:")
    for sid in job.stageIds():
        s = tracker.getStageInfo(sid)
        if s:
            print(f"  Stage {sid}: active={s.numActiveTasks()} "
                  f"done={s.numCompletedTasks()} failed={s.numFailedTasks()}")

# Link to Spark UI SQL tab
displayHTML(f'<a href="{spark.sparkContext.uiWebUrl}/SQL/" target="_blank">'
            f'Spark UI →</a>')
```

**Kill vs wait decision:**

```
Kill if:
  - shuffle_write >> input size (10x+) → cartesian join or missing filter
  - Stage restarted > 3 times → executor instability, fix before retrying
  - You see a structural mistake (missing join key, wrong table)

Wait if:
  - 1-3 tasks remaining out of hundreds → tail tasks / mild skew, usually finishes
  - spill_disk is small (<1GB) and tasks progress → will complete, optimize next run
```

---

## Building Wide Modeling Datasets (Join Chains + MLlib)

The hardest DS query is not a single join — it's the **modeling dataset**: a label table left-joined to 10+ feature tables, then fed into an MLlib `Pipeline`. A 30M-row label table joined to a dozen large feature tables can shuffle hundreds of GiB and run for hours. Every fix below is query-level or session-level — no admin rights.

**Symptom:** the final `fit` + `transform` + `write` cell runs far longer than expected. Read the physical plan from Spark UI (it can be 100+ nodes) and check, per feature table:

```
[ ] SortMergeJoin or BroadcastHashJoin? (right side shuffling fully = SMJ)
[ ] How many rows / GiB shuffled on the right side? (ShuffleQueryStage size)
[ ] Is there a filter on the ENTITY key, or only on the time key?
[ ] Dynamic Partition Pruning active? (dynamicpruningexpression in the scan)
[ ] sizeInBytes wildly inflated (e.g. 4E+94 B)? → Catalyst stats error across the chain
```

The dominant cost is almost always **right-side over-shuffle**: each feature table shuffles all rows in its time range, even though most entities never appear in the 30M-row label set and get discarded after the join.

### Fix 1 (biggest impact) — Semi-join pre-filter on the entity key

Drop rows that can never match **before** the expensive shuffle, using a broadcast `leftsemi` join against the distinct label entities.

```python
from pyspark.sql.functions import broadcast

# Distinct entity keys from the label table — small, broadcastable
label_entities = label_df.select("entity_key").distinct()

# Pre-filter EVERY feature table before the main left-outer join
for name, feat in feature_tables.items():
    feature_tables[name] = feat.join(broadcast(label_entities), on="entity_key", how="leftsemi")

# Then build modeling_df with the normal left-outer joins
```

**Semantics are preserved exactly.** The outer join still emits nulls for label entities missing from a feature table; the pre-filter only removes feature rows whose entity is absent from the label — those would have been discarded anyway. Works for Feature Store tables and Delta-path tables alike.

### Fix 2 — Reorder joins smallest → largest

Join the smallest feature table first and the largest last. AQE collects real runtime statistics from the early, cheap stages and uses them to make better adaptive decisions (coalesce, skew handling) on the biggest stage — instead of guessing with no stats when the largest table is joined early.

### Fix 3 — Repartition the left side once, up front

```python
# Distribute the label table evenly on the join keys before the chain begins
modeling_df = label_df.repartition(2000, "entity_key", "time_key")
```

This avoids skew accumulating across a long chain of joins.

### Fix 4 — Tune shuffle parallelism for the total shuffle volume (session-level)

Default `shuffle.partitions=200` over hundreds of GiB gives ~900 MiB/partition — well past the 128–256 MiB sweet spot, causing spill and OOM risk.

```python
spark.conf.set("spark.sql.shuffle.partitions", 2000)                 # target ~200 MiB/partition
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", 256 * 1024 * 1024)
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", True)
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", 3)  # more sensitive to moderate skew
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 100 * 1024 * 1024)  # broadcast the entity-key list
# Only if you have write access on the output table / your own schema:
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", True)   # or .option("delta.optimizeWrite","true") on write
```

### Fix 5 — Checkpoint before `fit()` to stop double execution

A lazy `modeling_df` fed into a Pipeline is recomputed **twice** — once for `pipeline.fit(df)` and again for `pipeline.transform(df).write(...)`. The whole join chain runs twice with no materialization in between.

```python
# Materialize the join chain ONCE before MLlib touches it
modeling_df = modeling_df.localCheckpoint(eager=True)

model = pipeline.fit(modeling_df)                  # reads from checkpoint
model.transform(modeling_df).write.format("delta")...  # also reads from checkpoint — chain runs once
```

`localCheckpoint(eager=True)` writes to executor-local disk: faster than a Delta intermediate write (no object-store round-trip) but **not fault-tolerant** — an executor loss forces recompute from scratch. Prefer it on stable clusters with low preemption; use a Delta intermediate write if the cluster is volatile.

> Full worked example, before/after physical-plan structure, and the DPP-inconsistency discussion are in `references/join_chain_optimization.md`.

---

## Feature Engineering Quick Reference

```python
# Lag features
w = Window.partitionBy("customer_id").orderBy("transaction_date")
df = df.withColumn("amount_lag_1", F.lag("amount", 1).over(w))
df = df.withColumn("amount_lag_7", F.lag("amount", 7).over(w))

# Rolling aggregations (pre-aggregate first)
daily = df.groupBy("customer_id", "date").agg(F.sum("amount").alias("daily"))
w_roll = Window.partitionBy("customer_id").orderBy("date").rowsBetween(-29, 0)
daily = daily.withColumn("rolling_30d_sum", F.sum("daily").over(w_roll))
daily = daily.withColumn("rolling_30d_mean", F.avg("daily").over(w_roll))

# Categorical encoding — frequency encoding
freq = df.groupBy("merchant_category").count().withColumnRenamed("count", "cat_freq")
df = df.join(broadcast(freq), on="merchant_category", how="left")

# Time-based features
df = df.withColumn("day_of_week", F.dayofweek("transaction_date"))
df = df.withColumn("is_weekend", (F.dayofweek("transaction_date").isin([1, 7])).cast("int"))
df = df.withColumn("days_since_last",
    F.datediff(F.col("transaction_date"), F.lag("transaction_date", 1).over(w)))

# Interaction features
df = df.withColumn("amount_per_day", F.col("total_amount") / F.col("active_days").cast("double"))
```

---

## Quality Standards

- **Profile before writing**: Run `DESCRIBE DETAIL` and `df.printSchema()` before the first query.
- **Sample before scale**: Develop on `.sample(0.01)` or `.limit(10_000)`. Run on full data once logic is correct.
- **Filter first**: Apply date range and status filters BEFORE joining to large tables.
- **Never SELECT \***: Select only the columns you need — unnecessary columns cross the network.
- **No functions on filter columns**: `YEAR(date)` breaks predicate pushdown. Use `date >= '...'` ranges.
- **Every window has PARTITION BY**: Never run a window function without partitioning on tables >1M rows.
- **Pre-aggregate before windowing**: Window on daily aggregates (365 rows/customer), not 100M raw rows.
- **approx_percentile over percentile**: Approximate is sufficient for EDA and feature engineering. 10x faster.
- **No Python UDFs on large tables**: Use built-in functions or `@pandas_udf`. Row-by-row Python is 10–50x slower.
- **Limit before toPandas()**: Always `.filter()` + `.limit()` + `.select()` before pulling to Pandas.
- **Unpersist after use**: `.cache()` holds memory cluster-wide. Release with `.unpersist()` when done.
- **Fixed date ranges**: Use explicit dates (`>= '2024-01-01'`), not `CURRENT_DATE - 30`. Required for reproducibility.
- **Read the plan**: Run `df.explain()` before submitting expensive queries. Fix cartesian products and missing pushdowns first.
- **Pre-filter big right-side tables**: Before joining a small label/cohort to a large feature table, `leftsemi`-broadcast the cohort keys to drop non-matching feature rows ahead of the shuffle. Safe for left-outer joins (unmatched labels still get nulls).
- **Materialize before MLlib**: `localCheckpoint(eager=True)` a multi-join `modeling_df` before `pipeline.fit()` so the chain isn't recomputed by the later `transform().write()`.
- **Size shuffle.partitions to the data**: On hundreds of GiB of shuffle, raise `spark.sql.shuffle.partitions` so each partition lands in the 128–256 MiB range — the default 200 spills and risks OOM.
- **Flag admin issues to DE**: If a query is slow because the table needs OPTIMIZE or ANALYZE TABLE, note it and ask the data engineer — do not attempt admin operations.

---

## Resources

### references/
- `references/eda_patterns.md` — Full EDA checklist: null analysis, distributions, outliers, cardinality, correlation
- `references/feature_engineering.md` — Feature engineering patterns: lag, rolling, encoding, interaction, time features
- `references/join_strategies.md` — Join decision tree: broadcast, skew hints, point-in-time, self-join, semi-join pre-filter
- `references/join_chain_optimization.md` — Wide modeling-dataset join chains: semi-join pre-filter, join reordering, shuffle tuning, MLlib double-execution & localCheckpoint, DPP notes
- `references/window_aggregation_patterns.md` — Window patterns: running total, bounded rolling, rank, dense_rank, lead/lag
- `references/anti_patterns.md` — Top DS anti-patterns: collect(), toPandas(), Python UDFs, missing filters, SELECT *
- `references/pandas_interop.md` — Pandas/Spark interoperability: Arrow, toPandas safety limits, createDataFrame

### Sources
- Apache Spark DataFrame API: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/dataframe.html
- PySpark SQL Functions: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions/index.html
- PySpark Window Functions: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.Window.html
- Databricks AQE: https://docs.databricks.com/aws/en/optimizations/aqe
- Delta Lake Time Travel: https://docs.delta.io/latest/delta-batch.html#query-an-older-snapshot-of-a-table-time-travel
- Databricks Pandas API on Spark: https://docs.databricks.com/aws/en/languages/pandas-api-on-spark
