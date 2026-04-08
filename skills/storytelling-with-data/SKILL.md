---
name: storytelling-with-data
description: Transforms data into compelling visual stories for financial services DS contexts. Covers the six-step communication framework (context → chart → clutter → attention → design → story) plus credit and risk analytics chart patterns (KS curve, vintage, migration matrix, risk heatmap, ROC/calibration, SHAP, PSI), multi-tier audience design (executive/committee/regulator/DS), and trustworthiness principles for regulated environments. Renders output in Databricks notebooks via display(fig) and displayHTML().
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: Synthesized from visualization and data communication principles
    adapted-for: Databricks (inline display via display(fig) and displayHTML())
---

# Storytelling with Data

## Overview

Data visualization is not just about displaying numbers — it is about communicating a message to a specific audience so they can take action. This skill covers both the general communication framework and credit/risk analytics chart patterns for financial services DS work.

---

## The Six-Step Framework

### Step 1 — Understand the Context

Before writing a single line of code, answer three questions:

**Who is your audience?**
- Identify the single primary decision-maker
- What do they already know? What don't they know?
- What do they care about? What will they do with this information?

**What do you need them to know or do?**
- Write one sentence: "I want my audience to [action/belief] because [data evidence]"
- This is the **Big Idea** — it must be specific, concrete, and convey a point of view

**How will you communicate?**
- Live presentation (verbal + visual, less text on slides)
- Document/report (must stand alone, more text)
- Dashboard (exploratory, no single narrative)

**Context checklist before proceeding:**
```
[ ] I can name my primary audience
[ ] I have written a one-sentence Big Idea
[ ] I know what action I want them to take
[ ] I know if this is a live presentation, document, or dashboard
```

Consult `references/principles/context-setting.md` for the full audience analysis worksheet.

---

### Step 2 — Choose an Appropriate Display

Use the correct chart for the relationship in your data. Never pick a chart because it looks impressive.

| Relationship | Best Chart | Avoid |
|---|---|---|
| Change over time | Line plot | Bar chart for many time points |
| Comparison (few categories) | Bar chart (vertical) | 3D bar, exploded pie |
| Comparison (many categories) | Horizontal bar | Vertical bar with rotated labels |
| Part of a whole | Stacked bar, 100% bar | Pie chart, donut chart |
| Distribution | Histogram, box plot | |
| Correlation / relationship | Scatter plot | |
| Two variables over time | Connected scatter | Dual-axis line |
| Single number that matters | Big number + context | Table |

**Rule:** If you are using a pie chart, ask whether a bar chart would be clearer. The answer is almost always yes.

Consult `references/principles/chart-selection.md` for full decision guide with examples.

---

### Step 3 — Eliminate Clutter

Clutter is any visual element that does not add informational value. It increases cognitive load without increasing understanding.

**Elements to eliminate by default:**
- Chart borders and frames
- Gridlines (remove or lighten to near-invisible)
- Data markers on every point of a line
- Axis labels that duplicate data labels
- Legends when you can label directly
- 3D effects, shadows, gradients
- Dual y-axes (almost always)
- Titles that describe what ("Sales by Month") instead of the insight ("Sales peaked in Q3")

**The data-ink test:** For every element, ask "Would removing this lose information?" If no → remove it.

```python
# Databricks: standard clutter elimination
import matplotlib.pyplot as plt

def declutter(ax):
    """Remove visual noise from a matplotlib axes."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.tick_params(colors='#666666')
    ax.yaxis.grid(True, color='#EEEEEE', linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    return ax
```

Consult `references/principles/clutter-elimination.md` for the full declutter checklist.

---

### Step 4 — Focus Attention

The audience's eye goes where you direct it. Use **pre-attentive attributes** to highlight the signal and suppress the noise.

Pre-attentive attributes (processed in < 250ms, before conscious thought):

