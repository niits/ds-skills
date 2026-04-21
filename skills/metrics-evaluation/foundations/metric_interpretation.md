# Metric Interpretation Guide

> **Convention key used throughout this file:**
> - `[Academic]` — threshold from peer-reviewed paper or textbook with citation
> - `[Industry]` — banking/ML industry convention, no academic backing; use with judgment
> - `[Definitional]` — mathematically derived, not an empirical judgment

---

## Average Precision (AP / AUC-PR)

### Baseline — The Only Reliable Reference Point `[Definitional]`

AP of a random classifier = positive rate (class prevalence).

> Source: Davis & Goadrich (2006), "The Relationship Between Precision-Recall and ROC Curves", ICML.
> Also confirmed: Saito & Rehmsmeier (2015), "The Precision-Recall Plot Is More Informative than the ROC Plot", PLOS ONE.

There is **no universal "good AP" threshold** — the interpretation always depends on the positive rate.
The only valid primary benchmark is: **Lift = AP_model / positive_rate**.

### How to Assess Lift
No verified threshold exists for "good" lift. Compare against:
1. The random baseline (= positive rate) — floor
2. The current heuristic/rule-based system — the real bar
3. The previous model (if one exists) — improvement bar

A lift > 20x is the trigger threshold for a mandatory leakage check before any other conclusion.
(The 20x trigger is consistent with Pattern 7.1 in diagnosis/patterns.md. The specific number is directional — no academic source; treat as industry convention.)

### PR Curve Shape — Red Flags
- Precision drops to near-baseline at recall > 0.1: model only catches easy positives
- Jagged curve: too few positive examples in eval set — estimate is unreliable
- Perfect at low recall but collapses: likely memorizing, not generalizing

---

## AUC-ROC

### Interpretation Framework `[Academic]`

> Source: **Hosmer & Lemeshow, "Applied Logistic Regression" (2nd ed., 2000), Chapter 5.**
> Widely adopted; also referenced in Hanley & McNeil (1982), Radiology, which established the AUC concept.

| AUC | Hosmer & Lemeshow Label | Practical Assessment |
|---|---|---|
| 0.5 | No discrimination | Random — useless |
| 0.5–0.7 | Poor discrimination | Weak — barely useful |
| 0.7–0.8 | Acceptable discrimination | May work for low-stakes decisions |
| 0.8–0.9 | Excellent discrimination | Good |
| > 0.9 | Outstanding discrimination | Strong — verify no leakage |

**Nuance on imbalanced data**: AUC-ROC does NOT inflate for imbalanced datasets — a
constant classifier always gets AUC-ROC = 0.5 regardless of class ratio. The common
claim that "AUC-ROC is inflated on imbalanced data" is imprecise.

The correct reason to prefer AP on imbalanced data: AUC-ROC summarizes sensitivity
and specificity but does not capture false discovery rate (precision). AP directly
measures precision-recall trade-off, which is what matters when positives are rare.

> Richardson et al. (2024), Patterns, Cell Press: "ROC-AUC is only inflated by imbalance
> in simulations where changing imbalance changes the score distribution" — i.e., AUC-ROC
> is robust to prevalence changes for fixed classifier performance.
>
> Saito & Rehmsmeier (2015), PLOS ONE (3,594 citations): PR curve is more informative
> than ROC for imbalanced data — not because ROC inflates, but because AP captures
> positive-class performance that ROC's specificity term obscures.

---

## KS Statistic (Credit Risk)

### Interpretation `[Industry convention — no traceable academic source]`

The KS statistic measures maximum separation between score CDFs of positives and negatives.
KS = 0 → no separation. KS = 100 → perfect separation.

| KS | Assessment |
|---|---|
| < 20 | Weak model |
| 20–40 | Acceptable |
| 40–60 | Good |
| > 60 | Strong — verify no leakage |

**Source status**: These thresholds appear consistently across banking practice (SAS Institute publications, credit scoring practitioners) but are **not traceable to a specific academic textbook**. Treat as industry rule of thumb.

> Reference for KS concept in credit: Anderson (2007), "The Credit Scoring Toolkit", Oxford University Press.
> KS maximization as training objective: Yan et al. (2018), "Directly Maximizing the KS Statistic", Computational Statistics & Data Analysis.

**KS ≠ decision threshold**: Banks do not set lending cutoffs using KS. It is a validation metric only; actual thresholds are set by risk appetite and profitability.

---

## Gini Coefficient (Credit Risk)

### Relationship to AUC `[Definitional]`

Gini = 2 × AUC − 1

This is a mathematical identity, not an approximation. Gini = 0 → random. Gini = 1 → perfect.

### Thresholds `[Industry — derived from Hosmer & Lemeshow via the AUC identity]`

| Gini | Equivalent AUC | Assessment |
|---|---|---|
| < 0.4 | < 0.7 | Poor — weak discrimination |
| 0.4–0.6 | 0.7–0.8 | Acceptable |
| 0.6–0.8 | 0.8–0.9 | Good |
| > 0.8 | > 0.9 | Strong — verify no leakage |

**Source status**: The Gini thresholds themselves are industry convention. However, because Gini = 2×AUC−1, they inherit the Hosmer & Lemeshow academic grounding indirectly.

> Industry reference: Siddiqi (2006), "Credit Risk Scorecards", Wiley. Gini/Somers' D used as primary scorecard validation metric.

---

## PSI (Population Stability Index)

### Thresholds `[Industry convention — explicitly NOT statistically justified]`

