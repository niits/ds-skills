# EDA Patterns with PySpark

A systematic EDA checklist for large tables on Databricks. All operations are read-only.

---

## 1. First Contact with an Unknown Table

```python
df = spark.table("schema.table_name")

df.printSchema()          # types and nullable flags
df.show(5, truncate=False)
df.count()                # total rows — cache df first if reusing
```

```sql
-- Table size, partitioning, clustering keys
DESCRIBE DETAIL schema.table_name;

-- Column types + comments, partition info
DESCRIBE EXTENDED schema.table_name;

-- Recent write history
DESCRIBE HISTORY schema.table_name LIMIT 10;
```

---

## 2. Completeness — Null Analysis

```python
from pyspark.sql import functions as F

total = df.count()

null_stats = df.select([
    F.struct(
        F.lit(c).alias("column"),
        F.count(F.when(F.col(c).isNull(), 1)).alias("null_count"),
        (F.count(F.when(F.col(c).isNull(), 1)) / total * 100).alias("null_pct")
    ).alias(c)
    for c in df.columns
])

# Simpler: one row per column
null_df = df.select([
    F.count(F.when(F.col(c).isNull(), c)).alias(c)
    for c in df.columns
])
null_df.show()
```

---

## 3. Distribution — Numeric Columns

```python
# Built-in describe: count, mean, stddev, min, max
df.describe(numeric_cols).show()

# Percentiles — use approx for large tables
df.select([
    F.approx_percentile(c, [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]).alias(c)
    for c in numeric_cols
]).show()

# Outlier boundary (IQR method)
from pyspark.sql import functions as F

q1, q3 = df.approxQuantile("amount", [0.25, 0.75], relativeError=0.01)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

outlier_count = df.filter(
    (F.col("amount") < lower_bound) | (F.col("amount") > upper_bound)
).count()
```

---

## 4. Cardinality — Categorical Columns

```python
string_cols = [f.name for f in df.schema.fields if str(f.dataType) == "StringType"]

# Distinct count per column
df.select([F.countDistinct(c).alias(c) for c in string_cols]).show()

# Top values for a specific column
df.groupBy("category_col") \
  .count() \
  .orderBy("count", ascending=False) \
  .show(20, truncate=False)

# Value distribution as percentage
total = df.count()
df.groupBy("status") \
  .count() \
  .withColumn("pct", F.round(F.col("count") / total * 100, 2)) \
  .orderBy("count", ascending=False) \
  .show()
```

---

## 5. Temporal Analysis

```python
# Date range
df.select(F.min("event_date"), F.max("event_date")).show()

# Row count by month
df.groupBy(F.date_trunc("month", "event_date").alias("month")) \
  .count() \
  .orderBy("month") \
  .show(24)

# Day of week distribution
df.groupBy(F.dayofweek("event_date").alias("dow")) \
  .count() \
  .orderBy("dow") \
  .show()
```

---

## 6. Correlation (Numeric)

```python
from pyspark.ml.stat import Correlation
from pyspark.ml.feature import VectorAssembler

numeric_cols = [f.name for f in df.schema.fields
                if str(f.dataType) in ("DoubleType", "FloatType", "LongType", "IntegerType")]

assembler = VectorAssembler(inputCols=numeric_cols, outputCol="features")
vector_df = assembler.transform(df.select(numeric_cols).dropna()).select("features")

corr_matrix = Correlation.corr(vector_df, "features", method="pearson").head()[0]

# To Pandas for visualization
import pandas as pd
import numpy as np

corr_pd = pd.DataFrame(corr_matrix.toArray(), index=numeric_cols, columns=numeric_cols)
```

---

## 7. Duplicates

```python
# Check for duplicate primary keys
pk_cols = ["customer_id", "transaction_id"]

total = df.count()
distinct = df.select(pk_cols).distinct().count()

if total != distinct:
    print(f"Duplicates found: {total - distinct} extra rows")

# Show duplicate keys
df.groupBy(pk_cols) \
  .count() \
  .filter("count > 1") \
  .orderBy("count", ascending=False) \
  .show(10)
```

---

## 8. Class Imbalance (ML Data Prep)

```python
# Label distribution for classification
label_dist = df.groupBy("label").count()
label_dist.withColumn(
    "pct", F.round(F.col("count") / df.count() * 100, 2)
).orderBy("count", ascending=False).show()

# Stratified sample to balance (oversample minority)
minority_frac = {"positive": 1.0, "negative": 0.1}
balanced = df.sampleBy("label", fractions=minority_frac, seed=42)
```
