# Evaluation Protocol

## Required Context

Before interpreting metrics, establish:

- Task type and exact positive/relevant outcome.
- Evaluation population, split construction, dates, and independent decision unit.
- Label maturity, censoring, and entity overlap across splits.
- Dataset size, positive/relevant count, prevalence, and policy volume.
- Metric implementation, averaging/interpolation, threshold, or ranking cutoff `k`.
- Current heuristic, prior model, and relevant no-skill baseline.
- Business action, capacity, costs, constraints, and required operating point.

Assume only non-critical descriptive context. If a decision-critical item is unknown,
return `INSUFFICIENT EVIDENCE`, list what is missing, and stop before a shipping verdict.

## Uncertainty

For every headline and decision-critical segment report the point estimate, support,
and a confidence interval. For model comparisons report a paired interval for
model-minus-baseline or model-minus-challenger.

Resample the independent deployment unit such as customer, account, or query. Cluster
repeated observations and use temporal blocks or rolling origins for time-dependent
data. Predeclare confirmatory segments and mark low-support or exploratory comparisons
inconclusive.

## First Evaluation

When no prior model or A/B result exists, state which comparison axes are unavailable.
Still evaluate no-skill/heuristic lift, split stability, uncertainty, and segment
behavior. Absence of historical evidence is not permission to omit synthesis.

## Validity Checks

Check before model quality:

1. Metric computation and positive-class orientation.
2. Point-in-time split and feature validity.
3. Mature, complete outcomes for the evaluated cohort.
4. No prohibited entity overlap or duplicated decision units.
5. Comparable populations and policies across model comparisons.
