# Domain Guide: Lead Scoring

## What Lead Scoring Is Actually Solving

Lead scoring ranks prospects by likelihood to convert (buy, sign, book a demo).
The output is a prioritization list for sales — not a yes/no decision.

**This means**: the model is a ranking model. Precision@k (where k = sales capacity)
is the correct primary metric, not AP or AUC in isolation.

> For feature selection, leakage/tautology guards, and point-in-time construction in
> lead scoring, see the `feature-onboarding` skill — `domains/lead_scoring.md` (feature
> framing) and `references/leakage_and_tautology.md`. This file is about *metric choice*.

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
SDR cost per lead worked = annual_SDR_cost / (leads_per_week × working_weeks_per_year)
  e.g., $80k/year SDR, works 50 leads/week for 50 weeks → $80k / (50×50) = $32/lead

Define the positive label before writing the value equation:
  If positive = Won:
    P_breakeven = SDR_cost_per_lead / contribution_margin_per_win
  If positive = SQL:
    P_breakeven = SDR_cost_per_lead /
                  (P(win | SQL) × contribution_margin_per_win)

Do not multiply won-deal precision by the same end-to-end conversion probability a
second time. Compare expected profit with the current assignment policy, not only random.
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
Revenue@k = Σ(realized contribution margin from won leads in top k)
Expected_profit@k = Σ(P(win_i) × expected_margin_i - work_cost_i)
```
Catching a $100k deal is worth 10× a $10k deal.

---

## Critical Data Problems in Lead Scoring

### Problem 1: Label Bias (Selection Bias)
**This is the most important problem in lead scoring. It is structural, not fixable by better models.**

Sales teams only call leads they were given — which in most companies are either:
(a) all leads (if no prior model), or
(b) leads above the previous model's threshold (if a model existed)

If (b), determine whether outcomes below the threshold are unobserved, action-dependent,
or still visible through self-service conversion. Never coerce missing outcomes to negatives.

**Warning signal**: a conversion discontinuity at the old threshold can reflect
underlying risk, treatment assignment, treatment effect, or all three. It does not
identify selection bias by itself; use randomized exploration or a justified causal design.

**Mitigations**:
- Enforce random exploration: sales must work a random sample of low-scored leads (size depends on statistical power needed and business feasibility)
- Engagement proxies define a different, exposure-biased target; evaluate them separately rather than treating them as conversion-label repair
- Causal estimation: use historical A/B tests on score thresholds if available

### Problem 2: Survivorship / Temporal Bias
- Labels require a full sales cycle to observe (often 30–180 days)
- Incomplete cohorts have censored outcomes. Bias direction depends on whether unresolved
  outcomes are treated as negatives or excluded and on close-time dependence.
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
- Use chronological OOT evaluation for future deployment and group repeated accounts/people.
  Perform model selection within development data and preserve a final untouched test set.

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
