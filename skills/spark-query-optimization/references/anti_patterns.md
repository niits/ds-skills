# DS Anti-Patterns in PySpark

The most common mistakes Data Scientists make when writing PySpark. Each entry has: what it looks like, why it's bad, and the fix.

---

## 1. `collect()` in a Loop

```python
# BAD: pulls ALL distinct values to driver, then loops over them
for cid in df.select("customer_id").distinct().collect():
    process(cid)   # runs one Spark job per customer_id — catastrophic

# GOOD: do the work in Spark, not Python
result = df.groupBy("customer_id").agg(
    F.sum("amount").alias("total"),
    F.count("*").alias("cnt")
)
```

**Why it's bad:** `.collect()` serializes the entire result to the driver. If there are 1M customer IDs, you're creating 1M Spark jobs.

---

## 2. `toPandas()` Without Filtering

```python
# BAD: crashes driver on any table > a few GB
pandas_df = spark_df.toPandas()

# GOOD: filter + select + limit BEFORE pulling
pandas_df = (spark_df
    .filter("event_date >= '2024-01-01'")
    .select("customer_id", "feature_1", "feature_2", "label")
    .limit(200_000)
    .toPandas())
```

**Why it's bad:** Driver memory is typically 8–32GB. A 100M-row table is usually 5–50GB. The job OOMs or kills the cluster for everyone.

---

## 3. Python UDF on Large Tables

```python
# BAD: serializes every row to Python interpreter — 10–50x slower
@udf("double")
def compute_score(amount, days):
    return float(amount) / max(float(days), 1)

df = df.withColumn("score", compute_score("amount", "days_since"))

# GOOD: built-in SQL function — zero Python overhead
df = df.withColumn("score", F.col("amount") / F.greatest(F.col("days_since"), F.lit(1)).cast("double"))

# GOOD: Pandas UDF if custom logic needed — Arrow batch transfer
@pandas_udf("double")
def compute_score_vec(amount: pd.Series, days: pd.Series) -> pd.Series:
    return amount / days.clip(lower=1)
```

---

## 4. `SELECT *` on Wide Tables

```python
# BAD: reads all columns across network, including unused ones
df = spark.sql("SELECT * FROM schema.wide_table")

# GOOD: select only what you need
df = spark.sql("SELECT customer_id, amount, transaction_date FROM schema.wide_table")

# GOOD: PySpark equivalent
df = spark.table("schema.wide_table").select("customer_id", "amount", "transaction_date")
```

**Why it's bad:** Delta Lake is columnar. Reading 50 columns when you need 3 is reading ~17x more data.

---

## 5. Function Wrapping Filter Columns

```python
# BAD: YEAR() wraps the column — Delta file skipping cannot apply
df.filter("YEAR(transaction_date) = 2024")

# BAD: same problem with CAST, MONTH, UPPER, etc.
df.filter("CAST(customer_id AS STRING) = '12345'")

# GOOD: range filter on raw column — Delta file statistics apply
df.filter("transaction_date >= '2024-01-01' AND transaction_date < '2025-01-01'")

# GOOD: filter on correctly typed column
df.filter(F.col("customer_id") == 12345)
```

---

## 6. Window Function Without PARTITION BY

```python
# BAD: global window — sorts ALL rows on a single executor
w_bad = Window.orderBy("transaction_date")
df.withColumn("rank", F.rank().over(w_bad))

# GOOD: partitioned window
w_good = Window.partitionBy("customer_id").orderBy("transaction_date")
df.withColumn("rank", F.rank().over(w_good))
```

**Why it's bad:** A global `ORDER BY` in a window function forces all data to one executor. On a 100M-row table this causes OOM.

---

## 7. Window on Raw Rows Instead of Pre-Aggregated

