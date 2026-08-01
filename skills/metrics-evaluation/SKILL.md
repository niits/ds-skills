---
name: metrics-evaluation
description: Use when model evaluation numbers need an honest, baseline-anchored usability verdict. Computes relevant baselines, maps metrics to business KPIs, detects multi-metric failure patterns, and prescribes remediation for classification, regression, and ranking.
allowed-tools: Read Write Edit Bash
license: MIT; third-party notices apply
metadata:
    skill-author: ds-skills
---

# ML Metrics Evaluation

## Principle

Never evaluate a metric in isolation. Every result needs a relevant baseline, business
context, valid evaluation design, uncertainty, and a direct verdict.

## Workflow

1. **Establish context and validity.** Identify task, population, split, label maturity,
   support, positive/relevant rate, metric implementation, operating threshold or `k`,
   baseline, and business decision. Apply `foundations/evaluation_protocol.md`.
2. **Load one domain guide.** Use the matching `domains/<domain>.md`; use the generic
   workflow only when no guide applies.
3. **Compute baselines.** Compare against no-skill, constant, heuristic, previous-model,
   popularity, or time-series baselines as appropriate. Use `foundations/baselines.md`.
4. **Interpret each metric.** Define implementation, averaging/interpolation, threshold
   or `k`, and comparison basis. Use `foundations/metric_interpretation.md`.
5. **Diagnose weak or suspicious results.** Check evaluation validity, leakage, shift,
   label quality, signal, model capacity, operating point/calibration, and metric choice
   in the order defined by `diagnosis/checklist.md`.
6. **Translate to business impact.** Trace the target to a KPI, derive the operating
   requirement, and quantify TP/FP/FN or ranking impact with `business/kpi_mapping.md`
   and `business/impact_translation.md`.
7. **Synthesize across metrics.** Match train/validation/test, aggregate/segment,
   discrimination/calibration, and offline/online evidence to `diagnosis/patterns.md`.
   State the matched pattern, likely cause, and single most important next action.
8. **Issue and report one verdict.** Follow `reporting/evaluation_report.md`.

## Evidence Gate

Return `INSUFFICIENT EVIDENCE` and do not issue a shipping verdict when a
decision-critical item is unknown: metric definition, evaluation population, split
validity, label maturity, support, threshold/`k`, baseline, or required economics.
List the evidence needed to resume.

## Hard Rules

- Always state the baseline or explain why no universal baseline applies.
- Report evaluation `n`, positive/relevant count, and uncertainty for headline and
  decision-critical segments.
- Report precision, recall, and F1 only with their threshold; ranking metrics with `k`.
- Compare models with paired uncertainty at the independent deployment unit.
- Do not use vague assessments such as "decent" or "promising"; use numbers.
- Diagnose poor or suspicious metrics instead of merely describing them.
- Do not claim `Good` or `Strong` when uncertainty includes the baseline or required
  business threshold.

## References

- `foundations/evaluation_protocol.md` - context, validity, support, and uncertainty.
- `foundations/baselines.md` - baseline calculations by task.
- `foundations/metric_interpretation.md` - definitions and interpretation limits.
- `diagnosis/checklist.md` - ordered root-cause checks.
- `diagnosis/patterns.md` - multi-metric diagnostic patterns and actions.
- `business/kpi_mapping.md` - domain KPIs to ML metrics.
- `business/impact_translation.md` - model outcomes to economic impact.
- `reporting/evaluation_report.md` - verdict taxonomy and report template.
- `domains/` - lead scoring, churn, recommendation, fraud, and credit guidance.
- `foundations/citations.md` - provenance for thresholds and claims; load on request.
