---
name: databricks
description: Use when querying or shaping large data on Databricks with Spark SQL/PySpark and Delta Lake, or packaging a trained model with MLflow for reproducible notebook-independent serving. Covers profiling, optimization, feature engineering, wide joins, model logging, registry aliases, and batch inference.
allowed-tools: Read Write Edit Bash
license: MIT; third-party notices apply
metadata:
    skill-author: ds-skills
    domain: general
    adapted-for: Databricks Runtime 13+ (Spark 3.4+, MLflow 2.x)
---

# Databricks for Data Scientists

Use Part A to produce correct, efficient training or analysis data and Part B to package
the resulting model as a reproducible artifact.

## Part A: Spark and Delta Workflow

1. **Profile first.** Inspect schema, table detail/history, size, partitions/clustering,
   date range, row grain, and skew. Follow `references/query_workflow.md`.
2. **Develop on a representative sample.** Set seeds and preserve class/segment coverage.
3. **Filter and select early.** Use raw-column range predicates, fixed dates, and only
   needed columns before joins.
4. **Choose joins from measured sizes and semantics.** Use
   `references/join_strategies.md`; a Delta snapshot is not a per-row as-of join.
5. **Aggregate and window safely.** Prefer built-ins, partition every large window, and
   pre-aggregate before windowing. Use `references/window_aggregation_patterns.md`.
6. **Avoid Python row overhead.** Built-in SQL/DataFrame functions first, Pandas UDFs
   second, Python UDFs only as a last resort.
7. **Keep large EDA distributed.** Use `references/eda_patterns.md`; bound data before
   `toPandas()` with `references/pandas_interop.md`.
8. **Cache or materialize deliberately.** Reuse only, force materialization when needed,
   and release ownership explicitly. Use `references/caching_and_plan_debugging.md`.
9. **Inspect the physical plan before expensive actions.** Fix cartesian products,
   missing pushdown, unintended sort-merge joins, and pathological shuffle first.
10. **For wide modeling datasets**, prefilter feature tables by cohort keys, order joins,
    size shuffle partitions, and materialize before repeated MLlib actions using
    `references/join_chain_optimization.md`.

Feature patterns for lag, rolling aggregation, encoding, interactions, and time fields
are in `references/feature_engineering.md`.

## Part B: MLflow Packaging Workflow

1. Package preprocessing and estimator together as an sklearn pipeline or `pyfunc`.
2. Log an input example, signature, exact dependencies, params, metrics, and artifacts.
3. Load the artifact in a fresh process to prove it has no notebook-state dependency.
4. Register in Unity Catalog and promote consumers through a stable alias such as
   `@champion`, not a run ID.
5. Run distributed batch inference as an idempotent Databricks Job over a fixed input
   window.

Use the complete patterns and checklist in `references/mlflow_model_packaging.md`.

## Hard Rules

- Do not use `SELECT *` or functions around filter columns on large scans.
- Never run an unpartitioned window over a large table.
- Never collect or call unbounded `toPandas()` on large data.
- Use built-ins instead of Python UDFs whenever possible.
- Read the plan before submitting expensive work; fix `CartesianProduct` immediately.
- Point-in-time feature joins require per-row event-time semantics; time travel alone is
  only a reproducible whole-table snapshot.
- Logged models include preprocessing, schema, exact dependencies, and external artifacts.
- Logged model code must not depend on `spark`, `dbutils`, widgets, globals, or relative
  notebook imports.
- Flag storage maintenance and stale-statistics issues to data engineering rather than
  attempting privileged production-table operations.

## References

- `references/query_workflow.md` - profiling, sampling, pushdown, and UDF hierarchy.
- `references/join_strategies.md` - broadcast, skew, semi, self, and as-of joins.
- `references/window_aggregation_patterns.md` - aggregation and window recipes.
- `references/eda_patterns.md` - distributed EDA.
- `references/pandas_interop.md` - Arrow and driver-memory safety.
- `references/caching_and_plan_debugging.md` - persistence, plans, runtime diagnosis.
- `references/join_chain_optimization.md` - wide feature join chains and MLlib reuse.
- `references/feature_engineering.md` - Spark feature patterns.
- `references/anti_patterns.md` - common correctness and performance failures.
- `references/mlflow_model_packaging.md` - logging, pyfunc, registry, and batch scoring.
