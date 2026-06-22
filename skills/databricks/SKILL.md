---
name: databricks
description: >
  Use when querying or shaping large data on Databricks with Spark SQL/PySpark and Delta
  Lake (profiling, predicate pushdown, joins, window functions, EDA, pandas interop, wide
  modeling-dataset join chains), or when packaging a trained model with MLflow for
  reproducible, notebook-independent serving (signature/input_example, pyfunc, registry
  aliases, batch inference). Covers query optimization and model packaging end to end.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: ds-skills
    domain: general
    adapted-for: Databricks Runtime 13+ (Spark 3.4+, MLflow 2.x)
---

# Databricks for Data Scientists

This skill has two halves of the same job. **Part A — Querying** covers reading and
shaping large data with Spark/Delta as a read-heavy DS. **Part B — MLflow Model
Packaging** turns the model you trained on that data into a reproducible,
notebook-independent artifact. Most projects use both: query → feature-engineer →
train → package.

---

# Part A — Querying with Spark

## Overview

As a DS you are a **read-heavy user** of Spark. Your job is to write queries that are fast, correct, and reproducible — not to manage storage layout or cluster configuration. Those are data engineering concerns.

**What you can do without admin rights:**
- `DESCRIBE DETAIL / EXTENDED / HISTORY` — inspect any table you have SELECT on
- `EXPLAIN` — see the query plan before running
- `SELECT`, `WITH` (CTEs), temp views (`createOrReplaceTempView`)
- Join hints (`/*+ BROADCAST */`; `/*+ SKEW */` is Databricks-specific) — query-level, not admin
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
| Known skew on join key | Any | Skew hint (Databricks; AQE also auto-handles skew) | `/*+ SKEW('table', 'column') */` |

Spark auto-broadcasts the smaller side only below `spark.sql.autoBroadcastJoinThreshold` (default **10 MB**); above that, broadcast won't happen unless you raise the threshold or add an explicit `/*+ BROADCAST */` hint.

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

# Pattern 2: Reproduce a feature table snapshot with Delta time-travel
# TIMESTAMP AS OF returns the WHOLE table as it was WRITTEN at that timestamp (one
# snapshot for all rows) — use it to reproduce a past run, NOT as a per-row as-of join.
features_snapshot = spark.sql("""
    SELECT * FROM feature_store.customer_features
    TIMESTAMP AS OF '2024-06-01T00:00:00'
    WHERE customer_id IN (SELECT DISTINCT customer_id FROM my_cohort)
""")
# WARNING: a true point-in-time join — each label row gets the feature value as of ITS
# OWN event time — is a DIFFERENT operation (an as-of / range join on event_time, or a
# Feature Store point-in-time lookup). Time-travel alone does not do this, and using a
# single snapshot timestamp as if it were per-row as-of causes leakage. See
# references/join_strategies.md and the feature-onboarding skill for as-of joins.

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
    F.approx_percentile("amount", 0.95).alias("p95_amount"),  # sketch-based, no full sort
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
| Percentiles P50/P95/P99 | `approx_percentile(col, 0.95)` — sketch-based, much faster than exact |
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
F.approx_percentile("amount", 0.95) # approximate (sketch) — much faster, usually sufficient
```

---

### Step 7 — EDA Patterns

Common read-only EDA on large tables: null counts/rates, numeric distributions via
`approx_percentile`, categorical value frequency + cardinality, and a native correlation
matrix (`VectorAssembler` → `Correlation.corr`, no collect). Two rules carry most of the
value: use `approx_percentile` (not exact) for distributions, and compute null rates as a
single multi-column `select` rather than per-column passes.

> Full copy-paste snippets for each pattern: `references/eda_patterns.md`.

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

Arrow (`spark.sql.execution.arrow.pyspark.enabled`, on by default on Databricks) batches
the transfer, so a size-bounded `toPandas()` is already fast — no extra code needed. Going
back the other way, `spark.createDataFrame(pandas_df, schema=...)` with an explicit schema
is more reliable than letting Spark infer types.

> Arrow tuning, safety limits, and `createDataFrame` schema patterns: `references/pandas_interop.md`.

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

The recurring DS feature families on Spark: **lag/lead** (`F.lag` over a partitioned,
ordered window), **rolling aggregates** (pre-aggregate to daily, then `rowsBetween`),
**frequency/target encoding** (`groupBy().count()` then broadcast-join back),
**time features** (`dayofweek`, `datediff`, weekend flags), and **interactions/ratios**.
The non-obvious rule: always pre-aggregate before windowing on raw rows (see Step 5).

> Copy-paste patterns for every family: `references/feature_engineering.md`.

---

# Part B — MLflow Model Packaging

## Overview

Querying gets you a training set; packaging gets you a model that survives leaving
your notebook. The failure you are designing against: the model scores perfectly in
the notebook that trained it and breaks the moment someone else loads it on a cold
cluster — because it secretly depended on a variable, an in-memory fitted encoder, or
a library version that only existed in your session.

A correctly packaged model is **self-contained and reproducible**. Three principles:

1. **No hidden dependencies.** The logged model must not reference notebook globals,
   widgets, `spark` from the outer scope, or relative-path imports (`from utils import ...`).
   If `models:/...` is loaded in a fresh Python process with nothing else defined,
   it must still predict.
2. **Log complete artifacts.** Always log the model **plus** an `input_example`, the
   environment (`conda_env` or `pip_requirements`), and metadata (metrics, params,
   signature). The `input_example` lets MLflow infer and enforce the schema.
3. **Preprocessing travels with the model.** Never log a bare estimator and keep the
   fitted scaler/encoder "in the notebook." Wrap preprocessing + estimator in one
   `Pipeline` (or a `pyfunc` wrapper) so the exact transforms that fit the model also
   serve it. A separate preprocessing step is the #1 source of train/serve skew.

## Pattern 1 — sklearn / LightGBM Pipeline

The common case: a scikit-learn `Pipeline` (which can wrap a `LGBMClassifier`). Log it
with `mlflow.sklearn.log_model`, an `input_example`, and an inferred signature.

```python
import mlflow
from mlflow.models import infer_signature
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from lightgbm import LGBMClassifier

