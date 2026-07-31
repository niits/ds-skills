---
name: visualization
description: >
  Make charts that communicate, for data science on Databricks. Use when building any
  figure — exploratory, publication, or stakeholder presentation.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: ds-skills
    domain: general
    adapted-for: Databricks (display(fig) for inline rendering; %md cells for narrative)
---

# Visualization for Data Scientists

## Overview & Philosophy

Two ideas govern every chart you make:

1. **SWD is always on.** Storytelling-with-Data is not a library or a chart type — it
   is the framework for communicative effectiveness, and it applies *regardless of which
   tool you use*. Big Idea → right chart → declutter → focus attention → design →
   narrative. Apply it to a throwaway EDA scatter and to a journal figure alike.
2. **Choose the library by the output goal, not by preference.** Plotly, matplotlib,
   and plotnine each win for a different goal. Picking by habit ("I always use
   matplotlib") is how you end up with a static, hover-less chart in an exploration task
   or an over-engineered grammar-of-graphics pipeline for a one-off figure.

This skill merges two concerns that used to be separate skills — the SWD framework for
communicative effectiveness, and the grammar of graphics (plotnine) for declarative chart
construction — into one goal-based reference. matplotlib/seaborn remain the default renderer for
static output. Publication-submission mechanics (venue formatting, DPI, journal requirements)
are out of scope here: this reference is about whether the chart lands the message, not how it
clears a submission checklist.

## Library Decision Tree

```
What is this chart for?
├─ Exploring data (EDA, unknown pattern) → Plotly first (interactive: hover, zoom, brush)
│   └─ Chart type not supported in Plotly → plotnine → matplotlib
├─ Static figure for a paper / journal → matplotlib / seaborn
│   └─ Chart fits grammar of graphics (faceted, grouped, layered) → plotnine acceptable
├─ Slide / presentation for stakeholders → matplotlib, slide-first defaults (large fonts, high
│   contrast, direct labels)
│   └─ Dashboard / interactive report → Plotly
└─ Binary classifier evaluation chart (ROC, PR, calibration, confusion matrix, KS, PSI) →
    `references/model-evaluation-viz.md`
```

The fallback arrows matter: **goal fixes the primary tool; capability gaps walk you
down the fallback chain.** Plotly is primary for EDA but cannot do everything — drop to
plotnine (grammar fit) then matplotlib (full control). Never invert this by starting
from the tool.

---

## SWD Framework (apply to every chart)

The through-line for all three goals below. Each step links to a reference with depth.

1. **Big Idea** — one sentence the chart must land. If you can't state it, you're not
   ready to plot. → `references/context-setting.md`
2. **Chart selection** — match the message to the form (trend → line, comparison → bar,
   distribution → histogram/box, relationship → scatter). → `references/chart-selection.md`
3. **Declutter** — remove everything that isn't carrying information: chartjunk,
   redundant gridlines, heavy borders, default legends you can replace with direct
   labels. → `references/clutter-elimination.md`
4. **Focus attention** — use pre-attentive attributes (color, size, position) so the eye
   lands on the Big Idea first; grey everything else. → `references/pre-attentive-attributes.md`
5. **Design** — alignment, whitespace, typography, sensible defaults. →
   `references/design-principles.md`
6. **Narrative** — the title *is* the insight (not "Default rate by month" but "Default
   rate is rising in subprime"); annotate the key moment. → `references/narrative-structure.md`
   and `references/audience-adaptation.md`

Use causal language only when the identification design supports it. Otherwise say
“is associated with,” “coincides with,” or describe the observed difference. Simplify
terminology, not evidence: retain material uncertainty, limitations, subgroup harms,
period, denominator, and source in the title, subtitle, annotation, or caption.

`assets/swd_style.py` operationalizes steps 3–6 for matplotlib: `declutter(ax)`,
`apply_swd_palette(values, ...)` (one highlighted, rest grey), `annotate_insight(ax, ...)`,
`insight_title(ax, ...)`, `label_bars(ax, ...)`.

---

## Mandatory Pre-Plot Audit

Before choosing a chart, record: analysis unit/grain; filters and exclusions; time
window, interval, and timezone; missingness by group/time; duplicate units; weights;
aggregation level; numerator and denominator for every rate; changing or zero
denominators; and sample/per-group/bin counts. A chart is `BLOCKED` when its displayed
denominator, missing-data treatment, or aggregation cannot be explained. Preserve this
information in the caption, note, accessible table, or adjacent text.

---

## Goal 1: EDA & Exploration

**Primary: Plotly.** Exploration means you don't yet know the pattern — so you need
hover (read exact values), zoom, and brushing. Static charts make you re-plot to
answer the next question; interactivity lets you ask it in place.

```python
import plotly.express as px
fig = px.scatter(df, x="amount", y="frequency", color="segment",
                 hover_data=["customer_id"], opacity=0.6)
fig.show()            # interactive in notebook
```

**Fallback: plotnine → matplotlib.** When Plotly lacks the chart (some statistical
layers, niche annotations), use plotnine if a grammar-of-graphics structure fits
(faceted small multiples across segments), otherwise matplotlib.

Even in EDA, SWD still applies in lightweight form: one question per chart, readable
axes, colorblind-safe categorical colors.

---

## Goal 2: Paper/Journal Figure

**Primary: matplotlib/seaborn**, with plotnine as a fallback when the chart's structure fits a
grammar-of-graphics layout (faceted, grouped, multi-layer). This goal is about correct,
honest chart-type selection and colorblind-safe encoding, not venue formatting — for exact
dimensions, DPI, and file-format requirements, consult your target venue's author guidelines
directly (out of scope here, see Overview above). Chart-type patterns (training curves,
ablations, heatmaps, scaling-law plots, and more) are in `references/data-visualization.md`;
worked examples for showing uncertainty honestly are in `references/matplotlib-examples.md`;
color-palette choice and caption practices are in `references/color-palettes.md` and
`references/style-guide.md`; broader clarity/accuracy/accessibility principles are in
`references/publication-guidelines.md`. As with every chart in this skill, the SWD framework
above still applies: state the Big Idea, declutter, and don't bury statistical caveats.

---

## Goal 3: Business Presentation

**Primary: matplotlib, with slide-first defaults.** Large fonts, wide (16:9) sizing,
decluttered spines, title-as-insight — apply these directly with rcParams and
`assets/swd_style.py` rather than a bundled theme file.

```python
import matplotlib.pyplot as plt
from swd_style import declutter, insight_title, apply_swd_palette, label_bars

plt.rcParams.update({"font.size": 16, "axes.titlesize": 20})
fig, ax = plt.subplots(figsize=(13.33, 7.5))   # 16:9, presentation scale
# ... plot, then declutter(ax), insight_title(ax, "the takeaway"),
#     direct-label instead of a legend ...
display(fig)
```

**Faceted / grouped slide chart → plotnine** with an explicit built-in theme recipe in
`references/grammar-of-graphics.md`. For the same look in
grammar-of-graphics form. **Dashboard / interactive report → Plotly** so stakeholders
can drill in themselves.

A presentation chart is the most SWD-demanding: one Big Idea per slide, everything
non-essential greyed, the insight in the title.

---

## Grammar of Graphics Reference (plotnine)

Use plotnine when declarative layered structure fits — faceted, grouped, multi-layer
statistical charts. Full geom / stat / scale / facet / theme API, a slide-theme
recipe, Databricks rendering, and "when NOT to use plotnine" are in
`references/grammar-of-graphics.md`.

## Color and Statistical-Honesty Reference (matplotlib figures)

Colorblind-safe palette choice (Okabe-Ito, Tol, viridis family), when to use sequential vs.
diverging vs. categorical color, showing uncertainty honestly, avoiding distorted/misleading
encodings, and chart-type patterns for common ML-paper figures are in
`references/color-palettes.md`, `references/style-guide.md`,
`references/publication-guidelines.md`, `references/matplotlib-examples.md`, and
`references/data-visualization.md`. `assets/color_palettes.py` (`apply_palette`, `get_palette`)
implements the palette choices in code.

---

## Databricks Rendering

- Render any matplotlib/plotnine figure inline with `display(fig)` (call `p.draw()`
  first for a plotnine object to get the `Figure`). Plotly renders with `fig.show()`.
- Upload `assets/` helpers to DBFS (or add the repo path to `sys.path`) before
  importing `swd_style` / `color_palettes`. Verify the upload before importing.
- Use explicit, reproducible figure sizes; do not rely on the notebook's default DPI.
- For interactive output, use responsive sizing and test at roughly 360 px width; do
  not put essential information only in hover. Check keyboard/focus behavior where the
  platform supports it and use touch-sized controls.
- Every delivered chart needs a concise text takeaway, meaningful alt text in the
  delivery surface, and an accessible adjacent data table or downloadable CSV.
- Colorblind-safe palettes are not sufficient by themselves: use redundant markers,
  line styles, labels, or hatches and verify text/background contrast.

Minimal delivery bundle:

```python
from pathlib import Path

out = Path("figures/model_comparison")
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out.with_suffix(".png"), dpi=300)
plotted_data.to_csv(out.with_suffix(".csv"), index=False)
# Add the takeaway and alt text in the notebook/report element that embeds the image.
```

---

## Resources

### references/ — SWD framework
- `context-setting.md`, `chart-selection.md`, `clutter-elimination.md`,
  `pre-attentive-attributes.md`, `design-principles.md`, `narrative-structure.md`,
  `audience-adaptation.md`

### references/ — styling & grammar
- `grammar-of-graphics.md` — plotnine geom/stat/scale/facet/theme API
- `publication-guidelines.md`, `style-guide.md`
- `color-palettes.md`, `matplotlib-examples.md`, `data-visualization.md`

### references/ — general analysis charts
- `model-evaluation-viz.md` — ROC, PR, calibration, confusion-matrix, KS, PSI charts
- `causal-inference-charts.md` — DiD, event-study charts

### assets/
- `swd_style.py` — SWD helpers (declutter, palette, annotate, insight title, label_bars,
  highlight_region, fmt_pct)
- `color_palettes.py` — colorblind-safe palettes (Okabe-Ito, Tol) and colormap choice lists
