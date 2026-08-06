# Evaluation Protocol

## Required Context

Before interpreting metrics, establish:

- Task type, exact outcome, target population, policy/exposure regime, and horizon.
- Prediction unit, action unit, analysis unit, aggregation/weighting, split construction,
  dates, and independent deployment unit.
- Label maturity, censoring, and entity overlap across splits.
- Dataset size, positive/relevant count, prevalence, and policy volume.
- Model-output representation and frozen evaluator contract: implementation, orientation,
  averaging, interpolation, ties, undefined cases, threshold, and cutoff when applicable.
- Current heuristic, prior model, and relevant no-skill baseline.
- Business action, capacity, costs, constraints, and required operating point when the
  requested conclusion concerns operating or economic value.
- For multi-class or multi-label targets: class/label count, per-class support, averaging
  scheme, and per-label threshold policy.
- For probabilistic forecasts: quantile levels, scoring rule, nominal interval level, and
  the horizon at which coverage is claimed.
- For anomaly detection: supervised, delayed-label, positive-unlabeled, event-based, or
  fully unsupervised setting and the available label evidence.
- For representations: claim being tested, frozen/fine-tuned status, probe recipe,
  query/gallery construction, contamination controls, and training-seed count.

Load `topics/core/evaluator_semantics.md` when these choices can change the reported result.

Assume only non-critical descriptive context. If a decision-critical item is unknown,
return `INSUFFICIENT EVIDENCE`, list what is missing, and stop before the requested
decision conclusion.

## Uncertainty

For every headline and decision-critical segment report the point estimate, support,
and a confidence interval. For model comparisons report a paired interval for
model-minus-baseline or model-minus-challenger.

Define an oriented paired difference `delta = model - baseline`, with larger values
always better, and a predeclared minimum useful margin `m >= 0` when practical usefulness
is being tested.

| Paired interval result | Supported conclusion |
|---|---|
| Upper bound `< 0` | Model is worse on the declared contrast |
| Interval includes `0` | Improvement is inconclusive |
| Lower bound `> 0` | Improvement is demonstrated |
| Upper bound `< m` | Useful margin is not reached |
| Lower bound `<= m` and upper bound `>= m` | Useful-margin status is inconclusive |
| Lower bound `> m` | Useful margin is demonstrated |

Report the comparison against zero and against `m` separately. Failure to demonstrate
improvement is not evidence of equivalence. Equivalence and non-inferiority require their
own predeclared margins and procedures.

Resample the independent deployment unit such as customer, account, identity, session,
series, or query group. Do not bootstrap correlated rows, labels, pairs, or time points as
if independent. Recompute the complete evaluator within each replicate.
Use temporal blocks or rolling origins for time-dependent data. State the interval level,
method, resampling unit, and assumptions. Report test-sample uncertainty separately from
training-seed and probe-seed variation. Predeclare confirmatory segments and mark low-
support or exploratory comparisons inconclusive. If several metrics, segments, or
thresholds can independently determine a confirmatory conclusion, predeclare the family
and use simultaneous or multiplicity-adjusted inference; otherwise label it exploratory.

Fit preprocessing, feature selection, calibration, threshold selection, and model
selection only on development data. Use an outer evaluation loop when the conclusion
must include pipeline-selection variability, and disclose test-set reuse.

## First Evaluation

When no prior model or A/B result exists, state which comparison axes are unavailable.
Still evaluate no-skill/heuristic lift, split stability, uncertainty, and segment
behavior. Absence of historical evidence is not permission to omit synthesis.

## Validity Checks

Check before model quality:

1. Metric computation and positive-class orientation.
2. Split design that represents deployment: time, entity, group, location, or an
   exchangeable random split as justified; point-in-time feature validity is independent
   of split type.
3. Mature, complete outcomes for the evaluated cohort.
4. No prohibited entity overlap or duplicated decision units.
5. Comparable populations and policies across model comparisons.
6. Comparable candidate, gallery, and probe protocols.
7. No near-duplicate records, identities, or correlated sessions crossing split
   boundaries unless that overlap is part of the declared deployment estimand.
