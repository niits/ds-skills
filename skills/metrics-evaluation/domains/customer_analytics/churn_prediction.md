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

Gap zero is valid when features are point-in-time correct and the outcome starts after
the scoring event. Leakage occurs only when timestamps overlap or unavailable-at-decision information enters features.
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
| Conditional save probability | Incremental probability of retention among true at-risk customers | Requires identified treatment-control evidence and assumptions |
| Campaign cost per contact | Total campaign cost / customers contacted | Break-even precision numerator |

### Break-Even Precision for Churn Campaigns
```
P_breakeven = campaign_cost_per_contact / (value_at_risk × conditional_save_probability)

e.g., LTV = $1,200, cost = $15/contact, conversion = 20%
P_breakeven = $15 / ($1,200 × 0.20) = 6.25%

Use this only when the incremental save probability is supported by treatment-control
evidence. Otherwise report scenario bounds; predictive precision cannot prove campaign ROI.
```

### MRR-at-Risk Concentration
Count-based precision treats a $10/month and $500/month customer equally.
Use MRR-weighted precision when LTV varies significantly:

```
MRR_at_risk_concentration@k =
    Σ(MRR_i for customers in top-k predictions who are true churners)
  / Σ(MRR_i for all customers in top-k predictions, churner or not)
```
The numerator is MRR attached to observed churners, not MRR saved. Incremental saved
MRR requires treatment-control evidence and subtraction of offer, contact, contraction,
and cannibalization costs.

---

## Correct Metric Framework for Churn Prediction

### Primary: Precision@budget
- budget = number of contacts the retention team can handle per period
- "Of the top N customers, what fraction subsequently churn under a common, stated policy?"
- Responsiveness is not identified by a churn prediction label.
- Compare to: random outreach = baseline churn rate

### Secondary: Revenue Recall
- Of total MRR at risk, what fraction does the model identify within the contact budget?
- High revenue recall at the budget level = model prioritizes high-value churners

### Uplift Metrics (if uplift model is used)
- **AUUC (Area Under Uplift Curve)**: measures model's ability to identify customers who respond to treatment
- **Qini coefficient** *(citation: `references/citations.md`)*: state the implementation, normalization, random-policy baseline,
  and uncertainty; raw and normalized variants differ and may be negative
- **Expected ROI at budget**: Σ(uplift_i × LTV_i − cost_i) for top k customers

### Metrics That Are Insufficient as Sole Decision Evidence
- **Overall AP**: useful for model comparison but does not evaluate the contact budget by itself
- **AUC-ROC**: measures global rank discrimination but does not expose precision,
  false-positive burden, calibration, or intervention value at the operating policy
- **F1 at default threshold**: threshold must be calibrated to contact budget, not 0.5
- **Accuracy**: insufficient without prevalence, class-specific errors, costs, and a relevant baseline

---

## Prediction vs Uplift — The Critical Choice

### Prediction Model
- Label: did the customer churn? (binary)
- Learns: who is at high risk
- Problem: includes "sure churners" (who will leave regardless) and "loyal customers who had a bad month"
- Result: wastes budget on customers who can't be saved and customers who don't need saving

### Uplift Model
- Inputs: treatment assignment, observed outcome, and covariates; individual treatment
  effect is not an observed label
- Requires randomization or defensible identification assumptions plus overlap
- Estimates conditional average treatment effect/uplift and its uncertainty
- Result: targets the "persuadables" — customers on the fence who respond to outreach

**When to use which:**
- No historical A/B data available → prediction model is the only option
- Historical A/B data or willingness to run holdout group → build uplift model
- Prediction AP is fine but campaign ROI is negative → switch to uplift model

### Without Randomized Treatment Data
Do not assign causal response types such as "persuadable" or "sure churner" from risk
and historical engagement. Historical campaign engagement is treatment-selected and
confounded. Use it descriptively, then validate targeting through a randomized holdout.

---

## Evaluation Protocol for Churn Prediction

### Step 1: Validate Label Definition
- Count: how many customers are in the outcome window? What is the churn rate?
- Separate voluntary from involuntary churn before modeling
- Verify no immortal cohort contamination

### Step 2: Split for the Deployment Estimand
- Train: cohort entering before month T, with full outcome window observed
- Val: cohort entering month T to T+N, where N allows the full outcome window to be observed
- Test: cohort entering after that, again with full outcome window observed

**Important**: if the outcome window is 90 days, customers entering in the last 90 days of your data cannot yet be labeled. Do not include them as negatives — exclude them from training and evaluation entirely. Adjust your cutoff dates to respect this lag.

Use chronological evaluation for future-cohort deployment. A random split is appropriate
only for an exchangeable deployment estimand with point-in-time-correct features and no
prohibited customer overlap.

### Step 3: Compute Metrics in This Order
1. **Baseline churn rate** in an untreated or common-policy test population
2. **AP and lift** over baseline
3. **Precision@budget** where budget = retention team capacity per month
4. **MRR-weighted precision@budget** if LTV varies
5. **Revenue recall**: of total at-risk MRR, what fraction is in the top-k predictions?
6. **Economic scenario or causal check**: combine prediction with an identified
   conditional save model, or directly evaluate incremental profit/uplift from randomized data

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

| Symptom | Compatible Hypotheses | Discriminating Check |
|---|---|---|
| AP good, campaign ROI negative | Treatment heterogeneity, costs, offer design, execution, or confounding | Treat as hypotheses; use randomized or credibly identified uplift evaluation |
| High recall, low precision at budget | Capacity/cost mismatch, weak separation, threshold policy | Evaluate the frozen policy across validation-selected thresholds |
| Precision@budget barely beats baseline | Weak/conditional signal, support, policy, or label issue | Compare multivariate baselines and run a separate label audit |
| Model performance degrades over time | Population, labels, policy, pipeline, calibration, concept shift | Link drift signals to matured outcomes before retraining |
| New customers score as high-risk immediately | Feature latency, missingness, cold-start population | Reconstruct score-time features and evaluate tenure strata |
| Involuntary and voluntary outcomes differ | Mixed estimands or different mechanisms | Evaluate separate labels; separate models only if evidence supports it |
| Count recall high, value-weighted recall low | Objective weighting, different behavior, concentration, noisy value | Report both estimands and concentration before changing training |

---

## Monitoring After Deployment

### What to Monitor
1. **PSI on input features**: detect population shift before model degrades
2. **Score distribution**: mean and variance of scores over time
3. **Precision@budget under a stable/common policy**: track after labels mature
4. **Reliability by probability bin plus calibration intercept/slope**: aggregate rate alone is only calibration-in-the-large
5. **Incremental retention by targeting stratum** from a valid treatment-control design

### Retraining Triggers
No verified universal thresholds — define triggers based on business tolerance, then monitor:
- PSI trend on key features increasing consistently (compare to PSI at launch)
- Precision@budget declining relative to launch value
- Actual churn rate diverging from model's predicted aggregate rate
- Business definition of churn changes (always requires retraining)
