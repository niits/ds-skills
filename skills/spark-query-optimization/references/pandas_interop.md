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

## Binary Classification Demo (One-Hot Categorical)  

Use this pattern when you want strong predictive performance from XGBoost and a rule-based interpretation layer from imodels.

```python
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from imodels import RuleFitClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score, roc_auc_score, f1_score

# 1) Example data (binary target + categorical columns)
rng = np.random.default_rng(42)
n = 20_000
df = pd.DataFrame({
    "amount": rng.normal(500, 120, size=n),
    "age": rng.integers(18, 70, size=n),
    "channel": rng.choice(["web", "app", "branch"], size=n, p=[0.45, 0.45, 0.10]),
    "segment": rng.choice(["A", "B", "C", "D"], size=n, p=[0.35, 0.30, 0.25, 0.10]),
})

# synthetic binary label with nonlinear signal
logit = (
    0.004 * (df["amount"] - 500)
    + 0.03 * (df["age"] < 25).astype(float)
    + 0.45 * (df["channel"] == "app").astype(float)
    + 0.35 * (df["segment"].isin(["C", "D"])).astype(float)
    - 1.4
)
prob = 1 / (1 + np.exp(-logit))
df["y"] = rng.binomial(1, prob)

# 2) One-hot encode categorical features
X = pd.get_dummies(df.drop(columns="y"), columns=["channel", "segment"], drop_first=False)
y = df["y"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3) XGBoost for predictive performance
pos = y_train.sum()
neg = len(y_train) - pos
xgb = XGBClassifier(
    n_estimators=400,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="binary:logistic",
    eval_metric="aucpr",
    scale_pos_weight=(neg / max(pos, 1)),
    random_state=42,
)
xgb.fit(X_train, y_train)

xgb_prob = xgb.predict_proba(X_test)[:, 1]
xgb_pred = (xgb_prob >= 0.5).astype(int)

print("XGBoost")
print("  AP      :", round(average_precision_score(y_test, xgb_prob), 4))
print("  ROC-AUC :", round(roc_auc_score(y_test, xgb_prob), 4))
print("  F1@0.50 :", round(f1_score(y_test, xgb_pred), 4))

# 4) imodels for interpretability (train on same one-hot features)
rulefit = RuleFitClassifier(
    n_estimators=200,
    tree_generator=xgb,   # distill tree structure from fitted XGBoost
    random_state=42,
)
rulefit.fit(X_train.values, y_train.values, feature_names=X_train.columns.tolist())

rf_prob = rulefit.predict_proba(X_test.values)[:, 1]
rf_pred = (rf_prob >= 0.5).astype(int)

print("RuleFit (imodels)")
print("  AP      :", round(average_precision_score(y_test, rf_prob), 4))
print("  ROC-AUC :", round(roc_auc_score(y_test, rf_prob), 4))
print("  F1@0.50 :", round(f1_score(y_test, rf_pred), 4))

# 5) Inspect learned rules (global explanations)
for i, rule in enumerate(rulefit.get_rules().query("coef != 0").head(10).itertuples(), 1):
    print(f"{i:02d}. coef={rule.coef:.4f}  rule={rule.rule}")
```

**Notes**
- `pd.get_dummies(...)` is enough if categorical columns are already one-hot ready.
- Tune threshold (`0.5` above) for business objective (precision-first vs recall-first).
- For very large data, keep feature prep in Spark, then pull only sampled/aggregated features to Pandas before training.

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
