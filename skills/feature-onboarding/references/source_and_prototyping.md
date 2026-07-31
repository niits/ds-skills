# Source Audit, Hypothesis Ledger, and Prototype

## Source Audit

Before computing features:

- Identify table, primary grain, schema, and ownership.
- Reconcile documented formulas on representative entities and periods with type-aware
  tolerances, units, null semantics, and exceptions.
- Record time range, period counts, target-population coverage, missingness, and mutually
  exclusive fields.
- Trace event/effective time and recorded/available time through lineage.

## Feature Decision Ledger

Create one row per candidate before data computation. Record:

- Name, formula, verified source semantics, lineage, population, and grain.
- Hypothesis: what subject behavior/state it measures and why it should relate to label.
- Event/effective time, availability time, scoring cutoff, boundary convention, label window.
- Null meaning, lag definition, model mode, and intended representation.
- Predeclared screening, lift, stability, uncertainty, and decision criteria.
- Results, final disposition/reason, owner, and data/code versions.

If the feature cannot be justified from source semantics, business decision, and
operational reality before computation, do not compute it. Name by measurement or
formula, not assumed meaning.

## Temporal Eligibility

Define scoring timestamp `T`, optional gap `g`, and non-overlapping label interval.
Event-driven scoring normally uses source data available before `T`; a closed period may
use `<= T` only when finalized before scoring. If historical values cannot be reproduced
as knowable at each cutoff, mark the candidate `BLOCKED`.

## Spark Prototype

- Use a separate exploration notebook and development data only.
- Load labels/target population plus enough historical source data for lags.
- Read the source once, filter early, perform one heavy aggregation, persist only when it
  fans out to multiple actions, and derive feature families from it.
- Keep computation distributed; no driver materialization or diagnostic actions in
  production-bound functions.
