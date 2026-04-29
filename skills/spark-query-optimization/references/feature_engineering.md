# Feature Engineering Patterns in PySpark

Common feature engineering patterns for DS building ML training data on Spark. All patterns use read access only — no admin operations required.

---

## Setup Pattern

Always start with a filtered base DataFrame and cache it before computing multiple features:

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Base: filtered, joined to needed reference data
base = (spark.table("schema.transactions")
    .filter("transaction_date >= '2023-01-01'")
    .filter("status = 'SETTLED'")
    .select("customer_id", "transaction_date", "amount",
            "merchant_category", "channel")
    .cache())
base.count()   # materialize cache

# Build features on top of base
```

---

## 1. Lag Features

```python
w = Window.partitionBy("customer_id").orderBy("transaction_date")

df = base.withColumn("amount_lag_1d",  F.lag("amount", 1).over(w))
df = df.withColumn("amount_lag_7d",   F.lag("amount", 7).over(w))
df = df.withColumn("days_since_last",
    F.datediff(F.col("transaction_date"), F.lag("transaction_date", 1).over(w)))
```

---

## 2. Rolling Aggregations (Pre-Aggregate First)

For large tables, always aggregate to daily granularity before applying rolling windows.

```python
# Step 1: daily aggregation (reduces cardinality from 100M to ~365 rows/customer)
daily = base.groupBy("customer_id", "transaction_date").agg(
    F.sum("amount").alias("daily_amount"),
    F.count("*").alias("daily_cnt"),
    F.countDistinct("merchant_category").alias("daily_unique_merchants")
)

# Step 2: rolling windows on daily table
w_30 = Window.partitionBy("customer_id").orderBy("transaction_date").rowsBetween(-29, 0)
w_90 = Window.partitionBy("customer_id").orderBy("transaction_date").rowsBetween(-89, 0)

features = daily.select(
    "customer_id", "transaction_date",
    F.sum("daily_amount").over(w_30).alias("sum_amount_30d"),
    F.avg("daily_amount").over(w_30).alias("avg_amount_30d"),
    F.max("daily_amount").over(w_30).alias("max_amount_30d"),
    F.sum("daily_cnt").over(w_30).alias("txn_count_30d"),
    F.sum("daily_amount").over(w_90).alias("sum_amount_90d"),
    F.avg("daily_amount").over(w_90).alias("avg_amount_90d"),
)
```

---

## 3. Time-Based Features

```python
df = df.withColumn("day_of_week",   F.dayofweek("transaction_date"))     # 1=Sun, 7=Sat
df = df.withColumn("day_of_month",  F.dayofmonth("transaction_date"))
df = df.withColumn("month",         F.month("transaction_date"))
df = df.withColumn("quarter",       F.quarter("transaction_date"))
df = df.withColumn("is_weekend",
    F.when(F.dayofweek("transaction_date").isin([1, 7]), 1).otherwise(0))
df = df.withColumn("is_month_end",
    F.when(F.dayofmonth("transaction_date") >= 28, 1).otherwise(0))
df = df.withColumn("hour_of_day",   F.hour("transaction_timestamp"))     # if timestamp available
```

---

## 4. Categorical Encoding

```python
# Frequency encoding (works at Spark scale — no admin needed)
cat_freq = base.groupBy("merchant_category").count() \
    .withColumnRenamed("count", "merchant_category_freq")
df = df.join(broadcast(cat_freq), on="merchant_category", how="left")

# Target encoding (mean of target per category — do on training set only)
train_base = base.filter("split = 'train'")
target_enc = train_base.groupBy("merchant_category").agg(
    F.avg("label").alias("merchant_category_target_enc")
)
df = df.join(broadcast(target_enc), on="merchant_category", how="left")

# Ordinal encoding using a lookup table
ordinal_map = spark.createDataFrame([
    ("LOW", 0), ("MEDIUM", 1), ("HIGH", 2)
], ["risk_tier", "risk_tier_ordinal"])
df = df.join(broadcast(ordinal_map), on="risk_tier", how="left")
```

---

## 5. Interaction Features

```python
# Ratio features
df = df.withColumn("avg_txn_amount",
    F.col("total_amount_30d") / F.greatest(F.col("txn_count_30d"), F.lit(1)).cast("double"))

df = df.withColumn("amount_velocity",
    F.col("sum_amount_30d") / F.greatest(F.col("sum_amount_90d"), F.lit(0.01)))

# Boolean interaction
df = df.withColumn("high_amount_weekend",
    (F.col("is_weekend") & (F.col("amount") > 500)).cast("int"))
```

---

## 6. Point-in-Time Features (Delta Time Travel)

Critical for ML: use feature values as they existed at a past date, not current values.

```python
# Delta time travel — reads the table as it existed at a specific timestamp
# No admin rights needed for SELECT with AS OF
features_at_snapshot = spark.sql("""
    SELECT customer_id, risk_score, segment, credit_limit
    FROM feature_store.customer_features
    TIMESTAMP AS OF '2024-06-01T00:00:00'
    WHERE customer_id IN (SELECT DISTINCT customer_id FROM training_cohort)
""")

# Join to training cohort with point-in-time correctness
training_data = cohort.join(
    features_at_snapshot, on="customer_id", how="left"
)
```

---

## 7. Rank and Percentile Features

```python
w_rank = Window.partitionBy("segment").orderBy(F.desc("amount"))

df = df.withColumn("amount_rank_in_segment",   F.rank().over(w_rank))
df = df.withColumn("amount_dense_rank",        F.dense_rank().over(w_rank))
df = df.withColumn("amount_percentile",
    F.percent_rank().over(w_rank))   # 0.0 to 1.0 within segment
```

---

## 8. Handling Nulls in Features

```python
# Fill numeric nulls with median (compute median first)
median_amount = df.approxQuantile("amount", [0.5], relativeError=0.01)[0]
df = df.fillna({"amount": median_amount})

# Fill categorical nulls
df = df.fillna({"merchant_category": "UNKNOWN", "channel": "OTHER"})

# Flag null with indicator column (often more informative than imputation)
df = df.withColumn("amount_was_null",
    F.when(F.col("amount").isNull(), 1).otherwise(0))
df = df.fillna({"amount": 0.0})

# Drop rows where key features are null
df = df.dropna(subset=["customer_id", "transaction_date", "label"])
```

---

## 9. Assembling for ML (Spark MLlib)

```python
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml import Pipeline

feature_cols = [
    "sum_amount_30d", "txn_count_30d", "avg_amount_30d",
    "days_since_last", "day_of_week", "merchant_category_freq",
    "amount_was_null"
]

assembler = VectorAssembler(inputCols=feature_cols, outputCol="features_raw",
                            handleInvalid="keep")  # keep=impute with 0 for nulls
scaler = StandardScaler(inputCol="features_raw", outputCol="features",
                        withStd=True, withMean=True)

pipeline = Pipeline(stages=[assembler, scaler])
model = pipeline.fit(train_df)
train_featurized = model.transform(train_df)
```

---

## 10. Train / Test Split

```python
# Random split (reproducible with seed)
train, test = df.randomSplit([0.8, 0.2], seed=42)

# Time-based split (preferred for time series / financial data — avoids leakage)
train = df.filter("transaction_date < '2024-10-01'")
test  = df.filter("transaction_date >= '2024-10-01'")

# Stratified split — preserve class balance
train = df.sampleBy("label", fractions={"0": 0.8, "1": 0.8}, seed=42)
test  = df.exceptAll(train)
```
