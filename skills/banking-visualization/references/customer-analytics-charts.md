# Customer Analytics Chart Patterns

Visualization patterns for customer segmentation, churn, lifetime value,
product funnel, and campaign analytics.

Audience in customer analytics tends to split between:
- **Product / marketing team** — funnel performance, campaign results, feature adoption
- **CRM / retention team** — churn risk, segment profiles, CLV distribution
- **Management** — cohort health, NPS trend, active user KPIs

---

## 1. Cohort Retention Heatmap

**Use when:** Tracking how different customer cohorts retain over time.
The most compact and information-dense view of retention across many cohorts simultaneously.

**Audience:** Product team, CRM, management

**Required inputs:**
- `retention_df` — DataFrame where:
  - index = cohort label (e.g. acquisition month "2023-01")
  - columns = period number since acquisition (M0, M1, M2, … MN)
  - values = retention rate (0–100); cells where the cohort hasn't reached that period should be `NaN`

**Key design decisions:**
- Mask `NaN` cells so they appear blank, not as zeros
- Use a sequential blue colormap from light (low retention) to dark (high retention)
- Annotate every non-masked cell with its value
- The triangular blank region in the top-right corner is expected — recent cohorts have fewer observations

**What to look for:**
- Steep drop at M1 → onboarding problem
- Flat retention after M3 → loyal core identified
- A cohort row that diverges downward → external event or product change impact

---

## 2. Conversion Funnel

**Use when:** Showing drop-off through a sequential process (onboarding, application,
product activation, purchase flow).

**Audience:** Product team, digital channel

**Required inputs:**
- `stages` — ordered list of stage names, top to bottom (e.g. `["Visit", "Register", "KYC", "First transaction"]`)
- `counts` — count of users reaching each stage (same order; monotonically decreasing)

**Key design decisions:**
- Center-align bars horizontally (not left-aligned) to create the funnel shape
- Normalize bar width to the first stage so each bar's width = count / count[0]
- Annotate each stage with its count
- Annotate the drop-off percentage between consecutive stages on the right side
- Accent the top stage; use gray for subsequent stages to focus attention on the drop-offs

---

## 3. RFM Segment Profile — Small Multiples Bar

**Use when:** Showing the characteristic profile of customer segments identified
by RFM (Recency, Frequency, Monetary) or any other clustering method.

Prefer small multiples bar charts over radar/spider charts.
Radar charts make comparison between segments difficult because area is hard to decode
and the shape changes with axis ordering.

**Audience:** CRM team, marketing

**Required inputs:**
- `segment_df` — DataFrame where:
  - index = segment names
  - columns = metric names (e.g. "Avg Recency", "Avg Frequency", "Avg Spend")
  - values = normalized metric scores (z-score or 0–100 scale so metrics are comparable across different units)
- `metrics` — list of metric column names to display

**Key design decisions:**
- One mini bar chart per metric (small multiples layout, shared y-axis for segment labels)
- Accent the highest-value bar in each panel; gray the others
- Sort segments consistently across all panels (e.g. by overall value tier)
- Annotate values directly on bars; remove x-axis

---

## 4. Churn Risk Distribution

**Use when:** Presenting the output of a churn model — showing how predicted churn
probability distributes across the active customer base.

**Audience:** CRM team, retention operations

**Required inputs:**
- `churn_probs` — array of predicted churn probabilities (0–1) for all active customers
- `risk_bands` *(optional)* — list of upper-bound thresholds defining risk tiers
  (e.g. `[0.3, 0.6, 1.0]` → Low / Medium / High)

**Key design decisions:**
- Histogram of churn probabilities; color bars by risk band (blue / amber / red)
- Draw vertical dividers at band boundaries
- Annotate each band with: band label, customer count, and % of total portfolio
- This tells the retention team how large each intervention target group is

---

## 5. Customer Lifetime Value — Distribution by Segment

**Use when:** Comparing CLV distributions across segments to inform acquisition
budget allocation or retention prioritization.

**Audience:** CRM, marketing, finance

**Required inputs:**
- `clv_by_segment` — dictionary mapping segment name → array of CLV values
  (e.g. `{"Premium": [...], "Standard": [...], "At-risk": [...]}`)

**Key design decisions:**
- Use horizontal box plots — segments are categorical labels that need horizontal space
- Sort segments by median CLV descending (highest median at top)
- Accent the highest-value segment; gray the others
- Suppress outlier dots (use `showfliers=False`) to avoid chart clutter; the box and whiskers convey the distribution shape
- Use a light horizontal grid; remove the y-axis spine

---

## 6. A/B Test Result — Effect Size with Confidence Interval

**Use when:** Communicating the result of a campaign or product A/B test.
Never show only the point estimate — always show the confidence interval.
The interval communicates whether the result is practically significant, not just statistically.

**Audience:** Product team, marketing, management

**Required inputs:**
- `metric_names` — list of metric labels being tested (e.g. `["Activation rate", "D7 retention", "Revenue/user"]`)
- `control_means` — list of control group mean values
- `treatment_means` — list of treatment group mean values
- `control_cis` — list of `(lower, upper)` 95% CI tuples for control
- `treatment_cis` — list of `(lower, upper)` 95% CI tuples for treatment

**Key design decisions:**
- Display control and treatment as separate dot-and-whisker rows per metric
- Color the treatment point green if the CI excludes zero lift on the positive side; red if negative; amber if the CI crosses zero (inconclusive)
- Add a vertical reference line at zero lift
- State sample size and test duration in the chart title or subtitle

**Critical rule:** Always show confidence intervals. A chart showing only means with no uncertainty band makes every experiment look conclusive — it is not.

---

## Audience Guide

| Chart | Product | CRM / Retention | Marketing | Management |
|---|---|---|---|---|
| Cohort retention heatmap | required | required | ✓ | summary row only |
| Conversion funnel | required | — | ✓ | ✓ (top-level) |
| Segment profile (small multiples) | ✓ | required | required | — |
| Churn distribution | — | required | ✓ | count by tier |
| CLV by segment | — | required | required | summary only |
| A/B test result | required | ✓ | required | lift + significance only |
