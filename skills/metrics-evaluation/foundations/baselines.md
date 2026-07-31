# Baseline Formulas

## Classification

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
- Accuracy = 1 - positive_rate  ← misleading, ignore this
- AP depends on score/tie handling; report the constant-score implementation explicitly
- Recall = 0 → useless

### Prior Model / Heuristic
- If you have a previous model or rule-based system, that is the true baseline.
- Random is only a no-skill reference, not the business bar.

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

## Anomaly Detection

Anomaly detection typically has no labeled ground truth — baselines must be constructed differently.

### Unsupervised (no labels)
- **Contamination rate baseline**: If you flag top X% of scores as anomalies, the expected precision of a random flag = actual_anomaly_rate (if known from domain knowledge) or undefined (document this gap explicitly).
- **Seasonal naive baseline**: flag periods that deviate > 2 std from the same period in prior weeks/months. Many "ML" anomaly detectors fail to beat this.

### Semi-supervised / labeled evaluation
- If a labeled anomaly set exists: treat as binary classification with extreme imbalance.
  - AP_random = anomaly_rate (same as classification)
  - Evaluate with AP and Precision@k where k = analyst review capacity
- **AUC-ROC caveat**: with < 1% anomaly rate, AUC-ROC is not the right primary metric — use AP.

### No verified thresholds exist for anomaly scores
Score distributions are algorithm-specific. The only valid comparison is against the seasonal naive or domain rule baseline.

---

## Ranking (NDCG, MAP)

### Random Baseline for NDCG@k
- Depends on relevance distribution — do not assume a fixed value
- Compute empirically: shuffle scores 1000 times, report mean NDCG@k

### Popularity Baseline
- Rank by item frequency in training set
- This beats random significantly on most recommendation tasks
- If the model does not beat popularity on the predefined ranking metric, it has not
  demonstrated improvement on that metric; justify any value through other predeclared objectives.

---

## Imbalanced Data — Metric Selection

The specific positive-rate cutoffs below are directional guidance, not verified thresholds.
The underlying principle (AP over AUC-ROC for rare positives) has academic support — see `foundations/citations.md`.

| Positive Rate | Preferred Metric | Avoid |
|---|---|---|
| High (balanced) | AUC-ROC, F1 | — |
| Moderate imbalance | AUC-PR, AP, F1 | Accuracy |
| Severe imbalance | AP, Precision@k | Accuracy |
| Extreme imbalance | AP, Precision@k | Accuracy |

At < 5% positive rate: **prefer AP / AUC-PR over AUC-ROC** — not because AUC-ROC
inflates (a constant classifier always gets AUC-ROC = 0.5), but because AUC-ROC does
not reflect false discovery rate. AP changes with class prevalence and therefore captures
positive-class performance directly. Full explanation: `foundations/metric_interpretation.md`.

Common misconception to avoid: "all-negative classifier gets AUC-ROC = 0.97 on 3%
positive data." This is wrong — that 0.97 is **accuracy**, not AUC-ROC.
