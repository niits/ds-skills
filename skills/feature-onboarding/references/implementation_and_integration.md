# Implementation and Integration

## Module Contract

Input: entity population, time range, optional lookback. Output:
`[entity_id, time_period, ...feature_cols]`.

The function must be deterministic, handle partial history and null sources, filter and
select early, and avoid writes, counts, or driver materialization. Before row-based lag,
assert one row per entity-period and densify the calendar; otherwise use exact-period joins.

Cache only an intermediate reused by multiple branches/actions. Do not unpersist a cached
parent before returning a still-lazy child; materialize first or let the caller own cache life.

Document feature groups, exclusions, null conventions, availability constraints, model
mode, and exported feature-name constants. Do not depend on implicit notebook state.

## Integration

1. Export and invoke the compute function from the feature pipeline.
2. Register/persist the feature group and run end to end.
3. Use the same transformation for training and serving.
4. Verify offline/online values on a representative sample.

For Databricks Feature Engineering:

- Precomputed `FeatureLookup` reads published materialized values; publish/sync them.
- Request-time computation requires on-demand feature functions, not plain lookup.
- Point-in-time training requires `timestamp_lookup_key`; otherwise current values leak.

## Reproducibility and Data Quality

Record keys, schema, source versions, code/transform version, parameters, runtime,
dependencies, and seeds. Use deterministic ordering with stable tie breakers. Require:

- Declared output key and uniqueness.
- Expected/actual key reconciliation using anti-joins both ways.
- Schema, null, finite-value, range, and source-period checks.
- Documented intentional exclusions and numeric tolerances.

Train/serve parity, key uniqueness, and finite-value integrity are unconditional hard stops.

## Monitoring Handoff

Define monitored features and score, reference bins/windows, freshness/publication lag,
coverage/null/range checks, feature and score drift, delayed-label performance, cadence,
thresholds, owner, escalation, and retraining/review triggers. Credit deployments also
need governance-defined calibration and fairness monitoring.