# Preprocessing is INSIDE the pipeline — it gets logged with the model.
pre = ColumnTransformer([("num", StandardScaler(), num_cols)], remainder="passthrough")
pipe = Pipeline([("pre", pre), ("model", LGBMClassifier(n_estimators=300))])
pipe.fit(X_train, y_train)

# input_example drives schema inference + enforcement at load time.
input_example = X_train.head(5)
signature = infer_signature(X_train, pipe.predict_proba(X_train)[:, 1])

with mlflow.start_run() as run:
    mlflow.log_params({"n_estimators": 300})
    mlflow.log_metric("auc_val", auc_val)
    mlflow.sklearn.log_model(
        sk_model=pipe,
        artifact_path="model",
        input_example=input_example,
        signature=signature,
        pip_requirements=[                  # pin versions — see reproducibility checklist
            f"lightgbm=={lightgbm.__version__}",
            f"scikit-learn=={sklearn.__version__}",
        ],
    )
    model_uri = f"runs:/{run.info.run_id}/model"
```

## Pattern 2 — custom model with external artifacts (`pyfunc`)

When the model is not a single sklearn estimator — custom logic, a lookup table, an
embedding file, multiple objects — subclass `mlflow.pyfunc.PythonModel`. External
files are passed through `artifacts` and re-loaded in `load_context`, never read from a
notebook path at predict time.

```python
import mlflow.pyfunc

class ScorerModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        import joblib, json
        self.model = joblib.load(context.artifacts["model_file"])
        with open(context.artifacts["thresholds"]) as f:
            self.thresholds = json.load(f)

    def predict(self, context, model_input):
        proba = self.model.predict_proba(model_input)[:, 1]
        return (proba >= self.thresholds["cutoff"]).astype(int)

with mlflow.start_run() as run:
    mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model=ScorerModel(),
        artifacts={                          # files copied into the model — no notebook paths
            "model_file": "/dbfs/tmp/model.joblib",
            "thresholds": "/dbfs/tmp/thresholds.json",
        },
        input_example=input_example,
        pip_requirements=["scikit-learn==1.4.2", "joblib==1.4.0"],
    )
```

## Pattern 3 — Model Registry: register → promote by alias

Promote by a stable pointer so consumers load the model without hard-coding a run id.
On Unity Catalog-backed MLflow (the Databricks default), models use **three-level names**
(`catalog.schema.model`) and **aliases** (e.g. `@champion`). Model "stages" are not
available in UC, and `transition_model_version_stage` is deprecated in MLflow 2.9+.

```python
import mlflow
from mlflow import MlflowClient

mlflow.set_registry_uri("databricks-uc")          # Unity Catalog registry
result = mlflow.register_model(model_uri, "main.credit.default_scorer")

client = MlflowClient()
# Promote by alias after validation passes — no stages, no run id.
client.set_registered_model_alias(
    name="main.credit.default_scorer", alias="champion", version=result.version)

# Consumers load by alias — decoupled from the training notebook.
model = mlflow.pyfunc.load_model("models:/main.credit.default_scorer@champion")
```

> **Legacy (pre-UC workspace registry):** older setups promoted with
> `client.transition_model_version_stage(..., stage="Production")` and loaded
> `models:/name/Production`. Stages are deprecated in MLflow 2.9+; use aliases.

## Pattern 4 — batch inference as a Job (not notebook commands)

Score in a **Databricks Job** that loads the registered model and writes a Delta table.
Use `mlflow.pyfunc.spark_udf` so inference runs distributed across the cluster, and
make the job idempotent (deterministic input window, overwrite/merge by key). Do not
leave scoring as interactive notebook cells that depend on session state.

```python
import mlflow

# Runs as a scheduled Job task, not an interactive cell.
predict_udf = mlflow.pyfunc.spark_udf(
    spark, model_uri="models:/main.credit.default_scorer@champion", result_type="double")

