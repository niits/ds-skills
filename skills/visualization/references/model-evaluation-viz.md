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
- evaluation split/cohort, sample size, positive count/prevalence, and uncertainty method

**Key design decisions:**
- Plot True Positive Rate (y) vs. False Positive Rate (x) across all thresholds
- Add a diagonal random-classifier reference line (AUC = 0.500)
- Shade the area under the curve lightly for visual emphasis
- Report AUC with a confidence interval; use paired resampling when comparing models

**When to prefer Precision-Recall instead:** when prevalence, operating costs, or
top-ranked false discoveries make precision operationally important. No universal
prevalence cutoff determines this choice.

---

## 2. Precision-Recall Curve

**Use when:** Class imbalance is significant (fraud, rare defaults).
PR curves expose precision-recall trade-offs and depend on prevalence.

**Audience:** Practitioners, model committee for imbalanced problems

**Required inputs:**
- `y_true` — binary target array (0 or 1)
- `y_score` — predicted probability for the positive class
- `model_name` — label for the legend
- evaluation split/cohort, sample size, positive count/prevalence, and uncertainty method

**Key design decisions:**
- Plot Precision (y) vs. Recall (x) across all thresholds
- Add a horizontal baseline at the positive class prevalence rate (random classifier)
- If shading geometric PR area, label it as trapezoidal PR-AUC. Average Precision uses
  a step-weighted definition and is not generally identical.
- Report the chosen summary with a confidence interval and implementation; use paired uncertainty for comparisons

---

## 3. Calibration Plot — Reliability Diagram

**Use when:** Validating that predicted probabilities are trustworthy.
A model predicting PD = 20% should see ~20% actual defaults in that bucket.
Miscalibration directly distorts Expected Loss calculations.

**Audience:** Model committee and applicable governance reviewers; requirements vary by jurisdiction and policy

**Required inputs:**
- `y_true` — binary target array
- `y_prob` — predicted probabilities (0–1)
- `n_bins` — number of probability bins (typically 10)
- per-bin counts and binomial/cluster-aware intervals, or a justified smooth calibration estimate

**Key design decisions:**
- Bin observations by predicted probability; compute actual positive rate per bin
- Plot mean predicted probability (x) vs. fraction of positives (y)
- Add a perfect calibration diagonal (y = x)
- Draw per-bin intervals and counts (or a count/rug panel). Do not present sampling
  noise as meaningful deviation shading.
- Reading: above diagonal = model underestimates risk; below = model overestimates risk

---

## 4. Confusion Matrix

**Use when:** Showing classification outcomes at a specific operating threshold.
Forces explicit acknowledgment of all four outcome types.

**Audience:** Practitioners, committee (when threshold selection is discussed)

**Required inputs:**
- `y_true` — binary true labels
- `y_pred` — binary predicted labels at the chosen threshold
- `labels` — class label names (e.g. `["Non-default", "Default"]`)
- `normalize` — `None`, `"true"`, `"pred"`, or `"all"`; state the chosen threshold

**Key design decisions:**
- Label axes clearly: Predicted (columns) vs. Actual (rows)
- Annotate every cell — color alone must not carry the information
- Show raw counts alongside normalized rates so prevalence and volume remain visible

---

## 5. Feature Importance — Global

**Use when:** Communicating features associated with model output overall.
Mean absolute SHAP is an attribution summary, not a causal effect; state background
data, output scale, and correlated-feature limitations.

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
Use only when it matches applicable governance and explanation requirements; SHAP alone
is not automatically a legally sufficient subject-facing explanation.

**Audience:** Practitioners, regulator, compliance (individual decision audit)

**Required inputs:**
- `shap_values` — array of SHAP values for one observation (one value per feature)
- `feature_names` — list of feature name strings
- `feature_values` — actual feature values for this observation (for label display)
- `base_value` — model expected value E[f(x)]
- `prediction` — final model output for this observation
- background dataset and output scale (probability, margin, or log-odds)

**Key design decisions:**
- Sort features by absolute SHAP value; show top 10–12 features
- Bars to the right increase the prediction (positive SHAP); bars to the left decrease it
- The sum of all displayed and omitted contributions + base value equals the explained
  output; show an “other features” remainder when truncating
- Use two colors: one for positive contributions, one for negative

---

## 7. Lift / Gain Chart

**Use when:** Showing how much better the model is than random selection at a given
population cutoff. Common language in credit collections and marketing targeting.

**Audience:** Business stakeholders, model committee

**Required inputs:**
- `y_true` — binary target array
- `y_score` — predicted score or probability
- evaluation cohort, `n`, prevalence, weights, tie handling, and uncertainty method

