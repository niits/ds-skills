# Window & Aggregation Patterns

Reference for window functions and aggregation patterns used in DS pipelines on Spark.

---

## Window Spec Quick Reference

```python
from pyspark.sql.window import Window
from pyspark.sql import functions as F

# Partition only (no ordering) — for aggregations over the whole group
w_partition = Window.partitionBy("customer_id")

# Ordered within partition — for rank, lag, lead
w_ordered = Window.partitionBy("customer_id").orderBy("transaction_date")

# Ordered with row frame — for rolling aggregations
w_rolling_30 = (Window
    .partitionBy("customer_id")
    .orderBy("transaction_date")
    .rowsBetween(-29, 0))   # current + 29 preceding rows

# Ordered with range frame — for time-based windows (use with timestamp/date col)
w_range_7d = (Window
    .partitionBy("customer_id")
    .orderBy(F.col("transaction_date").cast("long"))
    .rangeBetween(-7 * 86400, 0))   # 7 days in seconds

# Full partition frame — running total / cumulative
w_cumulative = (Window
    .partitionBy("customer_id")
    .orderBy("transaction_date")
    .rowsBetween(Window.unboundedPreceding, 0))
```

**Prefer `rowsBetween` over `rangeBetween`** when working with daily data — it's faster and more predictable. Use `rangeBetween` only when you need exact time intervals and your data is not daily.

---

## Rank & Ordering

```python
w = Window.partitionBy("customer_id").orderBy(F.desc("amount"))

df.withColumn("rank",        F.rank().over(w))         # gaps on tie: 1,1,3
df.withColumn("dense_rank",  F.dense_rank().over(w))   # no gaps: 1,1,2
df.withColumn("row_number",  F.row_number().over(w))   # unique: 1,2,3
df.withColumn("percent_rank", F.percent_rank().over(w)) # 0.0–1.0

# Get top 1 per group (deduplication)
w_dup = Window.partitionBy("customer_id").orderBy(F.desc("transaction_date"))
df.withColumn("rn", F.row_number().over(w_dup)).filter("rn = 1").drop("rn")
```

---

## Lead / Lag

```python
w = Window.partitionBy("customer_id").orderBy("transaction_date")

df.withColumn("prev_amount",      F.lag("amount", 1).over(w))
df.withColumn("next_amount",      F.lead("amount", 1).over(w))
df.withColumn("prev_amount_3",    F.lag("amount", 3).over(w))   # 3 rows back

# Days since previous transaction
df.withColumn("days_since_prev",
    F.datediff(F.col("transaction_date"), F.lag("transaction_date", 1).over(w)))
```

---

## Rolling Aggregations (ROWS BETWEEN)

```python
w_30 = Window.partitionBy("customer_id").orderBy("date").rowsBetween(-29, 0)
w_90 = Window.partitionBy("customer_id").orderBy("date").rowsBetween(-89, 0)

# On daily aggregated table (NOT on raw 100M rows)
daily.select(
    "customer_id", "date", "daily_amount",
    F.sum("daily_amount").over(w_30).alias("sum_30d"),
    F.avg("daily_amount").over(w_30).alias("avg_30d"),
    F.max("daily_amount").over(w_30).alias("max_30d"),
    F.min("daily_amount").over(w_30).alias("min_30d"),
    F.count("*").over(w_30).alias("active_days_30d"),
    F.sum("daily_amount").over(w_90).alias("sum_90d"),
    F.avg("daily_amount").over(w_90).alias("avg_90d"),
)
```

---

## Cumulative (Running Total)

```python
w_cum = (Window
    .partitionBy("customer_id")
    .orderBy("transaction_date")
    .rowsBetween(Window.unboundedPreceding, 0))

df.withColumn("cumulative_amount", F.sum("amount").over(w_cum))
df.withColumn("cumulative_count",  F.count("*").over(w_cum))
```

---

## First / Last Value in Group

```python
w = Window.partitionBy("customer_id").orderBy("transaction_date")
w_full = Window.partitionBy("customer_id").orderBy("transaction_date") \
    .rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)

df.withColumn("first_txn_date",
    F.first("transaction_date", ignorenulls=True).over(w_full))
df.withColumn("last_txn_date",
    F.last("transaction_date",  ignorenulls=True).over(w_full))
df.withColumn("first_txn_amount",
    F.first("amount", ignorenulls=True).over(w_full))
```

---

## GroupBy Aggregation (No Window)

```python
# Standard: prefer agg() over chained aggregation methods
result = df.groupBy("customer_id", "month").agg(
    F.sum("amount").alias("total"),
    F.count("*").alias("txn_count"),
    F.countDistinct("merchant_id").alias("unique_merchants"),
    F.approx_percentile("amount", 0.95).alias("p95"),
    F.max("amount").alias("max_amount"),
    F.min("amount").alias("min_amount"),
    F.stddev("amount").alias("amount_stddev"),
    F.first("channel").alias("most_common_channel"),   # non-deterministic — OK for EDA
)

# Multiple aggregations on the same column in one pass
result = df.groupBy("customer_id").agg(
    *[F.approx_percentile("amount", p).alias(f"p{int(p*100)}")
      for p in [0.25, 0.50, 0.75, 0.95, 0.99]]
)
```

---

## Pivot (Wide Format)

```python
# Monthly totals per channel — pivoted to wide format
pivot = (df
    .groupBy("customer_id")
    .pivot("channel", ["WEB", "MOBILE", "BRANCH"])  # explicit values = faster
    .agg(F.sum("amount")))

# Output: customer_id | WEB | MOBILE | BRANCH
```

---

## Performance Notes

| Pattern | When | Notes |
|---|---|---|
| `rowsBetween` | Most rolling windows | Faster than `rangeBetween` |
| `rangeBetween` | Exact time interval (seconds) | Cast date to `long` first |
| Pre-aggregate then window | Raw table > 1M rows | Always — reduces window input by 100x+ |
| `approx_percentile` | EDA, feature engineering | 10x faster than `percentile`, sufficient accuracy |
| Multiple `.withColumn(window)` | Building many window features | Group into `.select()` — one shuffle |