scoring_df = spark.table("features.credit_scoring_daily").where("as_of_date = '2026-06-20'")
scored = scoring_df.withColumn("score", predict_udf(*scoring_df.columns))
(scored.write.mode("overwrite")
       .option("replaceWhere", "as_of_date = '2026-06-20'")
       .saveAsTable("scores.credit_default_daily"))
```

## Reproducibility Checklist

Before you register a model, confirm:

- **Pinned versions** — `pip_requirements`/`conda_env` lists exact versions of every
  library the model needs (`==`, not `>=`). The cold cluster will not have your session.
- **Schema enforcement** — an `input_example` + `signature` are logged so MLflow rejects
  mismatched input columns/types at serve time instead of silently mis-scoring.
- **No global notebook state** — the model does not read `spark`, widgets, `dbutils`,
  notebook globals, or relative imports. Test by loading it in a fresh kernel.
- **Preprocessing is inside the artifact** — the fitted scaler/encoder/imputer is part
  of the logged `Pipeline` or `pyfunc`, not a separate notebook step.
- **External files passed as `artifacts`** — lookup tables, thresholds, embeddings are
  logged with the model, not read from `/dbfs/tmp` paths at predict time.
- **Loaded by alias** — consumers use `models:/catalog.schema.model@champion` (UC; or a
  legacy stage `models:/name/Production` on pre-UC registries), never `runs:/<id>/...`.

---

# Quality Standards

## Querying (Part A)

- **Profile before writing**: Run `DESCRIBE DETAIL` and `df.printSchema()` before the first query.
- **Sample before scale**: Develop on `.sample(0.01)` or `.limit(10_000)`. Run on full data once logic is correct.
- **Filter first**: Apply date range and status filters BEFORE joining to large tables.
- **Never SELECT \***: Select only the columns you need — unnecessary columns cross the network.
- **No functions on filter columns**: `YEAR(date)` breaks predicate pushdown. Use `date >= '...'` ranges.
- **Every window has PARTITION BY**: Never run a window function without partitioning on tables >1M rows.
- **Pre-aggregate before windowing**: Window on daily aggregates (365 rows/customer), not 100M raw rows.
- **approx_percentile over percentile**: Sketch-based; sufficient for EDA and feature engineering, and avoids a full sort.
- **No Python UDFs on large tables**: Use built-in functions or `@pandas_udf`. Row-by-row Python is 10–50x slower.
- **Limit before toPandas()**: Always `.filter()` + `.limit()` + `.select()` before pulling to Pandas.
- **Unpersist after use**: `.cache()` holds memory cluster-wide. Release with `.unpersist()` when done.
- **Fixed date ranges**: Use explicit dates (`>= '2024-01-01'`), not `CURRENT_DATE - 30`. Required for reproducibility.
- **Read the plan**: Run `df.explain()` before submitting expensive queries. Fix cartesian products and missing pushdowns first.
- **Pre-filter big right-side tables**: Before joining a small label/cohort to a large feature table, `leftsemi`-broadcast the cohort keys to drop non-matching feature rows ahead of the shuffle. Safe for left-outer joins (unmatched labels still get nulls).
- **Materialize before MLlib**: `localCheckpoint(eager=True)` a multi-join `modeling_df` before `pipeline.fit()` so the chain isn't recomputed by the later `transform().write()`.
- **Size shuffle.partitions to the data**: On hundreds of GiB of shuffle, raise `spark.sql.shuffle.partitions` so each partition lands in the 128–256 MiB range — the default 200 spills and risks OOM.
- **Flag admin issues to DE**: If a query is slow because the table needs OPTIMIZE or ANALYZE TABLE, note it and ask the data engineer — do not attempt admin operations.

## Packaging (Part B)

- **Log preprocessing with the model**: Wrap transforms + estimator in one `Pipeline`/`pyfunc`. Never keep a fitted encoder "in the notebook."
- **Always log an `input_example` + signature**: This gives schema enforcement at serve time and prevents silent mis-scoring on wrong columns.
- **Pin every dependency**: `pip_requirements` with `==`, not `>=`. The cold cluster does not have your session's library versions.
- **No notebook globals in the model**: No `spark`, `dbutils`, widgets, or relative imports inside the logged model. Verify by loading in a fresh kernel.
- **External files go in `artifacts`**: Lookup tables, thresholds, embeddings travel with the model — not read from `/dbfs/tmp` at predict time.
- **Consumers load by alias**: `models:/catalog.schema.model@champion` on UC (or a legacy `models:/name/Production` stage pre-UC), never `runs:/<id>/...` — decouple serving from the training run.
- **Batch inference is a Job, not cells**: Score with `mlflow.pyfunc.spark_udf` in a scheduled, idempotent Databricks Job over a fixed input window.

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
- MLflow Model Registry: https://mlflow.org/docs/latest/model-registry.html
- MLflow Models (signatures, input_example, pyfunc): https://mlflow.org/docs/latest/models.html
- Databricks MLflow batch inference (spark_udf): https://docs.databricks.com/aws/en/machine-learning/model-inference/