**Key design decisions:**
- Sort observations by score descending; use tie-aware cutoffs and report actual cumulative population shares
- Through cumulative cutoff `k`, compute
  `cumulative_lift = cumulative_positive_share / cumulative_population_share`
- Plot lift (y) vs. decile (x); add a reference line at lift = 1.0 (random baseline)
- Annotate lift value at each decile point
- Interpretation: lift = 2.0 at decile 1 means the top 10% of scores captures 2× the positives vs. random

---

## 8. KS Curve

**Use when:** Reporting binary classifier discrimination as a single interpretable statistic
alongside its full separation curve. Standard in credit scoring and collections, where
regulators and model committees expect KS as a companion to (not a replacement for) ROC/AUC.

**Audience:** Model committee, credit risk practitioners; policy-specific for regulators

**Required inputs:**
- `y_true` — binary target array (0 = good/non-default, 1 = bad/default)
- `y_score` — predicted probability or score for the positive (bad) class
- evaluation split/cohort, sample size, positive count/prevalence, and score binning method

**Key design decisions:**
- Sort observations by score; plot the cumulative distribution of goods (y) and the cumulative
  distribution of bads (y) against cumulative population or score threshold (x) as two lines
- KS statistic = the maximum vertical distance between the two cumulative curves; mark this
  point explicitly with a vertical line or bracket and annotate the KS value and the score/decile
  at which it occurs
- Direct-label the two curves ("Goods" / "Bads") instead of a legend — this is exactly the
  "one accent, rest gray" pattern from `pre-attentive-attributes.md`: accent the bads curve
  (the discriminating line), gray the goods curve
- Report KS alongside AUC, not instead of it — KS is threshold-specific (it names *where*
  separation is greatest); AUC summarizes discrimination across all thresholds. State the
  evaluation cohort and score binning, since both shift the KS value
- Interpretation for a practitioner: KS = 0.42 means the two population distributions are 42
  percentage points apart at their point of maximum separation; higher = better discrimination.
  There is no universal "good" threshold — state your organization's internal benchmark rather
  than implying a general-purpose cutoff

---

## 9. PSI Stability Chart

**Use when:** Monitoring whether a model's score distribution (or a feature's distribution) has
drifted between a reference period (e.g. development sample) and a current period (e.g. this
month's scored population). Standard in credit model monitoring and governance reporting.

**Audience:** Model committee, risk monitoring practitioners; policy-specific for regulators

**Required inputs:**
- `expected` — reference-period distribution (score or feature), typically binned into deciles
- `actual` — current-period distribution, same binning as `expected`
- `bin_edges` or `n_bins` — must match between reference and current periods
- reporting period, reference-period definition, and population sizes for both periods

**Key design decisions:**
- Two complementary views, pick based on audience: (a) a **bar chart** of PSI-by-bin, one bar
  per score decile, showing where the distribution shifted; (b) a **trend line** of the overall
  PSI statistic computed each reporting period, showing drift over time
- For the bar-by-bin view: annotate each bin's contribution to total PSI; accent bins that
  exceed the shift threshold, gray the stable bins (again, the highlight-one/gray-rest pattern)
- For the trend-line view: add horizontal reference lines at the two conventional thresholds
  (0.10, 0.25) so the reader can see at a glance which zone the current value falls in; label the
  zones "Stable" / "Moderate shift — monitor" / "Significant shift — investigate" directly on the
  chart rather than relying on a legend
- State the binning method, the reference-period definition, and sample sizes in the caption —
  PSI is sensitive to all three, and a chart without this context invites overreading a single
  number
- Interpretation: PSI < 0.10 → stable; 0.10–0.25 → moderate shift, monitor; ≥ 0.25 → significant
  shift, investigate. These are conventional rules of thumb, not universal evidence thresholds —
  state your organization's policy value rather than presenting them as fixed law

---

## Audience Guide for Model Charts

| Chart | Executive | Committee | Regulator | Practitioner |
|---|---|---|---|---|
| ROC Curve | — | commonly used | policy-specific | useful |
| Precision-Recall | — | when operationally relevant | policy-specific | useful |
| Calibration Plot | — | when probabilities drive decisions | policy-specific | useful |
| Confusion Matrix | summary only | threshold discussions | policy-specific | useful |
| Feature Importance | simplified | commonly used | policy-specific | useful |
| SHAP Waterfall | — | selected cases | policy-specific audit | model-specific |
| Lift Chart | ✓ (business language) | ✓ | — | ✓ |
| KS Curve | — | common in credit | policy-specific | domain-specific |
| PSI Stability Chart | summary only | common in monitoring reviews | policy-specific | domain-specific |
