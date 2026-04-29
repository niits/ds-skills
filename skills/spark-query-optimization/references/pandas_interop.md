# Pandas / Spark Interoperability

How to safely move data between Spark DataFrames and Pandas, and when to use each.

---

## The Core Rule

**Pandas runs on the driver.** Spark runs across executors. Every `.toPandas()` call pulls data from the cluster to a single machine. The driver typically has 8–32GB of RAM. Plan accordingly.

```
Spark DataFrame  →  (safe: filter + limit first)  →  Pandas DataFrame
Pandas DataFrame →  (always safe: small data)     →  Spark DataFrame
```

---

## Safe toPandas() Pattern

```python
# Always follow this order before toPandas():
pandas_df = (spark_df
    .filter("date >= '2024-01-01'")          # 1. Filter rows
    .filter("segment = 'ACTIVE'")
    .select("id", "feature_1", "feature_2")  # 2. Select only needed columns
    .limit(500_000)                           # 3. Hard limit as safety net
    .toPandas())                              # 4. Pull to driver

# Size check before pulling
count = spark_df.filter(...).select(...).count()
print(f"Will pull {count:,} rows")
assert count < 1_000_000, "Too many rows for toPandas — aggregate first"
```

---

## Arrow Optimization

Arrow is enabled by default on Databricks. It batches row transfer using Apache Arrow instead of serializing row-by-row — ~10x faster for large results.

```python
# Check (should be 'true' on Databricks DBR 13+)
spark.conf.get("spark.sql.execution.arrow.pyspark.enabled")

# If not enabled (vanilla Spark):
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
```

---

## Pandas → Spark (createDataFrame)

```python
import pandas as pd
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType

pandas_df = pd.DataFrame({"customer_id": ["A", "B"], "score": [0.8, 0.3]})

# Without schema — Spark infers types (may infer incorrectly for int/float)
spark_df = spark.createDataFrame(pandas_df)

# With explicit schema — more reliable, avoids type mismatches
schema = StructType([
    StructField("customer_id", StringType(), nullable=False),
    StructField("score", DoubleType(), nullable=True),
])
spark_df = spark.createDataFrame(pandas_df, schema=schema)
```

---

## Pandas UDF (Vectorized Bridge)

When you need to run Python/Pandas logic at scale without leaving Spark:

```python
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import DoubleType, StringType
import pandas as pd

# Scalar UDF: one output value per row (Series → Series)
@pandas_udf(DoubleType())
def normalize_amount(amount: pd.Series, mean: pd.Series, std: pd.Series) -> pd.Series:
    return (amount - mean) / std.clip(lower=1e-6)

# Grouped Map UDF: receive entire group as DataFrame, return transformed DataFrame
from pyspark.sql.functions import PandasUDFType

schema = "customer_id string, amount double, scaled_amount double"

@pandas_udf(schema, PandasUDFType.GROUPED_MAP)
def scale_per_customer(pdf: pd.DataFrame) -> pd.DataFrame:
    pdf["scaled_amount"] = (pdf["amount"] - pdf["amount"].mean()) / max(pdf["amount"].std(), 1e-6)
    return pdf[["customer_id", "amount", "scaled_amount"]]

result = df.groupBy("customer_id").apply(scale_per_customer)
```

---

## When to Use Each

| Use case | Recommendation |
|---|---|
| EDA on large table | Spark: `.describe()`, `.approx_percentile()`, `.groupBy()` |
| Modeling (sklearn, xgboost) | Pandas: pull aggregated/sampled features |
| Visualization (matplotlib, seaborn) | Pandas: aggregate to small result first |
| Custom transforms (vectorizable) | `@pandas_udf` — stays in Spark |
| Writing predictions back to Delta | Spark: `createDataFrame(pred_df).write.format("delta")` |
| Quick interactive exploration | Pandas on `.limit(10_000).toPandas()` |

---

## Size Thresholds (Rule of Thumb)

| Rows | Columns | Estimated size | Action |
|---|---|---|---|
| < 100K | any | < 100MB | Safe to `.toPandas()` directly |
| 100K – 1M | < 50 | ~100MB–1GB | `.toPandas()` after column select |
| 1M – 10M | < 20 | ~1–5GB | Aggregate in Spark first |
| > 10M | any | > 5GB | Never use `.toPandas()` — model in Spark (MLlib) |

---

## Writing Results Back

```python
# Write Pandas predictions to your dev schema (if write access granted)
predictions_spark = spark.createDataFrame(pred_df, schema=output_schema)

predictions_spark.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("dev.my_username.model_predictions")

# Or write to temp view for current session only (no write access needed)
predictions_spark.createOrReplaceTempView("my_predictions")
spark.sql("SELECT * FROM my_predictions LIMIT 10").show()
```