| Attribute | Best for | How to apply |
|---|---|---|
| **Color (hue)** | Categorical difference | 1 accent color; rest in gray |
| **Color (intensity)** | Magnitude / importance | Darker = more important |
| **Size** | Magnitude | Larger = more important |
| **Position** | Comparison | Align baselines |
| **Bold / weight** | Text emphasis | Bold the key number |
| **Enclosure** | Grouping | Box / shading around a region |

**Golden rule:** Use one accent color. Everything else is gray (`#CCCCCC` or `#AAAAAA`). The accent draws the eye; gray provides context without competing.

```python
# Storytelling with Data color pattern
GRAY_LIGHT  = '#CCCCCC'
GRAY_MED    = '#888888'
GRAY_DARK   = '#444444'
ACCENT      = '#E8664A'   # warm coral — stands out, not alarming
ACCENT_BLUE = '#1A77B5'   # for positive / neutral emphasis

def apply_swd_palette(ax, highlight_index, bars):
    """Color one bar accent, all others gray."""
    for i, bar in enumerate(bars):
        bar.set_color(ACCENT if i == highlight_index else GRAY_LIGHT)
```

Consult `references/principles/pre-attentive-attributes.md` for full visual emphasis guide.

---

### Step 5 — Think Like a Designer

Design is not decoration — it is the arrangement of elements to serve communication.

**Affordance:** Make it obvious how to read the chart. Labels should sit next to what they label. Axes should have clear titles with units.

**Accessibility:**
- Colorblind-safe: never use red + green as the only differentiator
- Minimum font size: 10pt for body, 12pt for titles
- All text horizontal (never rotated axis labels — use horizontal bar instead)

**Aesthetics — the three rules:**
1. Use white space intentionally; do not fill every pixel
2. Align elements on a grid; ragged layouts look unfinished
3. Choose one type family; vary weight and size, not the font

**Gestalt principles that apply most to data viz:**

| Principle | Application |
|---|---|
| **Proximity** | Group related series / labels close together |
| **Similarity** | Same color = same category across charts |
| **Enclosure** | Shaded region = this area is different / important |
| **Continuity** | Line implies connection; use only when data is continuous |
| **Figure-ground** | Accent color pops; gray recedes |

Consult `references/principles/design-principles.md` for the full design checklist.

---

### Step 6 — Tell a Story

A presentation without a narrative is a data dump. Structure your communication like a story.

**The Story Arc:**

```
Setup (tension)           → Conflict (complication)      → Resolution (call to action)
"Here is what we expected"  "Here is what actually happened"  "Here is what we should do"
```

**The 3-Minute Story:**
Distill your entire message to what you would say if you had only 3 minutes. This forces clarity. Then expand.

**Annotation as narrative:**
Use text directly on the chart to guide the audience. Never make them look back and forth between a legend and the chart.

```python
# Annotating the key moment in a line chart
ax.annotate(
    'Policy change\ncaused spike',
    xy=(highlight_x, highlight_y),
    xytext=(highlight_x + 2, highlight_y + 5),
    arrowprops=dict(arrowstyle='->', color=GRAY_DARK, lw=1.2),
    fontsize=9, color=GRAY_DARK,
    ha='left'
)
```

**Slide / section title rule:** The title IS the takeaway.
- Bad title: "Revenue by Region Q1–Q4 2024"
- Good title: "Northeast revenue fell 18% in Q3 — driven by supply disruption"

Consult `references/principles/narrative-structure.md` for story templates, slide structure, and the full annotation guide.

---

## Workflow

When a user brings data to communicate, follow this sequence:

1. **Elicit context** — Ask who the audience is and what action is needed. Do not proceed without a Big Idea.
2. **Audit the current visual** (if one exists) — Apply the clutter checklist. List every element that should be removed.
3. **Select or confirm chart type** — Justify with the chart selection guide.
4. **Apply the declutter template** — Use `declutter(ax)` + strip spines.
5. **Apply pre-attentive attributes** — One accent color; everything else gray.
6. **Write the chart title as the insight** — Not the description.
7. **Add annotations** — Mark the moment that supports the Big Idea.
8. **Render in Databricks** — `display(fig)` + `plt.close(fig)`.

