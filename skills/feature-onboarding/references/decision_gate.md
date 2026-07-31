# Feature Decision Gate

Adopt or replace all default criteria before viewing results. Undefined terms such as
"adequate" or "measurable" produce `BLOCKED`, not discretionary PASS.

## Go/No-Go Criteria

Before production implementation, confirm:

- **Data:** structural absence and unknown missingness meet separate criteria; intended
  population coverage is adequate.
- **Motivation:** every candidate has a pre-computation hypothesis grounded in verified
  semantics, business purpose, and domain reality.
- **Predictive evidence:** retained candidates/groups meet predeclared univariate or
  interaction evidence standards.
- **Incremental lift:** the frozen set exceeds its noise-aware paired lift threshold.
- **Redundancy:** mode-specific ablation and matrix diagnostics justify overlap.
- **Temporal safety:** every input obeys event/effective and availability-time predicates.
- **No tautology:** lineage and formulas do not reconstruct the realized label window.
- **Stability:** drift is dispositioned and the frozen pipeline passes one untouched OOT.
- **Lag feasibility:** exact-period history and coverage support retained horizons.
- **Mode consistency:** representation, nulls, monotonicity, fairness, and reason codes
  match the selected mode.
- **Auditability:** the ledger contains criteria, evidence, disposition, owner, and versions.

## Scale-Aware Execution

Always run temporal leakage, tautology, and one untouched OOT confirmation. For large
feature groups, run incremental lift at group level, vectorize IV/PSI, and reserve costly
VIF or per-feature ablation for survivors. Record which tier was used; throughput never
waives the hard stops.

## Decision Recording

Correlation, prevalence, null rate, IV, or PSI alone does not mandate removal. Drop for
proven temporal leakage or label reconstruction; otherwise use uncertainty, operational
cost, model mode, stable incremental lift, and governance requirements. Do not revise
selection using the inspected OOT window.
