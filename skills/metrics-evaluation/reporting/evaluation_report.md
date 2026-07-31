# Evaluation Verdict and Report

## Verdict Taxonomy

- **Insufficient evidence:** validity or required context is missing; no shipping decision.
- **Not usable:** barely beats the relevant baseline; do not ship.
- **Weak, conditional:** useful only at a narrow operating point with material risk.
- **Adequate:** meaningful lift and a business-feasible operating point.
- **Good:** strong, stable lift suitable for the next controlled production test.
- **Strong:** material improvement over baseline and prior model, ready with monitoring.

Every verdict must cite numbers and uncertainty, at least two complementary metrics,
the diagnostic pattern, and one required next action. `Good` and `Strong` are unavailable
when uncertainty includes the baseline or business threshold.

## Required Report

Include:

1. Context, population, dates, task, and metric definitions.
2. Assumptions, missing evidence, and split/label-maturity validity gate.
3. Baselines and model point estimates with support and uncertainty.
4. Operating threshold or `k`, capacity, and segment results.
5. Economic translation and counterfactual assumptions.
6. Diagnostic pattern, alternative hypotheses, and discriminating checks.
7. Direct verdict and one required next action.

In Databricks, render Markdown in `%md` cells and do not use `displayHTML()`.

## Verdict Block

```markdown
## Verdict: [INSUFFICIENT EVIDENCE | NOT USABLE | WEAK - CONDITIONAL | ADEQUATE | GOOD | STRONG]

| Item | Result |
|---|---|
| Primary metric | [estimate, interval, support] |
| Baseline | [estimate and definition] |
| Complementary metric | [estimate, interval] |
| Operating point | [threshold or k, volume] |
| Pattern matched | [diagnostic pattern] |
| Business impact | [estimate and assumptions] |
| Required action | [one action] |
```

## Metrics Summary

```markdown
| Metric | Model | Baseline | Difference/lift | Support and interval | Assessment |
|---|---|---|---|---|---|
| [metric] | [value] | [value] | [value] | [n/count/CI] | [direct assessment] |
```