---

## Databricks Quick Start

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# SWD color constants
GRAY_LIGHT  = '#CCCCCC'
GRAY_MED    = '#888888'
ACCENT      = '#E8664A'

# --- Data ---
categories = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
values     = [42, 78, 55, 91, 63]
highlight  = 3   # index of the bar we want the audience to focus on

# --- Build chart ---
fig, ax = plt.subplots(figsize=(6, 3.5))

colors = [ACCENT if i == highlight else GRAY_LIGHT for i in range(len(categories))]
bars = ax.barh(categories, values, color=colors, height=0.55)

# Eliminate clutter
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.xaxis.set_visible(False)
ax.tick_params(left=False)

# Direct labels — no axis needed
for bar, val in zip(bars, values):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
            f'{val}%', va='center', fontsize=9,
            color=ACCENT if val == values[highlight] else GRAY_MED,
            fontweight='bold' if val == values[highlight] else 'normal')

# Title IS the insight
ax.set_title('Product D leads with 91% satisfaction — 13 pts above average',
             fontsize=11, fontweight='bold', color='#222222', loc='left', pad=12)

display(fig)
plt.close(fig)
```

---

## Domain Context: Credit and Risk Analytics

### Audience Tiers

The same model or analysis requires a different visualization for each audience. Always identify the primary recipient before choosing a chart type.

| Tier | Who | What They Need | Chart Style |
|---|---|---|---|
| **Executive** | Head of division, business owner | Business impact in $ or %, single KPI trend | Bullet chart, big number + sparkline, 1-chart slides |
| **Risk / Model Committee** | Risk managers, validators | Model performance, stability, concentration | KS curve, vintage, migration matrix, PSI |
| **Regulator / Auditor** | External / internal audit | Methodology transparency, non-misleading scales | Conservative styling, full annotation, axis at 0 |
| **Fellow Practitioner** | Data scientists, MLEs | Diagnostic depth, calibration, attribution | ROC, calibration plot, SHAP, confusion matrix |

A KS curve in an executive slide will confuse; a single summary number in a risk review will be rejected as insufficient. These are not interchangeable.

### Trustworthiness in Regulated Environments

Visualizations in formal reports — model validation documents, regulatory submissions, audit trails — carry an obligation of accuracy that goes beyond aesthetic choices.

**Non-negotiable rules:**
- Bar charts must start at 0 — a cropped y-axis artificially inflates differences
- Dual y-axis must not be used in formal reports — the relationship between two arbitrary scales is misleading
- Sample size and observation period must be stated on every chart
- Trend lines must declare the method (rolling average, linear regression, LOWESS)
- Color must not be the sole information carrier — annotate values directly
- All charts in versioned reports carry a data-as-of date

### Task Map by Domain

**Credit and Risk Analytics**

| Task | Primary Chart | Reference |
|---|---|---|
| Scorecard discrimination | KS curve + score distribution overlay | `credit-risk-charts.md` |
| Portfolio cohort health | Vintage curve | `credit-risk-charts.md` |
| Credit state transitions | Migration matrix | `credit-risk-charts.md` |
| Risk concentration | Risk heatmap (segment × metric) | `credit-risk-charts.md` |
| KPI vs target | Bullet chart | `credit-risk-charts.md` |
| Model drift monitoring | PSI bar chart | `credit-risk-charts.md` |

**Model Evaluation (all domains)**

| Task | Primary Chart | Reference |
|---|---|---|
| Discrimination | ROC + KS | `model-evaluation-viz.md` |
| Class imbalance performance | Precision-recall curve | `model-evaluation-viz.md` |
| Probability trustworthiness | Calibration / reliability diagram | `model-evaluation-viz.md` |
| Global feature attribution | Feature importance bar | `model-evaluation-viz.md` |
| Individual decision explanation | SHAP waterfall | `model-evaluation-viz.md` |
| Business value of model | Lift / gain chart | `model-evaluation-viz.md` |

**Fraud Detection**

| Task | Primary Chart | Reference |
|---|---|---|
| Volume + anomaly window | Time series + enclosure | `fraud-detection-charts.md` |
| Volume vs rate trend | Dual panel (no dual axis) | `fraud-detection-charts.md` |
| Suspicious entity pattern | Scatter: amount × frequency | `fraud-detection-charts.md` |
| Time-of-day concentration | Calendar heatmap | `fraud-detection-charts.md` |
| Alert context | Rolling z-score with ±σ band | `fraud-detection-charts.md` |

**Customer Analytics**

| Task | Primary Chart | Reference |
|---|---|---|
| Retention by cohort | Cohort retention heatmap | `customer-analytics-charts.md` |
| Onboarding / product funnel | Center-aligned funnel chart | `customer-analytics-charts.md` |
| Segment comparison | Small multiples bar (not radar) | `customer-analytics-charts.md` |
| Churn risk sizing | Probability distribution + bands | `customer-analytics-charts.md` |
| CLV comparison | Horizontal box plot by segment | `customer-analytics-charts.md` |
| A/B test / campaign result | Effect size with CI | `customer-analytics-charts.md` |

**Causal Inference**

| Task | Primary Chart | Reference |
|---|---|---|
| Treatment effect estimate | Coefficient plot with CI | `causal-inference-charts.md` |
| Parallel trends assumption | Pre/post trend overlay | `causal-inference-charts.md` |
| DiD heterogeneity | Subgroup effect plot | `causal-inference-charts.md` |
| RDD discontinuity | Binned scatter + regression | `causal-inference-charts.md` |
| Propensity overlap | Overlapping histogram | `causal-inference-charts.md` |

---

## Common Anti-Patterns and Fixes

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Rainbow colors for categories | Eye jumps everywhere, no focal point | 1 accent color + gray for the rest |
| Pie chart with 6+ slices | Cannot compare angles accurately | Horizontal bar chart |
| Dual y-axis | Misleading — scales are arbitrary | Two separate charts, or index to 100 |
| Title describes the chart | Audience must figure out the point themselves | Title states the insight |
| Legend instead of direct labels | Forces back-and-forth eye movement | Label lines/bars directly |
| Y-axis not starting at 0 (bar charts) | Exaggerates differences | Always start at 0 for bars |
| Sorted alphabetically | Ranking is invisible | Sort by value (descending) |
| All data equally visible | No signal, only noise | Gray everything except the key series |

---

## Resources

### references/principles/
Communication and design fundamentals — apply to all chart types.

- `context-setting.md` — Audience analysis worksheet, Big Idea template, communication mode guide
- `chart-selection.md` — Chart decision guide with code templates for each type
- `clutter-elimination.md` — Declutter checklist, data-ink ratio, before/after examples
- `pre-attentive-attributes.md` — Pre-attentive attribute reference with code patterns
- `design-principles.md` — Gestalt principles, accessibility checklist, typography
- `narrative-structure.md` — Story arc templates, annotation guide, slide title rules

### references/domain/
Domain-specific chart patterns with ready-to-run code.

- `credit-risk-charts.md` — KS curve, vintage, migration matrix, risk heatmap, bullet chart, PSI
- `model-evaluation-viz.md` — ROC, calibration, SHAP waterfall, feature importance, lift/gain
- `fraud-detection-charts.md` — Anomaly time series, dual panel, scatter outlier, calendar heatmap, rolling z-score
- `customer-analytics-charts.md` — Cohort retention, funnel, segment profile, churn distribution, CLV box, A/B test CI
- `causal-inference-charts.md` — Coefficient plot, parallel trends, DiD event study, RDD binned scatter, propensity overlap

### scripts/
- `swd_style.py` — General: `declutter()`, `apply_swd_palette()`, `annotate_insight()`, `insight_title()`, `label_bars()`, `highlight_region()`
                   Domain: `risk_colormap()`, `psi_status()`, `fmt_pct()`, `fmt_bps()`, `waterfall_colors()`
