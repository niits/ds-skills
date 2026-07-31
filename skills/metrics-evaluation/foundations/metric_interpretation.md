# Metric Interpretation Guide

> **Convention key:**
> - `[Academic]` — threshold from a peer-reviewed paper or textbook
> - `[Industry]` — banking/ML industry convention, no academic backing; use with judgment
> - `[Definitional]` — mathematically derived, not an empirical judgment
>
> Full citation details (authors, venues, quotes): `foundations/citations.md` — reference only, not read during normal skill use.

---

## Average Precision and PR-AUC

### Definitions and No-Skill Reference

Average precision is the step-weighted summary of a binary precision-recall curve.
Trapezoidal PR-AUC uses different interpolation and is not generally equal to AP.
Classification mAP averages AP across classes; ranking MAP averages per-query/user AP.
Always state positive class, averaging, interpolation, and implementation.

Expected AP under random ranking is approximately class prevalence, subject to finite
candidate sets and tie handling. It is a reference expectation, not a floor.

There is **no universal "good AP" threshold** — interpretation always depends on the positive rate.
A useful no-skill comparison is **Lift = AP_model / positive_rate**, alongside the
current policy or prior model.

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

## KS Statistic (Credit Risk)

### Interpretation `[Industry convention — no traceable academic source]`

The KS statistic measures maximum separation between score CDFs of positives and negatives.
This skill reports `KS% = 100 × max(TPR - FPR)`: 0 means no separation and 100 means
perfect separation. State score orientation before computing KS/Gini.

| KS | Assessment |
|---|---|
| < 20 | Conventionally called weak separation |
| 20–40 | Conventionally called acceptable |
| 40–60 | Conventionally called good |
| > 60 | Conventionally called strong separation; verify leakage and utility |

**Source status**: These thresholds appear consistently across banking practice but are **not traceable to a specific academic textbook**. Treat as industry rule of thumb.

**KS ≠ decision threshold**: Banks do not set lending cutoffs using KS. It is a validation metric only; actual thresholds are set by risk appetite and profitability.

---

## Gini Coefficient (Credit Risk)

### Relationship to AUC `[Definitional]`

Gini = 2 × AUC − 1

This is a mathematical identity, not an approximation. Gini = 0 → random. Gini = 1 → perfect.

### Thresholds `[Industry]`

| Gini | Equivalent AUC | Assessment |
|---|---|---|
| < 0.4 | < 0.7 | Poor — weak discrimination |
| 0.4–0.6 | 0.7–0.8 | Acceptable |
| 0.6–0.8 | 0.8–0.9 | Good |
| > 0.8 | > 0.9 | Strong — verify no leakage |

**Source status**: Gini shares AUC's math identity, but its practitioner cutoffs come from Siddiqi-style industry norms, not from Hosmer & Lemeshow — the algebraic link to AUC does not transfer H&L's academic grounding to these specific cutoffs.

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
- F1 at 0.5 threshold on imbalanced data is almost always wrong
- No verified absolute thresholds exist for F1. Compare with explicit always-positive,
  current-policy, heuristic, and previous-model baselines under the same operating rule;
  define any randomized-classifier score protocol before using it.

---

## RMSE / MAE (Regression)

### Mean Baseline

Fit the constant prediction on training targets and evaluate it on the same test rows as
the model. Compare RMSE directly or report
`RMSE_model / RMSE_train_mean_baseline`. Dividing by `std(y_test)` equals an oracle
test-mean comparison only under matching variance conventions and is not the deployable baseline.

Always report MAE alongside RMSE — RMSE is dominated by large errors, MAE is more robust to outliers.

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

## NDCG@k (Ranking)

- Always state k — NDCG@10 ≠ NDCG@100 `[Definitional]`
- Beat popularity baseline before claiming value `[Industry]`
- Online A/B test overrides offline NDCG `[Industry — well established in practice]`

NDCG thresholds are entirely domain and dataset-specific. No universal "good NDCG" exists.

---

## Calibration

- `[Industry]` A well-ranked model (high AUC) can be badly calibrated
- Required when predicted probabilities drive decisions: credit scoring, pricing, insurance
- Check: plot mean(actual) vs mean(predicted) in probability decile buckets — should be near diagonal
- Assess reliability curves, calibration-in-the-large, calibration slope, Brier score,
  and an explicitly defined calibration error on untouched data. If recalibration is
  needed, fit Platt/isotonic or another calibrator on separate development data and
  re-evaluate it on untouched data. Monotone calibration does not improve ranking or
  the attainable precision-recall curve.

---

Full source list, direct quotes, and citation counts: `foundations/citations.md` (reference only — not part of the normal skill workflow).
