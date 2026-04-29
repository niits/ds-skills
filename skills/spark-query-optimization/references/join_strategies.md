# Join Strategies for Data Scientists

Join optimization patterns available to DS without admin rights. All of these are query-level hints — no ALTER TABLE or admin access required.

---

## Decision Tree

```
How big is the smaller table?
├── < 30 MB   → Broadcast join (explicit hint or automatic)
├── 30MB–2GB  → Try broadcast with explicit threshold; otherwise sort-merge
└── Both large → Sort-merge (AQE handles skew automatically)
                 If known severe skew on specific key → SKEW hint
```

---

## 1. Broadcast Join (Most Common for DS)

Use when one table is a reference table, lookup, or pre-aggregated result.

```python
from pyspark.sql.functions import broadcast

# PySpark
result = large_df.join(broadcast(small_df), on="key", how="left")

# Spark SQL
spark.sql("""
    SELECT /*+ BROADCAST(ref) */ t.*, ref.label
    FROM events t
    LEFT JOIN reference_table ref ON t.category = ref.category
""")
```

**Raise broadcast threshold if your "small" table is slightly over 30MB:**

```python
# Session-level — safe for DS to set, doesn't affect other users
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 200 * 1024 * 1024)  # 200MB
```

**Common "small" tables safe to broadcast:**

- Country/region lookups
- Product/category mappings
- Customer segment labels
- Pre-aggregated feature windows (if result is small)
- Model score thresholds

---

## 2. Sort-Merge Join (Large-to-Large)

The default for two large tables. AQE handles this automatically — no hint needed in most cases.

```python
# Just write the join; AQE will optimize
result = transactions.join(
    customer_features,
    on=["customer_id", "feature_date"],
    how="inner"
)
```

**If you suspect skew, let AQE handle it first.** Check Spark UI → SQL tab → the join node should show `AQE: isRuntime=true`. If one task is 100x slower than others, then add a SKEW hint.

---

## 3. Skew Hint

Use when AQE doesn't resolve skew automatically (rare — try without hint first).

```sql
-- SQL hint
SELECT /*+ SKEW('transactions', 'customer_id') */
  t.*, f.risk_score
FROM transactions t
JOIN customer_features f ON t.customer_id = f.customer_id

-- Multi-column skew
SELECT /*+ SKEW('t', 'customer_id', ('UNKNOWN', NULL)) */
  ...
```

**Skew signals in Spark UI (Stages tab):**
- One task duration >> median task duration
- One partition has 10x more rows than average

---

## 4. Point-in-Time Join (Delta Time Travel)

Critical for ML pipelines. Use feature values as they existed at the training date, not current values. No admin rights needed for `AS OF` queries.

```python
# Delta time travel — reads table snapshot at a specific timestamp
features_historical = spark.sql("""
    SELECT customer_id, risk_score, credit_limit
    FROM feature_store.customer_features
    TIMESTAMP AS OF '2024-06-01T00:00:00'
""")

training_data = cohort.join(
    broadcast(features_historical), on="customer_id", how="left"
)
```

---

## 5. Self-Join (Comparing Rows Within a Group)

Useful for session analysis, pair comparisons, or deduplication.

```python
# Self-join to find transactions within 10 minutes of each other
df_alias_1 = df.alias("t1")
df_alias_2 = df.alias("t2")

result = df_alias_1.join(
    df_alias_2,
    on=(
        (F.col("t1.customer_id") == F.col("t2.customer_id")) &
        (F.col("t1.transaction_id") != F.col("t2.transaction_id")) &
        (F.abs(F.col("t1.timestamp").cast("long") - F.col("t2.timestamp").cast("long")) < 600)
    ),
    how="inner"
)

# Alternative (usually faster): use window function instead of self-join
w = Window.partitionBy("customer_id").orderBy("timestamp")
df.withColumn("prev_timestamp", F.lag("timestamp", 1).over(w)) \
  .withColumn("seconds_since_prev",
    F.col("timestamp").cast("long") - F.col("prev_timestamp").cast("long"))
```

---

## 6. Anti-Join (Find Rows NOT in Another Table)

Useful for finding customers without activity, records not in a reference set, etc.

```python
# Customers who have no transaction in last 90 days
active_customers = transactions \
    .filter("transaction_date >= '2024-07-01'") \
    .select("customer_id").distinct()

all_customers = spark.table("schema.customers").select("customer_id")

inactive = all_customers.join(active_customers, on="customer_id", how="left_anti")
```

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Joining without filtering the large table first | Add WHERE clause inside CTE before join |
| Broadcasting a table > 2GB | Don't — it will OOM executors; use sort-merge |
| Self-join when window function works | Prefer window functions — no shuffle |
| Missing join condition (creates cartesian) | Always verify join condition with EXPLAIN before running |
| Wrong join type (inner drops valid rows) | Use left join by default for enrichment; check null counts after |

---

## Check the Join Type in the Plan

Before running any join against a large table:

```python
result.explain()
# Look for:
#   BroadcastHashJoin     → good for small table joins
#   SortMergeJoin         → expected for large-to-large
#   CartesianProduct      → STOP — missing join condition, will OOM
```
