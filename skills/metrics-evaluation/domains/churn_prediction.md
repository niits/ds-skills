# Domain Guide: Churn Prediction

## What Churn Prediction Is Actually Solving

Churn prediction ranks customers by risk of leaving so interventions can be targeted.
The model output drives a **campaign decision** — who to contact, with what offer, when.

**Critical distinction**:
- **Prediction** answers: who will churn?
- **Uplift** answers: who will stay if we intervene?

These are different models with different labels. Optimizing the wrong one is the
most common cause of churn campaigns with good AP but negative ROI.

---

## Label Definition — Get This Right First

Before evaluating any metric, confirm:

### What counts as "churn"?
| Definition | Problem |
|---|---|
| Subscription cancellation | Misses involuntary churn (failed payment) |
| 30-day inactivity | Too aggressive for low-frequency products |
| 90-day inactivity | Too late to intervene effectively |
| Downgrade to free tier | May be acceptable, not actual churn |

**Wrong label definition = wrong model regardless of AP.** Clarify before modeling.

### Observation Window vs Outcome Window
```
|---- observation window ----|-- gap --|---- outcome window ----|
  features computed here               churn defined here
```
- **Observation window**: period from which features are derived (e.g., last 90 days of activity)
- **Gap**: time between last feature and outcome start (e.g., 7 days — avoids using signals that co-occur with churn)
- **Outcome window**: period in which churn is defined (e.g., next 30 days)

If gap = 0: features and labels bleed into each other → leakage.
If outcome window too short: only fast churners are captured.

### Voluntary vs Involuntary Churn
- **Voluntary**: customer actively cancels or disengages — actionable with retention campaigns
- **Involuntary**: failed payment, card expired — requires different intervention (payment recovery)

Always separate these two. A model combining both learns a mix of signals.

### The Immortal Cohort Problem
Customers who signed up recently cannot be labeled as "not churned at 90 days" yet.
Including them as negatives in training inflates model performance and distorts the label distribution.

**Fix**: Only include customers who have completed the full outcome window.

---

## Business KPIs

| KPI | Definition | Why It Matters |
|---|---|---|
| Monthly/Annual churn rate | Churned customers / Active customers | Baseline positive rate for the model |
| Revenue churn (MRR churn) | Lost MRR / Total MRR | High-value churners matter more than count |
| Net Revenue Retention (NRR) | (Starting MRR + Expansion MRR − Contraction MRR − Churned MRR) / Starting MRR | Includes expansion; NRR > 100% = growth despite churn |
| LTV | Average revenue × avg customer lifetime | Denominator for campaign ROI calculation |
| Intervention conversion rate | % of contacted at-risk customers who stayed | Critical for break-even calculation |
| Campaign cost per contact | Total campaign cost / customers contacted | Break-even precision numerator |

### Break-Even Precision for Churn Campaigns
```
P_breakeven = campaign_cost_per_contact / (LTV_at_risk × intervention_conversion_rate)

e.g., LTV = $1,200, cost = $15/contact, conversion = 20%
P_breakeven = $15 / ($1,200 × 0.20) = 6.25%

At Precision@budget > 6.25%: campaign is ROI-positive
At Precision@budget < 6.25%: contacting these customers costs more than it saves
```

### MRR-Weighted Precision
Count-based precision treats a $10/month and $500/month customer equally.
Use MRR-weighted precision when LTV varies significantly:

```
MRR_weighted_precision@k =
    Σ(MRR_i for customers in top-k predictions who are true churners)
  / Σ(MRR_i for all customers in top-k predictions, churner or not)
```
Denominator = total MRR at stake if you intervene with all top-k. Numerator = MRR you actually save.

---

## Correct Metric Framework for Churn Prediction

### Primary: Precision@budget
- budget = number of contacts the retention team can handle per period
- "Of the top N customers we contact, what fraction are actually at-risk AND responsive?"
- Compare to: random outreach = baseline churn rate

### Secondary: Revenue Recall
- Of total MRR at risk, what fraction does the model identify within the contact budget?
- High revenue recall at the budget level = model prioritizes high-value churners

### Uplift Metrics (if uplift model is used)
- **AUUC (Area Under Uplift Curve)**: measures model's ability to identify customers who respond to treatment
- **Qini coefficient**: uplift equivalent of Gini — ranges 0 (random) to 1 (perfect)
- **Expected ROI at budget**: Σ(uplift_i × LTV_i − cost_i) for top k customers

