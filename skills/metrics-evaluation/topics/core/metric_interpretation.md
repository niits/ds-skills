# Metric Interpretation Guide

> **Convention key:**
> - `[Academic]` — threshold from a peer-reviewed paper or textbook
> - `[Industry]` — ML industry convention, no academic backing; use with judgment
> - `[Definitional]` — mathematically derived, not an empirical judgment
>
> Selected source provenance: `references/citations.md` - reference only, not read during normal skill use.

---

## Average Precision and PR-AUC

### Definitions and No-Skill Reference

Average precision is the step-weighted summary of a binary precision-recall curve.
Trapezoidal PR-AUC uses different interpolation and is not generally equal to AP.
Classification mAP averages per-class AP in a one-vs-rest decomposition; ranking MAP
averages per-query/user AP. These are different quantities that share an acronym — state
which one is meant. Always state positive class, averaging, interpolation, and
implementation.

Expected AP under random ranking is approximately class prevalence, subject to finite
candidate sets and tie handling. It is a reference expectation, not a floor.

There is **no universal "good AP" threshold** — interpretation always depends on the positive rate.
A useful no-skill comparison is **Lift = AP_model / positive_rate** `[Definitional]`,
alongside the current policy or prior model.

### How to Assess Lift
No verified threshold exists for "good" lift. Compare against:
1. The random-ranking expectation (approximately positive rate)
2. The current heuristic/rule-based system — the real bar
3. The previous model (if one exists) — improvement bar

Unusually large lift should increase leakage-review priority, but no fixed lift proves leakage.

### PR Curve Shape — Red Flags
- Precision drops to near-baseline at recall > 0.1: model only catches easy positives
- Jagged curve: too few positive examples in eval set — estimate is unreliable
- Perfect at low recall but collapses: likely memorizing, not generalizing

---

## AUC-ROC

### Interpretation Framework `[Academic]`

| AUC | Hosmer & Lemeshow descriptor | Discrimination only; not a shipping threshold |
|---|---|---|
| 0.5 | No discrimination | No rank discrimination |
| 0.5–0.7 | Poor discrimination | Low discrimination; utility requires policy analysis |
| 0.7–0.8 | Acceptable discrimination | Moderate discrimination; business utility unproven |
| 0.8–0.9 | Excellent discrimination | High discrimination; business utility unproven |
| > 0.9 | Outstanding discrimination | Very high discrimination; verify leakage and utility |

**Nuance on imbalanced data**: AUC-ROC does NOT inflate for imbalanced datasets — a
constant classifier always gets AUC-ROC = 0.5 regardless of class ratio. The common
claim that "AUC-ROC is inflated on imbalanced data" is imprecise.

The correct reason to prefer AP on imbalanced data: AUC-ROC summarizes sensitivity
and specificity but does not capture false discovery rate (precision). AP directly
measures the precision-recall trade-off, which is what matters when positives are rare.

---

## PSI (Population Stability Index)

### Thresholds `[Industry convention — explicitly NOT statistically justified]`

| PSI | Assessment |
|---|---|
| < 0.1 | Conventionally called small shift; does not prove model validity |
| 0.1–0.25 | Moderate shift — investigate |
| > 0.25 | Conventionally called large shift; investigate impact |

**Critical caveat**: These thresholds **have no statistical backing** — a peer-reviewed analysis found they are used "without reference to statistical type I or type II error rates" and have "no support or references in the academic world."

**What this means in practice**: PSI is a directional effect-size summary, but fixed
thresholds are arbitrary. Calibrate alerts from stable history, sample size, dependence,
multiplicity, and observed outcome/business loss; distribution tests alone do not prove harmful drift.

---

## F1 Score

- Only meaningful when threshold is chosen on validation set — not default 0.5
- Always report: which threshold was used, and on which split
- A threshold of 0.5 is valid only when probability calibration, costs, and the decision
  rule justify it; never accept it merely as a software default
- No verified absolute thresholds exist for F1. Compare with explicit always-positive,
  current-policy, heuristic, and previous-model baselines under the same operating rule;
  define any randomized-classifier score protocol before using it.

---

## Multi-Class and Multi-Label Averaging

An unqualified "precision", "recall", or "F1" is not interpretable beyond the binary case.
The averaging scheme changes both the value and the question being answered.

| Scheme | Computation | Answers | Dominated by |
|---|---|---|---|
| Micro | Pool all TP/FP/FN across classes, then compute | Overall decision quality | High-support classes |
| Macro | Compute per class, then unweighted mean | Per-class quality, equally weighted | Low-support classes |
| Weighted | Per class, mean weighted by support | Support-weighted quality | High-support classes |
| Sample (multi-label only) | Per instance, then mean | Per-instance label overlap | Instances with many labels |

- Under single-label multi-class assignment, micro precision, micro recall, micro F1, and
  accuracy are all equal `[Definitional]`. Reporting several of them is one measurement
  restated, not corroboration.