| PSI | Assessment |
|---|---|
| < 0.1 | Stable — model still valid |
| 0.1–0.25 | Moderate shift — investigate |
| > 0.25 | Significant shift — model likely invalid |

**Critical caveat**: These thresholds **have no statistical backing**.

> Source: Yurdakul (2018), "Statistical Properties of the Population Stability Index", Journal of Risk Model Validation (peer-reviewed). Explicitly states the 0.1/0.25 thresholds are "used without reference to statistical type I or type II error rates" and "do not have any support or references in the academic world."

**What this means in practice**: PSI is a useful directional signal, but the specific thresholds 0.1 and 0.25 are arbitrary. For rigorous monitoring, supplement PSI with chi-square tests or KS tests on score distributions with proper significance levels.

---

## F1 Score

- Only meaningful when threshold is chosen on validation set — not default 0.5
- Always report: which threshold was used, and on which split
- F1 at 0.5 threshold on imbalanced data is almost always wrong

No verified absolute thresholds exist for F1. Always compare to:
- F1 of the random baseline at the same threshold
- F1 of the current heuristic or previous model

There is no universal "good F1" value — it is entirely domain and threshold-dependent.

---

## RMSE / MAE (Regression)

### Normalized RMSE

nRMSE = RMSE / std(y_test)

| nRMSE | Assessment | Source |
|---|---|---|
| ≥ 1.0 | Worse than predicting the mean — model adds no value | `[Definitional]` RMSE of mean predictor = std(y) |
| < 1.0 | Better than mean prediction | `[Definitional]` |

No verified thresholds exist for what constitutes "weak", "moderate", or "good" nRMSE below 1.0.
Compare against: mean-prediction baseline, previous model, and best known benchmark for the task.

Always report MAE alongside RMSE — RMSE is dominated by large errors, MAE is more robust to outliers.

---

## MASE (Time Series Forecasting)

### Definition and Interpretation `[Academic]`

> Source: **Hyndman & Koehler (2006), "Another Look at Measures of Forecast Accuracy", International Journal of Forecasting, 22(4), 679–688.**

MASE = MAE_model / MAE_naive

Where naive = lag-1 (random walk) forecast on training data.

| MASE | Interpretation |
|---|---|
| > 1.0 | Worse than naive forecast `[Definitional]` — model adds no value |
| = 1.0 | Same as naive |
| < 1.0 | Better than naive |

**What constitutes "good" MASE**: Hyndman & Koehler do not specify thresholds below 1.0. The literature has no consensus on what MASE value is "adequate" vs "good" — it is domain-dependent. The only defensible statement is: **MASE must be < 1.0 to justify using the model at all**. Beyond that, compare to the best known alternative model, not to an arbitrary threshold.

---

## NDCG@k (Ranking)

| Guideline | Source |
|---|---|
| Always state k — NDCG@10 ≠ NDCG@100 | `[Definitional]` |
| Beat popularity baseline before claiming value | `[Industry]` |
| Online A/B test overrides offline NDCG | `[Industry — well established in practice]` |

**Source status**: NDCG thresholds are entirely domain and dataset-specific. No universal "good NDCG" exists.

> Original NDCG definition: Järvelin & Kekäläinen (2002), "Cumulated Gain-Based Evaluation of IR Techniques", ACM TOIS.

---

## Calibration

- `[Industry]` A well-ranked model (high AUC) can be badly calibrated
- Required when predicted probabilities drive decisions: credit scoring, pricing, insurance
- Check: plot mean(actual) vs mean(predicted) in probability decile buckets — should be near diagonal
- Fix: Platt scaling (logistic regression on scores) or isotonic regression

> Reference on calibration assessment: Niculescu-Mizil & Caruana (2005), "Predicting Good Probabilities with Supervised Learning", ICML.

---

## Source Index

| Source | What It Justifies | Quality Signal |
|---|---|---|
| Hosmer & Lemeshow, "Applied Logistic Regression" (2000) | AUC-ROC thresholds (0.7 / 0.8 / 0.9) | Standard textbook, widely adopted |
| Hanley & McNeil (1982), Radiology | AUC concept and interpretation | Foundational paper |
| Hyndman & Koehler (2006), Int'l J. of Forecasting | MASE definition and MASE < 1 baseline | Peer-reviewed, widely cited |
| Davis & Goadrich (2006), ICML | AP/AUPRC baseline = positive rate | 4,071 citations (Semantic Scholar) |
| Saito & Rehmsmeier (2015), PLOS ONE | AP more informative than AUC for imbalanced data (not that AUC inflates) | 3,594 citations |
| Richardson et al. (2024), Patterns (Cell Press) | AUC-ROC is robust to class imbalance (doesn't inflate) | Peer-reviewed, Cell Press journal |
| Yurdakul (2018), J. of Risk Model Validation | PSI thresholds are not statistically justified | Peer-reviewed |
| Siddiqi (2006/2017), Wiley | Gini/KS in credit scorecard validation | Industry standard textbook |
| Järvelin & Kekäläinen (2002), ACM TOIS | NDCG definition | Foundational paper |
| Niculescu-Mizil & Caruana (2005), ICML | Calibration assessment | ICML, top-tier venue |
| Anderson (2007), Oxford University Press | KS in credit scoring context | Industry reference |
| Radcliffe (2007) | Qini coefficient, uplift segments (persuadables/sure things/lost causes) | Industry reference, widely adopted |
| Joachims, Swaminathan & Schnabel (2017), WSDM | IPS for unbiased learning-to-rank | WSDM top-tier venue, foundational |
