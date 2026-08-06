# KPI to Metric Mapping

## Purpose

Use this topic only when the request concerns an operating policy, capacity, KPI, or
value decision. Domain guides own domain-specific KPI definitions and examples.

## Mapping Procedure

1. Define the action, action unit, eligible population, timing, and counterfactual policy.
2. Define the KPI numerator, denominator, attribution horizon, and aggregation weights.
3. Identify the model output that changes the action: probability, score, rank, set,
   sequence, forecast, or embedding.
4. Derive the operating constraint: threshold, capacity `k`, false-positive budget,
   latency, coverage, service level, or resource limit.
5. Select the metric at that operating point and a complementary metric for material
   failure modes. Do not derive value from a global metric alone.
6. Compare the complete policy with the current policy on identical eligible units.
7. Quantify uncertainty in predictions, action effects, costs, and KPI attribution.

## Generic Mapping Patterns

| Decision pattern | Primary evidence | Complementary evidence |
|---|---|---|
| Fixed review or contact capacity | Precision/recall/value at `k` | AP, segment support, throughput |
| False-positive constraint | Recall at fixed FPR or false positives per unit | Precision, calibration, harms |
| Ranked interface | NDCG/Recall/Precision at visible `k` | Coverage, diversity, valid online effect |
| Asymmetric forecast cost | Pinball loss at the decision-relevant quantile, or expected cost under declared loss | Bias, coverage, naive baseline |
| Planning under forecast uncertainty | Interval coverage with width, per horizon | Point accuracy alone, aggregate coverage |
| Abstention or human review | Risk-coverage and quality at review capacity | Calibration and segment coverage |
| Multi-label tagging | Per-label precision/recall at per-label thresholds | A single micro F1, macro figures without support |

## Causal Boundary

Predictive precision, recall, or ranking quality describes outcomes under an observed
policy. Incremental KPI value additionally requires a randomized experiment or defensible
causal assumptions about treatment, exposure, uptake, interference, and counterfactual
outcomes. Without that evidence, report scenario bounds rather than causal ROI.

## Alignment Red Flags

- Model metrics improve while a valid KPI estimate does not: test metric, policy,
  implementation, and experiment hypotheses separately.
- KPI improves while model metrics do not: investigate other simultaneous changes and
  attribution before assigning the impact to the model.
- A stakeholder supplies an absolute ML target without a policy derivation: trace it back
  to capacity, harms, costs, and the current-policy baseline.
