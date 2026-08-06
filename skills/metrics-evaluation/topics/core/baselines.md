# Baseline Formulas

## Binary Classification

The formulas in this section assume a single positive class and a single negative class.
`positive_rate` is the prevalence of the positive class. Do not apply them to multi-class
or multi-label problems; use the Multi-Class and Multi-Label sections below.

### Random Ranking Reference
- Expected PR precision and AP are approximately the positive rate under random ranking;
  finite-sample AP depends on candidate set, ties, and implementation. This is a
  no-skill expectation, not a mathematical floor.
- **AUC-ROC** = 0.5 `[Definitional]`
- **Expected precision** = positive rate under random selection
- **Recall** = operating-point dependent

### Always-Positive Classifier
- Precision = positive_rate
- Recall = 1.0
- F1 = 2 × positive_rate / (1 + positive_rate)

### Majority Class Classifier (predict all negative)
- Accuracy = 1 - positive_rate; this is informative only under stated symmetric costs
  and representative prevalence, and is insufficient without class-specific errors
- AP depends on score/tie handling; report the constant-score implementation explicitly
- Recall = 0 → useless

### Prior Model / Heuristic
- If you have a previous model or rule-based system, it is usually the primary operational baseline.
- Random is only a no-skill reference, not the business bar.

---

## Multi-Class Classification

Let `p_c` be the share of class `c` in the evaluation set, over `C` classes.

### Majority Class Classifier (predict the single most frequent class)
- Accuracy = `max_c p_c`. This is the class share itself, **not** `1 - p_c`. The binary
  shortcut `1 - positive_rate` is only correct when `C = 2` and the majority class is the
  negative one; applied to a multi-class problem it returns the wrong number.
- Macro recall = `1 / C`; macro precision and macro F1 are undefined for the `C - 1`
  classes that receive no predictions unless a zero-division convention is declared.
  State the convention (`sklearn` defaults to 0 with a warning).

### Uniform Random Classifier
- Accuracy = `1 / C`.
- Expected per-class recall = `1 / C`; expected per-class precision = `p_c`.

### Prior-Matching Random Classifier (sample class `c` with probability `p_c`)
- Accuracy = `Σ_c p_c²`. This is the correct no-skill accuracy when the classifier
  reproduces the class prior, and it exceeds `1 / C` whenever classes are imbalanced.

### Reporting requirement
- Report the averaging scheme with every multi-class metric. Micro-averaged precision,
  recall, F1, and accuracy are all identical under single-label multi-class assignment;
  reporting "micro F1" as if it were independent evidence of accuracy is a restatement,
  not a second measurement.
- Macro averaging weights every class equally regardless of support. State the per-class
  support alongside any macro figure, and mark classes below the declared minimum support
  as low-support rather than folding them into the headline.

---

## Multi-Label Classification

Each instance carries a subset of `L` labels. Per-label prevalence `p_l` varies, and the
binary formulas apply **per label**, not to the problem as a whole.

### Baselines
- **All-negative** (predict no labels): subset accuracy = share of instances with an
  empty true label set; per-label recall = 0; micro/macro F1 = 0.
- **Per-label prior**: for each label independently, use the binary baselines above with
  that label's own `p_l`. Report the vector, not a single collapsed number.
- **Label-power-set majority**: predict the most frequent label combination. Subset
  accuracy = the frequency of that combination. This is the correct baseline for exact-set
  claims and is usually far lower than any per-label figure.

### Metric selection
| Claim being made | Metric | Notes |
|---|---|---|
| Exact label set is correct | Subset (exact-match) accuracy | Harshest; drops to near zero as `L` grows |
| Overall label-decision quality | Micro-averaged precision/recall/F1 | Dominated by high-prevalence labels |
| Per-label quality treated equally | Macro-averaged precision/recall/F1 | Dominated by rare labels; report support |
| Per-instance label overlap | Sample-averaged F1, Hamming loss | Averages over instances, not labels |

### Rules
- Micro, macro, and sample averaging answer different questions and are not
  interchangeable. Report which one, and do not compare a micro figure from one model
  against a macro figure from another.
- Thresholds are per-label. A single global threshold across labels with different
  prevalence is a modeling choice that must be declared, not a default.
- Report the number of labels, per-label support, and cardinality (mean labels per
  instance). Micro F1 without per-label support hides total failure on rare labels.
- Label correlation invalidates treating per-label intervals as independent. Resample the
  instance, recompute all labels within each replicate.

---

## Regression

### Predict Mean Baseline
- Fit `c = mean(y_train)` and evaluate `RMSE(y_test, c)` and `MAE(y_test, c)`.
- Using `mean(y_test)` is an oracle test-set baseline, not a deployable predictor.

### Relative RMSE
- Prefer `RMSE_model / RMSE_train_mean_baseline` on the same evaluation rows.
- A ratio below 1 beats the deployable constant baseline; a ratio above 1 does not.

### For Time Series
- Naive baseline: predict previous value (lag-1)
- For seasonal period `m`, scale test absolute errors by the mean in-sample training
  error `mean(|y_t - y_{t-m}|)`.

**Intermittent demand guard**: If the MASE denominator is zero, MASE is undefined.
RMSSE may help for intermittent but non-constant series, but it is also undefined when
its training scaling denominator is zero:
```
RMSSE = sqrt(mean(test_error²) / mean((y_t - y_{t-m})² on training))
```
Report an unscaled error and an explicitly defined baseline when either scale is zero.

---

## Probabilistic Forecasting

