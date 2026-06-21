---
name: banking-visualization
description: Domain-specific charting for banking and financial-services data science. Use when building credit-risk, fraud, or customer-analytics figures for executives, risk committees, regulators, or fellow practitioners. Covers audience tiers, trustworthiness obligations in regulated environments (axis-at-zero, data-as-of dates, no color-only encoding, dual-axis caveats), and a task map of standard banking charts (KS curve, PSI bar, migration matrix, vintage curve, fraud anomaly enclosure, cohort retention). Defers the general SWD framework and library choice to the `visualization` skill.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: ds-skills
    domain: banking
    adapted-for: Databricks (%md cells for narrative, display(fig) for figures)
---

# Banking Visualization — Domain Charts

## Overview

This skill covers the **domain layer** of banking visualization: the specific
charts, audiences, and trust obligations that distinguish a credit-risk figure
from a generic one. It does **not** restate the general framework.

> **Read the `visualization` skill first.** It owns the SWD (Storytelling with
> Data) framework — Big Idea, decluttering, pre-attentive attributes, narrative —
> and the library decision tree (Plotly for EDA, matplotlib for publication,
> matplotlib + NYT theme for stakeholders). Everything here assumes that
> foundation and adds the banking-specific constraints on top.

Use this skill when the **audience is regulated** or the **chart is a banking
artifact** (scorecard performance, fraud monitoring, portfolio risk, customer
lifecycle). The core question shifts from "is this the clearest chart?" to
"is this chart clear **and** defensible to someone whose job is to find fault
with it?"

---

## 1. Audience Tiers

The same metric is plotted differently for each tier. Pick the tier before the
chart type.

| Tier | Needs | Provide | Avoid |
|------|-------|---------|-------|
| **Executive** | The decision and its size | One Big Idea per chart, absolute money/customers, a clear "so what" title | Model internals, more than one trend line, statistical jargon |
| **Risk Committee** | Whether risk is within appetite | Metric vs threshold/limit (bullet charts), trend with control bands, segment breakouts | Unlabeled thresholds, charts without an appetite reference line |
| **Regulator / Validator** | That the method is sound and the result reproducible | Full method footnotes, data-as-of date, sample sizes per bin, definitions of bad/good, every axis from a defensible baseline | Smoothing that hides instability, truncated axes, cherry-picked windows |
| **Practitioner (DS/analyst)** | Diagnostic detail to act | Distributions, residuals, per-segment KS/PSI, interactive EDA (Plotly) | Over-polished "exec" charts that drop the diagnostic detail they need |

**Rule:** when a single figure must serve two tiers, build the practitioner
version first, then produce a *separate* decluttered executive cut. Do not try to
serve an exec and a validator with one chart — their failure modes are opposite
(simplification vs completeness).

---

## 2. Trustworthiness in Regulated Environments

A chart in a banking context can become a compliance artifact. These are not
style preferences — a model validator can flag a misleading chart.

- **Axis at zero for magnitude encodings.** Bar charts and area charts must start
  the value axis at 0. A truncated bar axis that exaggerates a default-rate gap
  is the canonical "misleading chart" finding. (Line charts tracking a rate over
  time *may* zoom, but label the range explicitly.)
- **Data-as-of date on every figure.** Portfolio numbers move daily. Stamp the
  snapshot date and the data source in a subtitle or footnote. A chart without an
  as-of date is not reproducible and not defensible.
- **No color-only encoding.** ~8% of men have color-vision deficiency, and reports
  get printed in grayscale. Encode categories redundantly (label, marker shape,
  or direct annotation), not by hue alone. Red/green for good/bad must also carry
  text or position.
- **Dual-axis caveats.** Two y-axes (e.g., volume bars + rate line) invite false
  correlation by letting the author scale axes to manufacture a relationship.
  Use them only when the two series are genuinely a volume/rate pair, label both
  axes and their zero points, and never imply causation from visual crossover.
- **Show sample size.** KS, PSI, and bad-rate charts on thin bins are unstable.
  Annotate n per bin (or grey out bins below a minimum count) so the reader knows
  which points to trust.
- **Bin and threshold definitions are part of the chart.** Score bands, PSI bins,
  and "bad" definitions must be stated. A KS curve means nothing without the
  good/bad definition and observation window.

---

## 3. Task Map

Each task points to a reference file with ready-to-run PySpark/pandas → matplotlib
code. Implementation detail and the "Formal Report Checklist" live in the
references; this is the index.

### Credit & Risk Analytics → `references/credit-risk-charts.md`
- **Score distribution (discriminant overlay)** — good vs bad score densities;
  shows separation at a glance.
- **KS curve** — Kolmogorov–Smirnov separation; the standard discrimination plot.
- **Vintage curve** — cohort performance over months-on-book.
- **Migration matrix** — rating/state transitions as a heatmap.
- **Risk heatmap** — segment × metric.
- **Bullet chart** — KPI vs appetite/target (the Risk Committee workhorse).
- **PSI bar chart** — population stability across periods, with the
  green/amber/red 0.1 / 0.25 convention shown as reference lines.

### Fraud Detection → `references/fraud-detection-charts.md`
- **Transaction time series with anomaly enclosure** — highlight flagged windows.
- **Fraud-rate dual view** — volume bars + rate line (with the dual-axis caveat).
- **Amount vs frequency scatter** — outlier labeling.
- **Calendar heatmap** — fraud by day and hour.
- **Z-score / rolling-deviation** — real-time alert context.
- **Network graphs** — ring/mule structures (use sparingly; usually exploratory).

### Customer Analytics → `references/customer-analytics-charts.md`
- **Cohort retention heatmap.**
- **Conversion funnel.**
- **RFM segment profile** (small multiples).
- **Churn-risk distribution.**
- **Customer lifetime value** by segment.
- **A/B test result** — effect size with confidence interval (show the CI, never
  a bare bar of two means).

---

## 4. Workflow

1. **Identify the audience tier** (Section 1) — this fixes how much detail and
   polish the chart carries.
2. **Apply the general SWD framework** from the `visualization` skill — Big Idea,
   chart selection, declutter, pre-attentive emphasis, narrative title.
3. **Pick the library** via the `visualization` decision tree — Plotly for
   practitioner EDA, matplotlib (+ NYT theme) for committee/exec/regulator
   deliverables.
4. **Pull the chart pattern** from the relevant reference in Section 3.
5. **Run the trustworthiness checklist** (Section 2) before the figure leaves
   your notebook: axis-at-0, as-of date, redundant encoding, sample sizes,
   threshold definitions.

---

## References

- `references/credit-risk-charts.md` — scorecard and portfolio-risk charts +
  Formal Report Checklist.
- `references/fraud-detection-charts.md` — monitoring and anomaly charts +
  audience guide.
- `references/customer-analytics-charts.md` — lifecycle, retention, and
  experiment charts + audience guide.

**Cross-skill:** `../visualization/` for the SWD framework, library decision
tree, grammar-of-graphics (plotnine), and publication styling. `../shared/nyt_theme.py`
for the slide-first NYT style shared across matplotlib, Plotly, and plotnine.
