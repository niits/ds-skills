---
name: metrics-evaluation
description: Use when planning or interpreting model evaluation, comparing models, diagnosing metric failures, or deciding whether evidence supports a controlled test. Covers binary, multi-class, and multi-label classification, regression, point and probabilistic forecasting, anomaly detection, ranking and recommendation, churn prediction, lead scoring, and representation learning.
allowed-tools: Read Write Edit Bash
license: MIT; third-party notices apply
metadata:
    skill-author: ds-skills
---

# ML Metrics Evaluation

## Principle

Never evaluate a metric in isolation. Every result needs a relevant baseline, valid
evaluation design, uncertainty, and a conclusion scoped to the available evidence.

## Workflow

1. **Apply the universal protocol.** Establish the estimand, population, split, label
   maturity, support, metric implementation, baseline, operating point, and independent
   unit with `topics/core/evaluation_protocol.md`.
2. **Load one domain overlay when applicable.** Use the exact route below; do not load
   unrelated domains.
3. **Load topic guidance conditionally.** Use baselines and metric interpretation for
   calculation or interpretation; diagnosis only for weak, suspicious, or conflicting
   results; decision topics only for capacity, KPI, or value questions; reporting only
   when a formal conclusion or report is requested.
4. **Synthesize without asserting causes.** State the signal, compatible hypotheses,
   discriminating checks, supported conclusion, and primary next action.

## Routing

| Task or domain | Load |
|---|---|
| Every evaluation | `topics/core/evaluation_protocol.md` |
| Binary or multi-class classification, regression, forecasting, anomaly detection, or ranking | Relevant sections of `topics/core/baselines.md` and `topics/core/metric_interpretation.md` |
| Multi-label classification | `topics/core/baselines.md` (Multi-Label) and `topics/core/metric_interpretation.md` (Multi-Label) |
| Probabilistic or interval forecasting | `topics/core/baselines.md` (Probabilistic Forecasting) and `topics/core/metric_interpretation.md` (Probabilistic Forecasting) |
| Representation learning, embeddings, retrieval, or transfer | `domains/representation_learning.md` |
| Lead scoring | `domains/customer_analytics/lead_scoring.md` |
| Churn prediction | `domains/customer_analytics/churn_prediction.md` |
| Recommendation | `domains/recommendation.md` |

## Evidence Gate

Return `INSUFFICIENT EVIDENCE` and do not issue the requested decision conclusion when a
decision-critical item is unknown: estimand, metric or evaluator definition, evaluation
population, split validity, label maturity, support, operating point, baseline,
independent unit, or economics required for an economic claim.
List the evidence needed to resume.

This gate governs the requested decision conclusion only. Descriptive, interpretive, and
partial-evidence answers remain in scope: state what the available evidence does support,
name the missing items, and continue. Do not refuse a question you can answer with a
correctly scoped conclusion.

## Hard Rules

- Always state the baseline or explain why no universal baseline applies.
- Report evaluation `n`, positive/relevant count, and uncertainty for headline and
  decision-critical segments.
- Report precision, recall, and F1 only with their threshold; ranking metrics with `k`.
  For multi-class and multi-label, also report the averaging scheme.
- Compare models with paired uncertainty at the independent deployment unit.
- Do not compare results produced with different candidate, gallery, normalization, or
  probe protocols without a prominent protocol-difference warning.
- Separate test-sample uncertainty from variation across model-training seeds.
- Do not use vague assessments such as "decent" or "promising"; use numbers.
- Diagnose poor or suspicious metrics instead of merely describing them.
- Use a paired interval for model-minus-baseline; overlap between two marginal intervals
  is not a model-comparison test.

## Topic Index

- `topics/core/` - universal protocol, baselines, and metric semantics.
- `topics/diagnosis/checklist.md` - ordered validity and troubleshooting checks.
- `topics/diagnosis/general_patterns.md` - cross-domain hypotheses and discriminating checks.
- Domain-specific diagnostics live in the relevant file under `domains/`.
- `topics/decision/kpi_mapping.md` - decision-to-metric mapping and the causal boundary.
- `topics/decision/impact_translation.md` - capacity, counterfactual, and value translation.
- `topics/reporting/evaluation_report.md` - conclusion rules and conditional report profiles.
- `domains/` - specialized evaluation overlays grouped by application domain.
- `references/citations.md` - optional provenance; load only on request.