```python
# BAD: 30-day rolling average on 100M raw transactions
w = Window.partitionBy("customer_id").orderBy("transaction_date").rowsBetween(-29, 0)
df.withColumn("rolling_avg", F.avg("amount").over(w))  # 100M rows in window

# GOOD: daily aggregation first (365 rows per customer), then window
daily = df.groupBy("customer_id", "transaction_date").agg(
    F.sum("amount").alias("daily_total")
)
w_daily = Window.partitionBy("customer_id").orderBy("transaction_date").rowsBetween(-29, 0)
daily.withColumn("rolling_30d", F.avg("daily_total").over(w_daily))
```

---

## 8. Not Caching a Reused DataFrame

```python
# BAD: same expensive join recomputed 3 times
feature_1 = base_join().groupBy(...).agg(...)
feature_2 = base_join().groupBy(...).agg(...)
feature_3 = base_join().filter(...).select(...)

# GOOD: compute once, cache, reuse
base = (spark.table("transactions")
    .filter("date >= '2024-01-01'")
    .join(broadcast(segments), on="customer_id", how="left")
    .cache())
base.count()  # materialize

feature_1 = base.groupBy(...).agg(...)
feature_2 = base.groupBy(...).agg(...)
feature_3 = base.filter(...).select(...)

base.unpersist()  # release when done
```

---

## 9. Exact Percentile Instead of Approximate

```python
# BAD: exact percentile on 100M rows — full shuffle
df.select(F.percentile("amount", 0.95)).show()

# GOOD: approximate — sufficient for EDA and features, 10x faster
df.select(F.approx_percentile("amount", 0.95, relativeError=0.01)).show()

# GOOD: multiple percentiles in one pass
df.select(F.approx_percentile("amount", [0.25, 0.50, 0.75, 0.95, 0.99])).show()
```

---

## 10. Feeding a Lazy DataFrame Into `fit()` Then `transform().write()`

```python
# BAD: the whole join chain behind modeling_df runs TWICE
model = pipeline.fit(modeling_df)                 # execution #1
model.transform(modeling_df).write.save(...)      # execution #2 — recomputes everything

# GOOD: materialize once, then both reads are cheap
modeling_df = modeling_df.localCheckpoint(eager=True)
model = pipeline.fit(modeling_df)
model.transform(modeling_df).write.save(...)
```

**Why it's bad:** MLlib `fit` and the later `transform`/`write` are two separate actions. A lazy DataFrame is recomputed on each action, so an expensive multi-join `modeling_df` executes its entire DAG twice. `localCheckpoint(eager=True)` writes the result to executor-local disk so both actions read the materialized data (fast, but not fault-tolerant — recomputes from scratch on executor loss). Use a Delta intermediate write instead if the cluster is preemption-prone. `.cache()` also works but can be evicted under memory pressure, silently triggering recompute.

---

## 11. Joining a Big Feature Table Without Filtering to the Cohort First

```python
# BAD: feature_table (374M rows) shuffles in full, then most rows are discarded by the join
modeling_df = label_df.join(feature_table, on="customer_id", how="left")  # 30M labels

# GOOD: semi-join pre-filter drops non-matching feature rows BEFORE the shuffle
from pyspark.sql.functions import broadcast
cohort = label_df.select("customer_id").distinct()
feature_filtered = feature_table.join(broadcast(cohort), on="customer_id", how="leftsemi")
modeling_df = label_df.join(feature_filtered, on="customer_id", how="left")
```

**Why it's bad:** in a left-outer join only the keys present in the small label table can ever match. Shuffling the full feature table wastes the bulk of the work on rows that get thrown away. The `leftsemi` pre-filter preserves outer-join semantics (unmatched labels still get nulls) while shrinking the shuffle dramatically. See `join_strategies.md` §7.

---

## 12. Forgetting to Unpersist Cached DataFrames

```python
# BAD: cache accumulates across cells — others on the cluster OOM
df1.cache()
df2.cache()
df3.cache()
# ... never released

# GOOD: release as soon as you're done
df1.cache()
df1.count()
# ... use df1 ...
df1.unpersist()

# GOOD: use context pattern for important pipelines
try:
    base.cache()
    base.count()
    run_analysis(base)
finally:
    base.unpersist()
```
