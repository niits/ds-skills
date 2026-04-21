# Domain Guide: Lead Scoring

## What Lead Scoring Is Actually Solving

Lead scoring ranks prospects by likelihood to convert (buy, sign, book a demo).
The output is a prioritization list for sales — not a yes/no decision.

**This means**: the model is a ranking model. Precision@k (where k = sales capacity)
is the correct primary metric, not AP or AUC in isolation.

---

## Business Context

### The Funnel
```
Leads → MQL (Marketing Qualified) → SQL (Sales Qualified) → Opportunity → Won
         ↑ model scores here      ↑ sales works here
```

Model goal: maximize SQL conversion rate within the MQL → SQL handoff budget.

### Business KPIs to Collect Before Evaluating Any Metric

| KPI | Definition | Why It Matters |
|---|---|---|
| MQL→SQL conversion rate | SQLs / MQLs worked | Baseline precision: if sales works all leads, what % convert? |
| SQL→Opportunity rate | Opportunities / SQLs | Downstream funnel health |
| SDR capacity | Leads an SDR works per day/week | This is k in Precision@k |
| Average deal size (ACV) | Revenue per closed deal | Weights the value of each conversion |
| Sales cycle length | Days from first contact to close | Affects label availability and decay |
| CAC (Customer Acquisition Cost) | Total sales+marketing cost / customers | Break-even precision denominator |

### Break-Even Precision for Lead Scoring
```
SDR cost per lead worked = SDR_salary / (leads_per_day × working_days)
  e.g., $80k/year SDR, works 50 leads/week → $80k / (50×50) = $32/lead

Revenue per closed deal = ACV
Conversion rate of worked lead = historical MQL→SQL→Won rate = r

Break-even precision = SDR_cost_per_lead / (ACV × r)
  e.g., ACV=$10k, r=5% → P_breakeven = $32 / ($10k × 0.05) = 6.4%
  Any model with Precision@SDR_capacity > 6.4% is ROI-positive vs random
```

---

## Correct Metric Framework for Lead Scoring

### Primary: Precision@k
- k = SDR team capacity per week/month
- "Of the top k leads we hand to sales, what % convert?"
- Compare to: random baseline = historical MQL→SQL conversion rate
- Lift = Precision@k / historical_conversion_rate

### Secondary: Coverage and Score Distribution
- Do high-scored leads actually represent the full ICP (Ideal Customer Profile)?
- Does the score correlate with firmographic fit (company size, industry) rather than buying intent?

### What NOT to Report as Primary
- **AUC-ROC**: misleading when positive rate < 10%
- **F1**: requires threshold calibration; not how sales teams operate
- **Overall AP**: useful for model selection but not for business stakeholders

### Revenue-Weighted Precision@k
If deal sizes vary significantly:
```
Revenue_weighted_precision@k = Σ(ACV_i for converted leads in top k) / Σ(expected_ACV × k)
```
Catching a $100k deal is worth 10× a $10k deal.

---

## Critical Data Problems in Lead Scoring

### Problem 1: Label Bias (Selection Bias)
**This is the most important problem in lead scoring. It is structural, not fixable by better models.**

Sales teams only call leads they were given — which in most companies are either:
(a) all leads (if no prior model), or
(b) leads above the previous model's threshold (if a model existed)

If (b): **you will never observe labels for leads below the old threshold.**
A lead that would have converted, but was never called, is labeled as "not converted."
Your training data systematically underestimates the quality of low-scored leads.

**Detection**: Check if conversion rate drops sharply at the old model's threshold.
If yes → the drop is at least partially selection bias, not true quality difference.

**Mitigations**:
- Enforce random exploration: sales must work a random sample of low-scored leads (size depends on statistical power needed and business feasibility)
- Use proxy labels: website behavior, email engagement, content downloads as weak labels
- Causal estimation: use historical A/B tests on score thresholds if available

### Problem 2: Survivorship / Temporal Bias
- Labels require a full sales cycle to observe (often 30–180 days)
- Short evaluation periods will show inflated precision (only fast-close deals are labeled)
- Model trained on fast-closing deals may score differently than slow-moving enterprise deals

**Always ask**: What is the label observation window? Does it cover the full sales cycle?

### Problem 3: ICP Drift
The Ideal Customer Profile changes. A model trained on 2022 customers may not reflect
current buyers. Firmographic features (company size, industry) are especially prone to this.

**Detection**: Plot score distribution over time. Rising or falling mean score on new leads → drift.

### Problem 4: Feature Availability at Score Time
Lead scoring features fall into two categories:
- **Firmographic** (company size, industry, tech stack): available at lead creation, static
- **Behavioral** (email opens, page visits, content downloads): accumulate over time

A behavioral feature like "visited pricing page" is only meaningful if leads have had time to visit.
Scoring a day-old lead with behavioral features designed for 30-day-old leads → misleading scores.

**Always document**: Which features are available at score time? At what latency?

---

## Evaluation Protocol for Lead Scoring

### Step 1: Establish the Correct Baseline
- Baseline 1: Random — precision = historical MQL→SQL→Won rate
- Baseline 2: Rule-based (e.g., company size > 500 employees) — what does the current heuristic achieve?
- Baseline 3: Previous model (if one exists)

### Step 2: Time-Based Split — Mandatory
- Train on leads entered before date T
- Test on leads entered after T with outcomes observed
- Never random split — it leaks behavioral features across time

### Step 3: Compute Primary Metrics
```
Precision@k where k = SDR capacity
Lift@k = Precision@k / baseline_conversion_rate
Revenue@k = Σ(won_deal_ACV for top k leads)
```

### Step 4: Sanity Checks
- Score distribution by lead source: are some sources consistently over/under-valued?
- Score distribution over time: is it stable? Rising scores may indicate data drift or feature leakage.
- Score vs firmographic alignment: does high score = large company? If yes, model may be proxying ICP rather than intent.
- Feature importance: is one behavioral feature dominating? If it's "demo booked," that's near-leakage.

### Step 5: Sales Feedback Loop
Quantitative metrics alone are insufficient — the model is a tool for salespeople.
Collect structured feedback from SDRs (e.g., post-call disposition: "engaged", "not interested", "wrong contact"):
- Systematic "not interested" on high-scored leads → feature set does not capture buying intent
- Systematic "engaged but didn't convert" → model is correct but sales cycle or ICP needs review
- Note: SDR feedback is qualitative signal, not a metric. Use it to direct investigation, not to override precision@k directly.

---

## Common Failure Modes

| Symptom | Likely Cause | Check |
|---|---|---|
| Precision@k barely beats baseline | Weak features or label bias | Single-feature AUCs, check selection bias |
| Score correlates with company size | Model learned ICP not intent | Remove firmographic features, recheck AP |
| Model AP great, SDRs complain | Precision@SDR_capacity is wrong metric level | Compute Precision@actual_k, not overall AP |
| Score stable but conversion dropping | Sales cycle length changed or market shift | Check label observation window |
| New leads score very high initially | Behavioral features not yet accumulated | Check feature latency at score time |
| Sudden AP improvement | Leakage — check if "demo booked" is in features | Remove and recheck |