Applies when the deliverable is a predictive distribution, a set of quantiles, or a
prediction interval rather than a point forecast. Point-forecast accuracy is not evidence
about interval quality, and a model can win on MASE while its intervals are badly
miscalibrated.

### Baselines
- **Empirical-residual baseline**: form intervals from the in-sample residual quantiles of
  the naive or seasonal-naive point forecast. This is the deployable no-skill interval.
- **Climatological / unconditional baseline**: quantiles of the training target
  distribution, ignoring covariates. A conditional model that does not beat this has not
  demonstrated conditional skill.
- Do not use a Gaussian interval derived from in-sample RMSE as a baseline unless
  normality and homoscedasticity have been checked; it understates tails on most demand
  and financial series.

### Scoring rules
- **Pinball (quantile) loss** at quantile level `τ`, for forecast `q` and outcome `y`:
  ```
  L_τ(q, y) = τ · max(y - q, 0) + (1 - τ) · max(q - y, 0)
  ```
  Report the quantile levels evaluated and average over them explicitly. A single averaged
  pinball number hides which tail is failing.
- **CRPS** generalizes pinball loss over all quantile levels and reduces to MAE when the
  forecast is a point mass, which makes CRPS and MAE directly comparable in units but not
  interchangeable in meaning.
- Both are proper scoring rules: they are minimized by the true predictive distribution,
  so they can be optimized directly. Interval coverage alone is not proper and can be
  gamed by widening intervals.

### Calibration
- **PICP** (prediction interval coverage probability) = share of outcomes falling inside
  the nominal interval. For a nominal 90% interval, target 90%.
- Report PICP **with** interval width (MPIW or a normalized width). Coverage without width
  is not evidence of a useful forecast: an arbitrarily wide interval achieves any coverage.
- Report coverage per horizon. Aggregate coverage routinely masks correct short-horizon
  and badly undercovered long-horizon intervals.
- Coverage is itself an estimate. Report its uncertainty at the independent unit (series or
  temporal block), not per forecast point.

---

## Anomaly Detection

Anomaly detection may be supervised, delayed-label, positive-unlabeled, event-based, or
fully unsupervised; state which setting applies before choosing a baseline.

### Unsupervised (no labels)
- **Contamination rate baseline**: If you flag top X% of scores as anomalies, the expected precision of a random flag = actual_anomaly_rate (if known from domain knowledge) or undefined (document this gap explicitly).
- **Domain rule or seasonal baseline**: reproduce the current alert budget and decision
  rule; do not assume a universal standard-deviation cutoff.

### Semi-supervised / labeled evaluation
- If a labeled anomaly set exists: treat as binary classification with extreme imbalance.
  - AP_random = anomaly_rate (same as classification)
  - Evaluate with AP and Precision@k where k = analyst review capacity
- **Operating caveat**: overall AUC-ROC is usually insufficient for a constrained alert
  queue; pair discrimination with AP, event recall, detection delay, and precision at capacity.

### No verified thresholds exist for anomaly scores
Score distributions are algorithm-specific. Compare against the current policy and
task-appropriate simple rules; synthetic anomalies are stress tests, not validity evidence.

### Point-adjustment protocol warning (time series)
Point adjustment (PA) credits every timestamp in a ground-truth anomaly segment as
detected when the model flags **any** single timestamp inside it, then scores the result
as if it were point-wise. This inflates precision, recall, and F1 by a large and
unbounded margin, and the inflation grows with segment length. Under PA, a random
detector flagging a small fraction of timestamps can score above 0.9 F1 on standard
benchmarks. A PA-adjusted F1 is not comparable to a point-wise F1 and is not evidence of
detection quality.

Required handling:
- Ask whether reported time-series anomaly results used point adjustment before accepting
  them. Many published and library-default results do, without stating it.
- If PA numbers are the only ones available, label the conclusion as protocol-dependent
  and do not compare them against point-wise or event-wise numbers.
- Prefer stating the evaluation unit explicitly instead: point-wise metrics, or event-wise
  metrics that count each ground-truth segment once (detected / missed) and report
  detection delay and false-alarm rate per unit time separately.
- Report the segment-length distribution. It determines the size of the PA distortion.

---

## Ranking (NDCG, MAP)

### Random Baseline for NDCG@k
- Depends on relevance distribution — do not assume a fixed value
- Compute empirically with seeded score shuffles. Choose enough Monte Carlo replicates
  that simulation error is negligible for the decision, and report that error.

### Popularity Baseline
- Rank by item frequency in training set
- Popularity is a common operational baseline, but whether it beats random is data-dependent.
- If the model does not beat popularity on the predefined ranking metric, it has not
  demonstrated improvement on that metric; justify any value through other predeclared objectives.

---

## Imbalanced Data — Metric Selection

Metric choice should follow the operating decision rather than a universal prevalence cutoff.

| Decision need | Primary evidence | Usually insufficient alone |
|---|---|---|
| Rank discrimination | AUC-ROC or AP with prevalence | Accuracy |
| Rare-positive retrieval | AP plus precision/recall at capacity | Overall AUC-ROC |
| Fixed operating policy | Expected loss or constrained precision/recall | Global ranking metric |
| Calibrated probability | Log loss, Brier score, reliability | F1 |

For rare positives, usually pair AP with operating-point evidence because AUC-ROC does
not reflect false discovery rate. AP changes with prevalence, so report prevalence and
avoid comparing AP across populations without accounting for the population change.

Common misconception to avoid: "all-negative classifier gets AUC-ROC = 0.97 on 3%
positive data." This is wrong — that 0.97 is **accuracy**, not AUC-ROC.
