# Model Evaluation Visualization

Charts for diagnosing, validating, and communicating ML model performance.
Used in model development, validation documents, and committee presentations.

---

## 1. ROC Curve

**Use when:** Reporting binary classifier discrimination across all thresholds.

**Audience:** Model committee, practitioners

**Required inputs:**
- `y_true` — binary target array (0 or 1)
- `y_score` — predicted probability or score for the positive class
- `model_name` — label for the legend

**Key design decisions:**
- Plot True Positive Rate (y) vs. False Positive Rate (x) across all thresholds
- Add a diagonal random-classifier reference line (AUC = 0.500)
- Shade the area under the curve lightly for visual emphasis
- Embed AUC value in the chart title

**When to prefer Precision-Recall instead:** When the positive class is rare (< 10% of data),
ROC-AUC can look deceptively high. Use PR curve alongside ROC for fraud and low-default-rate credit models.

---

## 2. Precision-Recall Curve

**Use when:** Class imbalance is significant (fraud, rare defaults).
PR curve reflects true model quality on the minority class.

**Audience:** Practitioners, model committee for imbalanced problems

**Required inputs:**
- `y_true` — binary target array (0 or 1)
- `y_score` — predicted probability for the positive class
- `model_name` — label for the legend

**Key design decisions:**
- Plot Precision (y) vs. Recall (x) across all thresholds
- Add a horizontal baseline at the positive class prevalence rate (random classifier)
- Shade the area under the PR curve lightly
- Embed Average Precision (AP) in the chart title

---

## 3. Calibration Plot — Reliability Diagram

**Use when:** Validating that predicted probabilities are trustworthy.
A model predicting PD = 20% should see ~20% actual defaults in that bucket.
Miscalibration directly distorts Expected Loss calculations.

**Audience:** Model committee, regulator (mandatory in IRB model validation)

**Required inputs:**
- `y_true` — binary target array
- `y_prob` — predicted probabilities (0–1)
- `n_bins` — number of probability bins (typically 10)

**Key design decisions:**
- Bin observations by predicted probability; compute actual positive rate per bin
- Plot mean predicted probability (x) vs. fraction of positives (y)
- Add a perfect calibration diagonal (y = x)
- Shade the deviation between the model curve and the diagonal
- Reading: above diagonal = model underestimates risk (conservative); below = overestimates (aggressive)

---

## 4. Confusion Matrix

**Use when:** Showing classification outcomes at a specific operating threshold.
Forces explicit acknowledgment of all four outcome types.

**Audience:** Practitioners, committee (when threshold selection is discussed)

**Required inputs:**
- `y_true` — binary true labels
- `y_pred` — binary predicted labels at the chosen threshold
- `labels` — class label names (e.g. `["Non-default", "Default"]`)
- `normalize` — `True` to show row-normalized rates; `False` for raw counts

**Key design decisions:**
- Label axes clearly: Predicted (columns) vs. Actual (rows)
- Annotate every cell — color alone must not carry the information
- Row-normalized rates are easier to compare when class sizes differ

---

## 5. Feature Importance — Global

**Use when:** Communicating which features drive the model overall.
Use mean absolute SHAP values when available — more theoretically grounded than built-in importances.

**Audience:** Practitioners, model committee

**Required inputs:**
- `feature_names` — list of feature name strings
- `importances` — corresponding importance scores (e.g. mean |SHAP|)
- `top_n` — how many features to display (typically 10–15)

**Key design decisions:**
- Sort by importance descending; display top N only
- Use horizontal bar — feature names are text and need horizontal space
- Accent the top feature in the focus color; gray the rest
- Annotate values directly on the bars; remove the x-axis

---

## 6. SHAP Waterfall — Individual Prediction Explanation

**Use when:** Explaining why a specific observation received a particular prediction.
Required in regulated contexts where model decisions must be explainable to the subject.

**Audience:** Practitioners, regulator, compliance (individual decision audit)

**Required inputs:**
- `shap_values` — array of SHAP values for one observation (one value per feature)
- `feature_names` — list of feature name strings
- `feature_values` — actual feature values for this observation (for label display)
- `base_value` — model expected value E[f(x)]
- `prediction` — final model output for this observation

**Key design decisions:**
- Sort features by absolute SHAP value; show top 10–12 features
- Bars to the right increase the prediction (positive SHAP); bars to the left decrease it
- The sum of all bars + base_value = prediction (annotate both in the title/subtitle)
- Use two colors: one for positive contributions, one for negative

---

## 7. Lift / Gain Chart

**Use when:** Showing how much better the model is than random selection at a given
population cutoff. Common language in credit collections and marketing targeting.

**Audience:** Business stakeholders, model committee

**Required inputs:**
- `y_true` — binary target array
- `y_score` — predicted score or probability

**Key design decisions:**
- Sort observations by score descending; divide into deciles (10 equal groups)
- For each decile, compute cumulative lift = (% of positives captured) / (decile size / total)
- Plot lift (y) vs. decile (x); add a reference line at lift = 1.0 (random baseline)
- Annotate lift value at each decile point
- Interpretation: lift = 2.0 at decile 1 means the top 10% of scores captures 2× the positives vs. random

---

## Audience Guide for Model Charts

| Chart | Executive | Committee | Regulator | Practitioner |
|---|---|---|---|---|
| ROC Curve | — | required | required | required |
| Precision-Recall | — | for imbalanced | for fraud/rare | required |
| Calibration Plot | — | required | required (IRB) | required |
| Confusion Matrix | summary only | required | required | required |
| Feature Importance | simplified | required | required | required |
| SHAP Waterfall | — | selected cases | audit trail | required |
| Lift Chart | ✓ (business language) | ✓ | — | ✓ |
| KS Curve | — | required | required | required |
