---
name: banking-hypothesis-generation
description: Structured hypothesis formulation for banking data science. Use when experimental observations, model results, or business data require testable hypotheses, predictions, mechanisms, and experiments across credit risk, fraud, customer analytics, AML, or model validation.
allowed-tools: Read Write Edit Bash
license: MIT; third-party notices apply
metadata:
    skill-author: ds-skills
    domain: banking
    adapted-for: Databricks (no LaTeX output; %md cells for narrative, display(fig) for figures)
---

# Hypothesis Generation - Banking Domain

## Purpose

Turn a measured banking phenomenon into competing, falsifiable explanations and tests.
A hypothesis is a directional mechanism:

> If X changes, metric Y changes by direction or magnitude Z in population W because M.

Use this skill for model- or phenomenon-level investigations. Use `feature-onboarding`
for hypotheses that justify individual candidate features before computation.

## Use When

- A model metric regresses or behaves unexpectedly.
- PSI, KS, calibration, or vintage performance changes.
- A champion-challenger, policy test, or validation investigation needs design.
- Investigation candidates must be prioritized for a constrained sprint.

## Workflow

1. **Scope the observation.** Record the metric change, population, product, time and
   performance windows, data as-of date, and what remains unknown. Follow
   `references/investigation_workflow.md`.
2. **Gather evidence internal-first.** Review monitoring, vintage, feature-attribution,
   data-quality, strategy, inventory, and macro evidence. Add external evidence only
   when useful; follow `references/literature_search_strategies.md`.
3. **Synthesize mechanisms.** Separate proximate evidence, plausible mechanisms,
   unexplained residuals, and analogues from prior incidents.
4. **Prioritize.** Rank candidates by expected impact, test cost, existing signal, and
   reversibility. Eliminate hypotheses already answered by existing evidence.
5. **Generate competing hypotheses.** Use 2-4 for normal investigations and 1-2 for
   urgent incidents. Each must identify a mechanism, falsification condition, and a
   prediction distinguishable from the alternatives.
6. **Evaluate quality.** Apply testability, falsifiability, parsimony, explanatory power,
   consistency, and evidence standards from `references/hypothesis_quality_criteria.md`.
7. **Design tests.** Specify dataset, comparison, primary metric, support/power,
   confounds, and a predeclared decision rule. Use
   `references/experimental_design_patterns.md`.
8. **Report.** Produce an executive summary, one evidence block per hypothesis,
   prediction table, and distinguishing experiments using
   `references/investigation_report_template.md`.

## Hard Rules

- Anchor every investigation in a concrete measured observation.
- Explain a mechanism; "feature X is important" is not a hypothesis.
- State a quantitative or otherwise observable falsification condition.
- Rule out data-quality and population-shift explanations before model redesign.
- Cite evidence in formal validation material; belief alone is not defensible.
- Narrow the scope before producing more than four hypotheses.
- In Databricks, write narrative in `%md`; do not use `displayHTML()`.

## References

- `references/investigation_workflow.md` - scoping, evidence synthesis, prioritization,
  hypothesis families, and prediction design.
- `references/investigation_report_template.md` - Databricks-ready report templates.
- `references/hypothesis_quality_criteria.md` - quality and falsifiability criteria.
- `references/experimental_design_patterns.md` - champion-challenger, holdout,
  backtesting, A/B, and quasi-experimental designs.
- `references/literature_search_strategies.md` - internal and external banking evidence.
