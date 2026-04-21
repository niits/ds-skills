# Baseline Formulas

## Classification

### Random Classifier
- **AP** = positive_rate = n_positive / n_total `[Academic: Davis & Goadrich 2006, ICML; Saito & Rehmsmeier 2015, PLOS ONE]`
- **AUC-ROC** = 0.5 `[Definitional]`
- **Precision** = positive_rate (at any threshold) `[Definitional]`
- **Recall** = threshold-dependent, but AUC-PR = positive_rate

### Always-Positive Classifier
- Precision = positive_rate
- Recall = 1.0
- F1 = 2 × positive_rate / (1 + positive_rate)

### Majority Class Classifier (predict all negative)
- Accuracy = 1 - positive_rate  ← misleading, ignore this
- AP = positive_rate (same as random)
- Recall = 0 → useless

### Prior Model / Heuristic
- If you have a previous model or rule-based system, that is the true baseline.
- Random is only the floor, not the bar.

---

## Regression

### Predict Mean Baseline
- RMSE_baseline = std(y_test)
- MAE_baseline = mean(|y - mean(y)|) ≈ 0.798 × std(y) for normal distributions

### Normalized RMSE
- nRMSE = RMSE_model / std(y_test)
- nRMSE ≥ 1.0: worse than or equal to predicting the mean `[Definitional]`
- nRMSE < 1.0: better than mean prediction `[Definitional]`
- No verified thresholds below 1.0 — compare to previous model and task benchmarks

### For Time Series
- Naive baseline: predict previous value (lag-1)
- MASE (Mean Absolute Scaled Error) = MAE_model / MAE_naive — use this instead of raw MAE

**Intermittent demand guard**: If naive baseline = 0 for many periods (e.g., sparse SKUs with frequent zero demand), MAE_naive → 0 and MASE is undefined (division by zero). In this case substitute **RMSSE** (Root Mean Squared Scaled Error), which uses squared naive error in the denominator and is defined even when MAE_naive = 0.
```
RMSSE = RMSE_model / RMSE_naive
RMSE_naive = sqrt(mean((y_t - y_{t-1})²))  — always > 0 for non-constant series
```
> Reference: M5 Competition (Makridakis et al. 2022) uses RMSSE as the primary metric
> specifically because MASE is undefined for intermittent demand series.

---

## Anomaly Detection

Anomaly detection typically has no labeled ground truth — baselines must be constructed differently.

### Unsupervised (no labels)
- **Contamination rate baseline**: If you flag top X% of scores as anomalies, what is the expected precision if flags were random? = actual_anomaly_rate (if known from domain knowledge) or undefined (document this gap explicitly).
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
- If your model doesn't beat popularity, it has learned nothing useful

---

## Imbalanced Data — Metric Selection

The specific positive-rate cutoffs below are directional guidance, not verified thresholds.
The underlying principle has academic support (Saito & Rehmsmeier 2015, Davis & Goadrich 2006).

| Positive Rate | Preferred Metric | Avoid |
|---|---|---|
| High (balanced) | AUC-ROC, F1 | — |
| Moderate imbalance | AUC-PR, AP, F1 | Accuracy |
| Severe imbalance | AP, Precision@k | Accuracy |
| Extreme imbalance | AP, Precision@k | Accuracy |

At < 5% positive rate: **prefer AP / AUC-PR over AUC-ROC** — not because AUC-ROC
inflates (a constant classifier always gets AUC-ROC = 0.5), but because AUC-ROC does
not reflect false discovery rate. AP changes with class prevalence and therefore captures
positive-class performance directly.

Common misconception to avoid: "all-negative classifier gets AUC-ROC = 0.97 on 3%
positive data." This is wrong — that 0.97 is **accuracy**, not AUC-ROC.

> Sources: Richardson et al. (2024), Patterns (Cell Press) — AUC-ROC is invariant to
> class imbalance. Saito & Rehmsmeier (2015), PLOS ONE (3,594 citations) — PR/AP is
> more informative for imbalanced data because it focuses on positive-class performance.
