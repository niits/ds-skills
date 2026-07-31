# Caching, Materialization, and Plan Debugging

## Persistence

Cache a filtered/joined DataFrame only when multiple downstream actions reuse it.

```python
base = filtered.join(reference, "key").persist()
base.count()  # materialize intentionally
first = base.groupBy("customer_id").agg(...)
second = base.groupBy("segment").agg(...)
base.unpersist()
```

- Default `MEMORY_AND_DISK` is safe for reusable session data.
- Use `DISK_ONLY` when data exceeds executor memory and is expensive to recompute.
- Do not cache one-use DataFrames or enormous scans likely to churn the cache.
- Make ownership explicit; do not unpersist a parent before a lazy returned child runs.
- Materialize long join chains before repeated MLlib `fit`/`transform` actions; choose
  local checkpoint versus durable Delta based on cluster fault tolerance.

## Inspect the Plan

```python
df.explain()
df.explain(mode="extended")
df.explain(mode="cost")
```

Good signals include `PushedFilters`, intended `BroadcastHashJoin`, and active AQE.
Investigate absent pushdown, sort-merge joins against known-small tables, unknown or
impossible cardinality estimates, excessive exchanges, and `CartesianProduct`.

## Runtime Diagnosis

Use the Spark UI SQL/stage views to compare scan, shuffle, spill, skew, failed tasks,
and output volume. Stop work for a structural mistake, explosive shuffle relative to
input, cartesian join, or repeatedly failing stages. A few progressing tail tasks or
small bounded spill may justify waiting and optimizing the next run.

Size `spark.sql.shuffle.partitions` from expected shuffle volume, aiming for practical
partition sizes rather than accepting the default for hundreds of GiB. AQE can coalesce
small partitions and handle skew, but cannot repair incorrect filters or join semantics.
