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

Population-level no-skill PR precision equals prevalence. Finite-sample AP under uniform
random ordering is not generally prevalence; it depends on positive support and the
frozen evaluator. Use the comparator procedure in `topics/core/baselines.md`.

There is **no universal "good AP" threshold** - interpretation depends on prevalence and
the decision. `AP / positive_rate` is a population-oriented descriptive lift
`[Definitional]`, not exact finite-sample lift over random ordering. For small candidate
sets, compare against random permutations evaluated with the frozen evaluator, alongside
the current policy or prior model.

### How to Assess Lift
No verified threshold exists for "good" lift. Compare against:
1. The random-order comparator under the frozen evaluator
2. The current heuristic/rule-based system — the real bar
3. The previous model (if one exists) — improvement bar

Unusually large lift should increase leakage-review priority, but no fixed lift proves leakage.

### PR Curve Shape — Red Flags
- Precision concentrated at low recall shows that useful ranking quality may be confined
  to a small operating region; inspect capacity and segment composition.
- Jaggedness may reflect limited positive support, tied/discrete scores, weighting, or
  ordinary threshold discreteness; inspect counts, ties, and uncertainty.
- Perfect precision over a small low-recall region may reflect genuine separation,
  leakage, duplicates, or low support; audit before assigning a cause.

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

**Nuance on imbalanced data**: AUC-ROC does not inflate merely because prevalence is low.
Use `topics/core/evaluator_semantics.md` for random/constant score and tie behavior; do not
confuse score AUC with the accuracy of an all-negative hard classifier.

The correct reason to prefer AP on imbalanced data: AUC-ROC summarizes sensitivity
and specificity but does not capture false discovery rate (precision). AP directly
measures the precision-recall trade-off, which is what matters when positives are rare.

### Choosing Classification Evidence

| Decision need | Primary evidence | Usually insufficient alone |
|---|---|---|
| Rank discrimination | AUC-ROC or AP with prevalence | Accuracy |
| Rare-positive retrieval | AP plus precision/recall at capacity | Overall AUC-ROC |
| Fixed operating policy | Expected loss or constrained precision/recall | Global ranking metric |
| Calibrated probability | Log loss, Brier score, reliability | F1 |

Metric choice follows the operating decision, not a universal prevalence cutoff. AP
changes with prevalence, so avoid unqualified comparisons across populations.
Synthetic anomalies support stress testing, not outcome-validity claims.

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

- Interpretable only with the complete decision rule and positive-class definition.
- If a threshold or policy is tuned, tune it on development data and evaluate it on
  untouched data; a predeclared rule or multi-class argmax need not introduce a threshold.
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
- Hamming loss averages incorrect decisions over the instance-label matrix; it is not an
  overlap metric and can look small when absent labels dominate sparse targets.

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

Failure to beat an unconditional training-distribution comparator does not demonstrate
conditional forecast skill.

| Quantity | Interpretation | Required disclosure |
|---|---|---|
| Pinball loss | Weighted absolute error asymmetric about quantile `τ` | Which `τ` levels, and how they were averaged |
| CRPS | Integral of pinball loss over all `τ` | Reduces to MAE for a point forecast — do not read a CRPS/MAE comparison as a distributional gain |

Report per-quantile pinball loss, not only the average. An averaged figure can improve
while the upper tail — usually the quantile the decision depends on — gets worse.

### Interval Coverage

- PICP is the share of outcomes inside the declared prediction interval.
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

- NDCG measures gain concentrated toward earlier ranks under declared gain and discount
  functions. State `k` for NDCG@k; a full-list definition needs no artificial cutoff.
- Ranking MAP averages per-query AP and is distinct from classification mAP. State whether
  MAP is full-list or truncated.
- Popularity is one possible domain comparator, not a universal ranking bar.
- A valid online experiment is primary causal evidence for its declared estimand and
  horizon, but does not automatically resolve long-term effects, rare harms, or guardrails

NDCG and MAP thresholds are domain and dataset-specific. No universal "good" value
exists. Freeze their full evaluator contracts with `topics/core/evaluator_semantics.md`.

---

## Calibration

- `[Industry]` A well-ranked model (high AUC) can be badly calibrated
- Required when predicted probabilities drive decisions such as pricing, triage, or resource allocation
- Check: plot mean(actual) vs mean(predicted) in probability decile buckets — should be near diagonal
- Assess reliability curves, calibration-in-the-large, calibration slope, Brier score,
  and an explicitly defined calibration error on untouched data. If recalibration is
  needed, fit Platt/isotonic or another calibrator on separate development data and
  re-evaluate it on untouched data. Recompute ranking metrics after calibration; the
  implementation-dependent reason and tie contract live in
  `topics/core/evaluator_semantics.md`.

---

Selected provenance: `references/citations.md` (reference only; not part of the normal skill workflow).
