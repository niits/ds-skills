# Credit and Risk Analytics Chart Patterns

Chart patterns for credit risk, portfolio monitoring, and fraud analytics.
Complements `chart-selection.md` with domain-specific templates.

---

## 1. Score Distribution — Discriminant Overlay

**Use when:** Presenting classifier or scorecard output. Shows separation between target classes.

**Audience:** Model committee, practitioners

**Required inputs:**
- `scores_neg` — array of model scores for the negative class (e.g. non-default)
- `scores_pos` — array of model scores for the positive class (e.g. default)
- `threshold` *(optional)* — cut-off score value to annotate on the chart

**Key design decisions:**
- Overlay kernel density estimates (KDE) for each class with fill; two colors, one per class
- If a threshold is provided, mark it with a vertical dashed line
- Annotate KS statistic and Gini in the title or subtitle; visual separation proxies discrimination quality

---

## 2. KS Curve — Kolmogorov-Smirnov

**Use when:** Reporting model discrimination in validation or committee review.
Shows how quickly the model captures the positive class as the threshold is lowered.

**Audience:** Model committee, regulator

**Required inputs:**
- `y_true` — binary target array (0 = negative class, 1 = positive class)
- `y_score` — model predicted score or probability for each observation

**Key design decisions:**
- Sort observations by score descending; compute cumulative % of each class captured
- Plot cumulative % of positives and negatives vs. % of population on the same axes
- Add a random diagonal reference line
- Annotate the KS statistic with a vertical bracket at the point of maximum separation
- Embed KS value in the chart title

---

## 3. Vintage Curve — Cohort Performance

**Use when:** Tracking how origination cohorts perform over their lifetime.
Standard view for portfolio quality monitoring.

**Audience:** Risk committee, portfolio managers

**Required inputs:**
- `vintage_df` — long-format table with columns:
  - `vintage` — origination period label (e.g. "2023-Q1")
  - `mob` — months on book (integer)
  - metric column — performance rate at that MOB (e.g. cumulative default rate, 30+ DPD rate)
- `metric` — name of the metric column to plot
- `highlight_vintage` *(optional)* — one vintage to accent; all others rendered in gray

**Key design decisions:**
- Each vintage is one line; highlight the cohort of interest, gray all others
- Label the highlighted vintage directly at its last data point
- Steeper early slope → worse origination quality; parallel upward shift at MOB → macro deterioration

---

## 4. Migration Matrix — Credit State Transitions

**Use when:** Showing movement between credit states over an observation period
(e.g., Current → DPD30 → DPD60 → Write-off).

**Audience:** Risk committee, regulator

**Required inputs:**
- `matrix` — 2D array or DataFrame; rows = from-state, columns = to-state, values in %
- `states` — ordered list of state labels (e.g. `["Current", "DPD30", "DPD60", "Write-off"]`)

**Key design decisions:**
- Use a perceptually-uniform sequential colormap (YlOrRd)
- Always annotate values in every cell — color is a secondary cue, not the sole carrier
- Focus audience attention on off-diagonal entries that have shifted vs. prior period

---

## 5. Risk Heatmap — Segment × Metric

**Use when:** Showing concentration across two dimensions (product × DPD bucket,
region × risk grade, etc.).

**Audience:** Risk committee, portfolio managers

**Required inputs:**
- `df_pivot` — pivot table; rows = one segmentation dimension, columns = second dimension, values = metric rate (%)

**Key design decisions:**
- Annotate every cell; color is a redundant, not primary, cue
- Colorblind readers must be able to use the chart from numbers alone
- Use `RdYlGn_r` for rate metrics where higher = worse (red = danger)

---

## 6. Bullet Chart — KPI vs Target

**Use when:** Showing one metric against its target and qualitative performance bands.
Replaces dial/gauge charts, which encode values as angles — much harder to decode.

**Audience:** Executive, division heads

**Required inputs:**
- `actual` — current metric value (float)
- `target` — target or benchmark value (float)
- `bands` — list of upper-bound values for each performance band
  (e.g. `[3.0, 5.0, 8.0]` → 0–3 acceptable, 3–5 watch, 5–8 breach)
- `metric_name` — axis label including units (e.g. "NPL Ratio (%)")

**Key design decisions:**
- The bar encodes the actual value; the vertical line encodes the target
- Shaded bands supply qualitative context without requiring a legend
- Use green / amber / red band colors aligned to acceptable / watch / breach thresholds

---

## 7. PSI Bar Chart — Population Stability Index

**Use when:** Monitoring score distribution drift between reference and current period.

**Audience:** Model committee, practitioners, regulator

**Required inputs:**
- `bins` — list of score bin labels (e.g. score deciles or custom ranges)
- `pct_ref` — % of population in each bin during the reference period
- `pct_current` — % of population in each bin during the current period
- `psi_total` — pre-computed PSI value (scalar)

**PSI thresholds (industry convention):**
- < 0.10 → stable
- 0.10 – 0.25 → moderate shift, increase monitoring frequency
- > 0.25 → significant shift, investigate root cause or retrain

**Key design decisions:**
- Side-by-side bars per bin: reference in gray, current in accent color
- Embed a status badge in the chart (color-coded by PSI threshold)
- Title states the verdict, not just the statistic

---

## Formal Report Checklist

Before any chart goes into a validation document, committee deck, or regulatory submission:

```
[ ] Bar charts start at 0 — no cropped y-axis
[ ] Dual y-axis not present
[ ] Sample size (n=) and observation period stated on chart
[ ] Trend lines declare the fitting method
[ ] Values annotated directly — color is a secondary cue
[ ] Data-as-of date included
[ ] No 3D effects or decorative elements
[ ] Readable in grayscale
[ ] Axis labels include units
[ ] Title states the insight, not the description
```
