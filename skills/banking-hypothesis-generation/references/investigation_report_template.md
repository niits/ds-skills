# Investigation Report Template

Write all narrative as Markdown in Databricks `%md` cells. Do not use `displayHTML()`.

## Executive Summary

```markdown
## Hypothesis Investigation: [Phenomenon]

**Observation:** [metric, before/after values, population, period]
**Primary hypothesis:** [identifier and mechanism]
**Top recommendation:** [single discriminating next action]
**Decision required by:** [date]
```

## Hypothesis Block

```markdown
### H1: [Title]

**Mechanism:** [why this cause produces the observation]

**Key evidence:**
- [source and finding]
- [supporting data point]

**Falsification condition:** H1 is rejected if [observable outcome].
**Recommended test:** [dataset, comparison, metric, decision threshold]
```

## Prediction Table

```markdown
| Hypothesis | If true, expect | Falsified if | Test dataset |
|---|---|---|---|
| H1 | [quantitative prediction] | [rejection condition] | [cohort/window] |
| H2 | [different prediction] | [rejection condition] | [cohort/window] |
```

## Distinguishing Experiments

```markdown
| Test | Distinguishes | H1 expects | H2 expects |
|---|---|---|---|
| [test] | H1 vs H2 | [outcome] | [different outcome] |
```

Use inline author-year citations for external sources and a report name plus period for
internal evidence, for example `(Model Monitoring Report, Q4 2024)`.