### What NOT to Report
- **Overall AP**: useful internally but meaningless to business stakeholders
- **AUC-ROC**: positive rate is often 5–20%, making AUC misleading
- **F1 at default threshold**: threshold must be calibrated to contact budget, not 0.5
- **Accuracy**: always high due to imbalance, always wrong to report

---

## Prediction vs Uplift — The Critical Choice

### Prediction Model
- Label: did the customer churn? (binary)
- Learns: who is at high risk
- Problem: includes "sure churners" (who will leave regardless) and "loyal customers who had a bad month"
- Result: wastes budget on customers who can't be saved and customers who don't need saving

### Uplift Model
- Label: treatment effect — did intervention cause this customer to stay?
- Requires: **randomized experiment** with treatment (contacted) and control (not contacted) groups
- Learns: who has the highest marginal response to intervention
- Result: targets the "persuadables" — customers on the fence who respond to outreach

**When to use which:**
- No historical A/B data available → prediction model is the only option
- Historical A/B data or willingness to run holdout group → build uplift model
- Prediction AP is fine but campaign ROI is negative → switch to uplift model

### Uplift Segmentation (Simplified, No A/B Data)
Even without A/B data, segment the prediction model output:
```
High score, low engagement with past campaigns → "sure churners" (don't waste budget)
High score, high engagement with past campaigns → "persuadables" (prioritize)
Low score → "safe" (don't contact)
```

---

## Evaluation Protocol for Churn Prediction

### Step 1: Validate Label Definition
- Count: how many customers are in the outcome window? What is the churn rate?
- Separate voluntary from involuntary churn before modeling
- Verify no immortal cohort contamination

### Step 2: Time-Based Split — Mandatory
- Train: cohort entering before month T, with full outcome window observed
- Val: cohort entering month T to T+N, where N allows the full outcome window to be observed
- Test: cohort entering after that, again with full outcome window observed

**Important**: if the outcome window is 90 days, customers entering in the last 90 days of your data cannot yet be labeled. Do not include them as negatives — exclude them from training and evaluation entirely. Adjust your cutoff dates to respect this lag.

Never random split — activity features leak across time.

### Step 3: Compute Metrics in This Order
1. **Baseline churn rate** in test set (= AP_random)
2. **AP and lift** over baseline
3. **Precision@budget** where budget = retention team capacity per month
4. **MRR-weighted precision@budget** if LTV varies
5. **Revenue recall**: of total at-risk MRR, what fraction is in the top-k predictions?
6. **Break-even check**: is Precision@budget > P_breakeven?

### Step 4: Cohort Analysis
Always decompose performance by:
- **Tenure**: new customers churn for different reasons than long-tenured ones. Model should be segment-specific or features should encode tenure explicitly.
- **Product tier**: free vs paid, plan type — churn dynamics differ
- **Acquisition channel**: organic vs paid users have different retention profiles

### Step 5: Early Warning Check
A churn model is only useful if it predicts early enough to intervene.
- Plot: average days between "first high-score prediction" and actual churn date
- If lead time < intervention delivery time → model is predicting too late

---

## Common Failure Modes

| Symptom | Diagnosis | Action |
|---|---|---|
| AP good, campaign ROI negative | Contacting non-persuadables or sure churners | Switch to uplift model or segment prediction output |
| High recall, low precision at budget | Model too liberal — contacting too many low-risk customers | Tighten threshold; optimize Precision@budget specifically |
| Precision@budget barely beats baseline | Weak features or wrong label definition | Check: does churn correlate with any single feature? If no → label problem |
| Model performance degrades over time | PSI increase on feature distributions | Monitor PSI trend; trigger retraining when shift is detected |
| New customers score as high-risk immediately | Behavioral features not yet accumulated; immortal cohort contamination | Exclude customers who haven't completed the full outcome window from scoring |
| Score predicts involuntary churn well, voluntary poorly | Mixed labels | Separate label types; train separate models |
| Model catches 80% of churners but misses high-LTV segment | Model optimizes count, not revenue | Switch to MRR-weighted training loss |

---

## Monitoring After Deployment

### What to Monitor
1. **PSI on input features**: detect population shift before model degrades
2. **Score distribution**: mean and variance of scores over time
3. **Precision@budget**: track weekly — leading indicator of model decay
4. **Actual churn rate vs predicted churn rate**: calibration check
5. **Campaign conversion rate**: did customers predicted as at-risk actually respond to intervention?

### Retraining Triggers
No verified universal thresholds — define triggers based on business tolerance, then monitor:
- PSI trend on key features increasing consistently (compare to PSI at launch)
- Precision@budget declining relative to launch value
- Actual churn rate diverging from model's predicted aggregate rate
- Business definition of churn changes (always requires retraining)
