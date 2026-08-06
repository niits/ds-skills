# Evaluation Conclusion and Report

## Conclusion Taxonomy

- **Insufficient evidence:** a validity gate or decision-critical context is missing.
- **Model is worse:** the paired interval is wholly below zero on the oriented contrast.
- **Improvement inconclusive:** the paired interval includes zero.
- **Improvement demonstrated; useful margin unresolved or not reached:** the paired
  interval is above zero but includes or lies below the predeclared useful margin.
- **Meets predeclared offline criteria:** validity passes and paired estimates meet the
  declared useful margin, segment, operating, and uncertainty criteria.
- **Eligible for controlled online test:** offline criteria pass and experiment
  eligibility, guardrails, logging, fallback, rollback, and monitoring are defined.

No evaluation conclusion alone means production, safety, legal, or governance approval.
Require the smallest metric set that covers the estimand, operating policy, calibration
or uncertainty, and material harms; do not require an arbitrary metric count.

Use the paired interval rules in `topics/core/evaluation_protocol.md`. Report conclusions
against zero and against the useful margin separately; do not call an inconclusive result
"no improvement."

## Report Profiles

### Core Profile

Required for every formal conclusion:

1. Estimand, prediction/action unit, population, dates, task, and metric definitions.
2. Assumptions, missing evidence, split/label-maturity validity, and test-reuse disclosure.
3. Baseline, oriented paired difference, interval level/method/unit, and useful margin.
4. Frozen operating threshold or `k` when applicable, critical segments, and multiplicity status.
5. Direct conclusion, blocking risks, and the primary required next action.

### Diagnostic Profile

Add only for weak, suspicious, or conflicting results: observed signal, compatible
hypotheses, discriminating checks, and the evidence needed to support a cause.

### Economic Profile

Add only for a capacity, KPI, operating-value, or controlled-test decision: action,
counterfactual, capacity, costs, intervention-effect assumptions, scenario uncertainty,
and expected incremental value. Predictive metrics alone do not establish causal value.

### Probabilistic Forecasting Profile

Add for interval or distributional forecasts: quantile levels evaluated, scoring rule and
its averaging, observed coverage with interval width per horizon, the coverage estimate's
own uncertainty at the independent unit, and the baseline interval construction. Report
point-forecast accuracy and interval calibration separately; neither substitutes for the
other.

### Multi-Class and Multi-Label Profile

Add for more than two classes or labels: class or label count, per-class/per-label
support, the averaging scheme for every reported metric, the zero-division convention for
classes with no predictions, and — for multi-label — cardinality, per-label thresholds,
and subset accuracy alongside the averaged figures.

### Representation Profile

Add for representation claims: encoder checkpoint/provenance, claim scope, probe or
fine-tuning budget, query/gallery protocol, contamination status, encoder/probe seed
levels, datasets/tasks, and the breadth supported by the evidence.

## Conclusion Block

```markdown
## Conclusion: [INSUFFICIENT EVIDENCE | MODEL IS WORSE | IMPROVEMENT INCONCLUSIVE | IMPROVEMENT DEMONSTRATED; USEFUL MARGIN UNRESOLVED OR NOT REACHED | MEETS PREDECLARED OFFLINE CRITERIA | ELIGIBLE FOR CONTROLLED ONLINE TEST]

| Item | Result |
|---|---|
| Primary metric | [estimate, interval, support] |
| Baseline | [estimate and definition] |
| Paired contrast | [oriented difference, interval, method, independent unit] |
| Useful margin | [value and rationale; result against margin] |
| Operating point | [threshold or k, volume] |
| Protocol | [split, evaluator, averaging scheme, independent unit] |
| Optional profile | [diagnostic, economic, probabilistic forecasting, multi-class/multi-label, representation, or none] |
| Required action | [one action] |
```

## Metrics Summary

```markdown
| Metric | Model | Baseline | Difference/lift | Support and interval | Assessment |
|---|---|---|---|---|---|
| [metric] | [value] | [value] | [value] | [n/count/CI] | [direct assessment] |
```
