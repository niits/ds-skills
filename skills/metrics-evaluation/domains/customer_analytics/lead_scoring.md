# Domain Guide: Lead Scoring

## What Lead Scoring Is Actually Solving

Lead scoring ranks prospects by likelihood to convert (buy, sign, book a demo).
The output is a prioritization list for sales — not a yes/no decision.

**This means**: the model is a ranking model. Precision@k (where k = sales capacity)
is the correct primary metric, not AP or AUC in isolation.

> This file covers evaluation. Route feature admissibility and feature construction to
> the `feature-onboarding` skill by name. Independently verify prediction cutoffs,
> point-in-time availability, aggregation windows, embargoes, and target-proxy tautology.

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

### Metrics That Are Insufficient as the Sole Primary Evidence
- **AUC-ROC**: measures global rank discrimination but does not expose precision or
  false-positive burden at sales capacity; pair it with AP and operating-point metrics
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

### Problem 1: Action-Dependent or Selectively Observed Labels

This is a high-priority validity risk when historical actions determine which outcomes
are observed. Better predictive models alone cannot identify missing counterfactual outcomes.

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

**Check**: Plot score and feature distributions over time. A changing mean is a shift
signal, not proof of harmful drift; link it to matured outcomes and policy changes.

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

### Step 2: Split for the Deployment Estimand
- Train on leads entered before date T
- Test on leads entered after T with outcomes observed
- Use chronological out-of-time evaluation for future deployment and group repeated accounts/people.
  Perform model selection within development data and preserve a final untouched test set.

### Step 3: Compute Primary Metrics
```
Precision@k where k = SDR capacity
Lift@k = Precision@k / baseline_conversion_rate
Revenue@k = Σ(won_deal_ACV for top k leads)
```

### Step 4: Sanity Checks
- Score distribution by lead source: are some sources consistently over/under-valued?
- Score distribution over time: is it stable? Rising scores can reflect population,
  policy, feature, or pipeline changes; distinguish them before assigning a cause.
- Score vs firmographic alignment: does high score track company size? If yes, test
  within-segment lift, coverage, selection policy, and ablations before claiming proxy use.
- Feature importance: is one behavioral feature dominating? If it's "demo booked," that's near-leakage.

### Step 5: Sales Feedback Loop
Quantitative metrics alone are insufficient — the model is a tool for salespeople.
Collect structured feedback from SDRs (e.g., post-call disposition: "engaged", "not interested", "wrong contact"):
- Systematic "not interested" on high-scored leads suggests checking operating-point
  precision, label alignment, timing, and feature coverage.
- Systematic "engaged but didn't convert" suggests checking horizon, downstream policy,
  sales-cycle maturity, and whether the target matches the desired action.
- Note: SDR feedback is qualitative signal, not a metric. Use it to direct investigation, not to override precision@k directly.

---

## Common Failure Modes

| Symptom | Compatible Hypotheses | Discriminating Check |
|---|---|---|
| Precision@k barely beats baseline | Weak signal, support, labels, policy selection | Compare paired multivariate baselines; audit labels and historical actions |
| Score correlates with company size | Genuine conditional signal, selection, proxy use, coverage differences | Evaluate within tiers and run held-out ablations |
| AP improves but sales feedback is poor | Operating-region mismatch, target mismatch, feedback sampling | Evaluate Precision@actual_k and structured outcomes |
| Score stable but conversion drops | Label maturity, policy change, market shift, implementation | Check horizon, exposure, pipeline, and matured outcomes |
| New leads score very high | Feature latency, missingness encoding, population change | Reconstruct features at score time and stratify by age |
| Sudden AP improvement | Leakage, changed cohort, label process, genuine gain | Replay one pipeline, audit provenance, and test an independent cohort |
