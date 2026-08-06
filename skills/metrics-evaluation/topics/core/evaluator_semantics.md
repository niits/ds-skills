# Evaluator Semantics

## Freeze the Evaluator

Load this file when calculating, reproducing, auditing, or comparing a result whose value
depends on evaluator choices. Freeze and report:

- Prediction representation: hard label, score, probability, ranked list, point/event
  alert, point forecast, quantile, interval, or predictive distribution.
- Library and version or complete formula, score orientation, evaluated labels, weighting,
  averaging, interpolation, ties, undefined cases, and cutoff when applicable.
- Evaluation population, candidate filtering, query grouping, relevance definition, and
  the relationship between model output and the reported metric.

Follow `topics/core/evaluation_protocol.md` for paired resampling, complete-evaluator
recomputation, and the boundary between frozen test-sample uncertainty and outer-loop
pipeline variability.

## Classification and Score Metrics

Hard-decision metrics require the full rule: direct labels, threshold, argmax, abstention,
per-label thresholds, or capacity policy. AP and ROC AUC require scores or an explicitly
declared representation of hard outputs as tied score levels.

- **AP:** state the positive class, sample weights, and AP definition. Step-weighted
  average precision is not trapezoidal area under the empirical precision-recall curve;
  name trapezoidal PR-AUC separately.
- **Ties:** declare threshold grouping or another tie policy. Do not use accidental input
  order as an undocumented tie break. A constant score is not a random tie-free ordering.
- **ROC AUC:** state score direction and tie credit. Under the standard pairwise definition,
  tied positive-negative pairs receive half credit. ROC AUC is unsupported when only one
  class is observed, even if software emits a sentinel.
- **Undefined components:** state the explicit label set, averaging, and `zero_division`
  behavior. Count absent, omitted, or undefined class, label, and sample components; do not
  silently drop them from macro or sample averages.
- **Multi-class:** state one-vs-rest or one-vs-one decomposition for AUC and every averaging
  scheme. Under single-label assignment, micro precision, recall, F1, and accuracy coincide.
- **Multi-label:** state per-label thresholds, empty-set behavior, cardinality, and
  micro/macro/weighted/sample averaging. Resample instances, not labels independently.

Finite-list random-order AP depends on candidate count, positive count, and the AP
definition. Evaluate tie-free random permutations with this same frozen contract instead
of using prevalence as an exact finite-sample value. Evaluate random tied scores as a
separate comparator under the declared tie policy.

## Ranked Lists and Retrieval

Freeze query population and weighting, eligible candidates, candidate generation, catalog
snapshot, relevance judgments and gains, unjudged-item policy, duplicate/self-match
handling, exact versus approximate retrieval, score direction, ties, and full-list versus
sampled-candidate evaluation. State `k` only for metrics defined or truncated at `k`.

For **NDCG**, declare the gain transformation, discount, `k` when truncated, IDCG
construction and relevance universe, behavior when `IDCG = 0`, short-list behavior, ties,
and query aggregation. Report candidate recall separately when NDCG is conditional on a
candidate generator.

For ranking **AP/MAP**, declare binary or thresholded relevance, per-query AP convention,
denominator, optional truncation, ties, candidate set, query weighting, and treatment of
queries with no valid positives. Ranking MAP averages per-query AP; classification mAP
averages classwise one-vs-rest AP and is a different quantity.

For ranker-only comparisons, score all rankers on identical candidates. When candidate
generation is part of the compared system, keep the query population, eligible universe,
snapshot, and judgment policy common, then separate candidate recall from conditional
ranking quality.

## Calibration and Probabilistic Outputs

A strictly increasing transformation preserves score ordering and rank metrics. Isotonic
calibration is only non-decreasing and may merge scores into ties. Those ties can change
AP, ROC AUC, and available operating points. Recompute all metrics after calibration with
the declared tie policy.

For probabilistic forecasts, freeze quantile levels and aggregation, pinball-loss
convention, CRPS implementation, interval endpoint inclusion, nominal coverage, interval
width definition, per-horizon weighting, and handling of missing or crossed quantiles.
Coverage uncertainty uses the independent series or temporal block, not each forecast
point as if independent.

For quantile level `tau`, forecast `q`, and outcome `y`, declare pinball loss as:

```text
L_tau(q, y) = tau * max(y - q, 0) + (1 - tau) * max(q - y, 0)
```

For point forecasts at seasonal lag `m`, MASE and RMSSE use in-sample training scales;
`RMSSE = sqrt(mean(test_error^2) / mean((y_t - y_{t-m})^2))`. Either metric is undefined
when its training denominator is zero; report an unscaled error and comparator instead.

## Time-Series Anomaly Evaluation

Keep score ranking, thresholded point alerts, and event detection separate. Event
evaluation must declare event matching, overlap, detection windows, duplicate alerts,
detection delay, and false-alarm denominator.

Point adjustment credits an entire ground-truth segment after one detection and is not
comparable with point-wise or event-wise evaluation. It can inflate bounded precision,
recall, and F1 across nearly their full range. Absolute increase is bounded by the metric's
`[0, 1]` range; relative inflation may be arbitrarily large when the unadjusted score
approaches zero.

If point adjustment is used, label the metric as protocol-dependent, state the exact
variant, and report segment-length distribution. Prefer point-wise metrics or event-wise
metrics that count each event once, together with detection delay and false alarms per
unit time.