- Macro F1 is the mean of per-class F1 values, not the F1 of the mean precision and mean
  recall. The two differ; state which was computed.
- A macro figure with unreported per-class support is uninterpretable. One class at
  `n = 12` can move macro F1 by several points.
- Never compare a micro figure from one model against a macro figure from another. This
  is the most common way multi-class comparisons produce a false winner.
- Multi-label only: subset (exact-match) accuracy falls as label count grows and is
  usually far below every averaged F1 on the same model. A low subset accuracy next to a
  high micro F1 is expected, not a contradiction.

Multi-class AUC-ROC requires the same disclosure: one-vs-rest or one-vs-one, and macro or
weighted averaging. The four combinations give different numbers on the same predictions.

---

## RMSE / MAE (Regression)

### Mean Baseline

Fit the constant prediction on training targets and evaluate it on the same test rows as
the model. Compare RMSE directly or report
`RMSE_model / RMSE_train_mean_baseline`. Dividing by `std(y_test)` equals an oracle
test-mean comparison only under matching variance conventions and is not the deployable baseline.

Choose MAE, RMSE, quantile loss, or another loss from the decision cost. A complementary
error summary is often useful, but it should answer a distinct question rather than meet
an arbitrary reporting rule.

---

## MASE (Time Series Forecasting)

### Definition and Interpretation `[Academic]`

For seasonal lag `m`, MASE divides mean test absolute error by the mean in-sample
training error `|y_t - y_{t-m}|`. Both the training scale and evaluation protocol must
be stated. MASE is undefined when the training scale is zero.

| MASE | Interpretation against the training naive scale |
|---|---|
| > 1.0 | Test MAE exceeds the in-sample training naive scale |
| = 1.0 | Test MAE equals that scale |
| < 1.0 | Test MAE is below that scale |

MASE is scale-free, but it is not a direct test-set comparison with a fitted seasonal
naive forecast. Score that baseline on the same test rows before claiming the model adds
value, and compare with the best known alternative rather than an arbitrary quality threshold.

---

## Probabilistic Forecasting

### Pinball Loss and CRPS `[Definitional]`

Both are proper scoring rules: minimized in expectation by the true predictive
distribution, so a lower score cannot be obtained by distorting the forecast. Neither has
a universal "good" threshold; both are in the units of the target and must be compared
against a stated baseline on the same rows.

| Quantity | Interpretation | Required disclosure |
|---|---|---|
| Pinball loss | Weighted absolute error asymmetric about quantile `τ` | Which `τ` levels, and how they were averaged |
| CRPS | Integral of pinball loss over all `τ` | Reduces to MAE for a point forecast — do not read a CRPS/MAE comparison as a distributional gain |

Report per-quantile pinball loss, not only the average. An averaged figure can improve
while the upper tail — usually the quantile the decision depends on — gets worse.

### Interval Coverage

- PICP is only interpretable **with** interval width. Coverage alone is trivially
  satisfiable by widening the interval, so a coverage figure without width is not
  evidence.
- Compare observed coverage against the nominal level with an interval on the coverage
  estimate itself. "88% observed against 90% nominal" is not a miscalibration finding
  without knowing the number of independent units behind it.
- Report coverage by horizon. Aggregate coverage commonly hides correct short-horizon
  intervals combined with severe long-horizon undercoverage.
- Coverage and sharpness trade off. State the operating preference before evaluating,
  otherwise any result can be narrated as a success.

Point-forecast accuracy is not evidence about interval quality. A model can improve MASE
and simultaneously degrade coverage; report both when the deliverable is a distribution.

---

## NDCG@k (Ranking)

- Always state k — NDCG@10 ≠ NDCG@100 `[Definitional]`
- Beat popularity baseline before claiming value `[Industry]`
- A valid online experiment is primary causal evidence for its declared estimand and
  horizon, but does not automatically resolve long-term effects, rare harms, or guardrails

NDCG thresholds are entirely domain and dataset-specific. No universal "good NDCG" exists.

---

## Calibration

- `[Industry]` A well-ranked model (high AUC) can be badly calibrated
- Required when predicted probabilities drive decisions such as pricing, triage, or resource allocation
- Check: plot mean(actual) vs mean(predicted) in probability decile buckets — should be near diagonal
- Assess reliability curves, calibration-in-the-large, calibration slope, Brier score,
  and an explicitly defined calibration error on untouched data. If recalibration is
  needed, fit Platt/isotonic or another calibrator on separate development data and
  re-evaluate it on untouched data. A strictly increasing calibration map does not change
  ranking or the attainable precision-recall curve. Isotonic regression is non-decreasing
  rather than strictly increasing: it merges scores into ties, which leaves rank-based
  AUC and AP essentially unchanged but reduces the number of distinct operating points
  available for threshold selection.

---

Selected provenance: `references/citations.md` (reference only; not part of the normal skill workflow).
