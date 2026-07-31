# Spark Query Workflow

## Scope and Privileges

Data scientists can normally inspect (`DESCRIBE DETAIL/EXTENDED/HISTORY`, `EXPLAIN`),
query, create temporary views, apply query hints, persist session DataFrames, and write
to granted scratch schemas. Production `OPTIMIZE`, `VACUUM`, `ANALYZE TABLE`, clustering,
and DDL require appropriate privileges; escalate storage-layout or statistics problems.

## Profile Before Querying

```sql
DESCRIBE DETAIL schema.table_name;
DESCRIBE EXTENDED schema.table_name;
DESCRIBE HISTORY schema.table_name LIMIT 10;
```

```python
df = spark.table("schema.table_name")
df.printSchema()
df.summary().show()
```

Record size, row grain, partition/clustering columns, common filters, needed columns,
date coverage, and known skew. Avoid repeated full actions merely for profiling.

## Sample Before Scale

```python
sample = df.sample(fraction=0.01, seed=42)
quick_schema_check = df.limit(10_000)
balanced = df.sampleBy("label", {0: 0.01, 1: 0.1}, seed=42)
```

Use random sampling for EDA, `limit` only for quick structural checks, and stratified
sampling when rare classes/segments must remain represented. Always set a seed.

## Filter and Select Early

Filter raw columns with half-open ranges so Delta statistics can skip files:

```sql
WITH recent AS (
  SELECT customer_id, transaction_date, amount
  FROM transactions
  WHERE transaction_date >= '2025-01-01'
    AND transaction_date < '2026-01-01'
    AND status <> 'VOIDED'
)
SELECT r.*, c.segment
FROM recent r
JOIN customers c ON r.customer_id = c.customer_id;
```

Avoid `YEAR(transaction_date) = 2025`, `SELECT *`, late filters after large joins, and
relative dates in reproducible pipelines.

## Aggregation and UDF Hierarchy

Prefer built-in DataFrame/SQL functions, then vectorized Pandas UDFs, then Python UDFs.
Built-ins remain Catalyst-optimized and avoid row serialization. Use sketch-based
`approx_percentile` for large EDA instead of exact full-sort percentiles.

```python
result = df.groupBy("customer_id", "month").agg(
    F.sum("amount").alias("total_amount"),
    F.count("*").alias("txn_count"),
    F.approx_percentile("amount", 0.95).alias("p95_amount"),
)
```

Use Pandas UDFs only for vectorizable logic unavailable in Spark functions. Never call
`collect()` in an entity loop or use a Python UDF for simple math/string/date operations.
