---
name: visualization
description: >
  Make charts that communicate, for data science on Databricks. Use when building any
  figure — exploratory, publication, or stakeholder presentation. Applies the
  Storytelling-with-Data (SWD) framework to every chart, then picks the library by
  output goal: Plotly for interactive EDA, matplotlib/seaborn for publication, matplotlib
  + NYT theme for presentations, plotnine when the grammar of graphics fits. Covers chart
  selection, decluttering, pre-attentive emphasis, colorblind-safe palettes, venue sizing,
  and Databricks rendering.
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

This skill merges three concerns that used to be separate skills — the SWD framework,
publication/scientific styling (matplotlib/seaborn), and the grammar of graphics
(plotnine) — into one goal-based reference.

## Library Decision Tree

```
What is this chart for?
├─ Exploring data (EDA, unknown pattern) → Plotly first (interactive: hover, zoom, brush)
│   └─ Chart type not supported in Plotly → plotnine → matplotlib
├─ Static figure for a paper / journal → matplotlib / seaborn
│   └─ Chart fits grammar of graphics (faceted, grouped, layered) → plotnine acceptable
├─ Slide / presentation for stakeholders → matplotlib + NYT theme
│   └─ Dashboard / interactive report → Plotly
└─ Banking domain chart (KS, PSI, vintage, fraud monitoring) → see `banking-visualization` skill
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

`assets/swd_style.py` operationalizes steps 3–6 for matplotlib: `declutter(ax)`,
`apply_swd_palette(values, ...)` (one highlighted, rest grey), `annotate_insight(ax, ...)`,
`insight_title(ax, ...)`, `label_bars(ax, ...)`.

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

## Goal 2: Publication / ML Papers

**Primary: matplotlib / seaborn.** Static, print-resolution, fully controllable. Use
the publication style presets and a colorblind-safe palette.

```python
import sys; sys.path.append("assets")     # or the Databricks DBFS path you uploaded to
from style_presets import apply_publication_style, set_color_palette, configure_for_journal

apply_publication_style("default")         # clean, professional rcParams
set_color_palette("okabe_ito")             # colorblind-safe categorical
configure_for_journal("nature", figure_width="single")   # venue sizing + DPI
```

**Acceptable: plotnine** when the figure is grammar-of-graphics-compatible — faceted
panels, grouped aesthetics, layered geoms. A 3×N faceted comparison is cleaner as
plotnine than as a hand-built matplotlib subplot grid.

Get the details right (these are reject-triggers at review): vector format (PDF/SVG)
or ≥300 DPI raster, colorblind-safe palette, error bars defined, font sizes legible at
print size, venue column-width sizing. → `references/publication-guidelines.md`,
`references/journal-requirements.md`, `references/matplotlib-examples.md`.

---

## Goal 3: Business Presentation

**Primary: matplotlib + NYT theme.** Slide-first defaults: large fonts, 16:9 sizing,
decluttered spines, title-as-insight.

```python
import sys; sys.path.append("..")          # make `shared` importable (or the DBFS path you uploaded to)
from shared.nyt_theme import apply_nyt_all, NYT, FIG_SLIDE   # ../shared/nyt_theme.py
apply_nyt_all()                            # NYT rcParams (also strips top/right spines)
fig, ax = plt.subplots(figsize=FIG_SLIDE)
# ... plot, then direct-label instead of a legend, title = the takeaway ...
display(fig)
```

**Faceted / grouped slide chart → plotnine** with `theme_nyt()` for the same look in
grammar-of-graphics form. **Dashboard / interactive report → Plotly** so stakeholders
can drill in themselves.

A presentation chart is the most SWD-demanding: one Big Idea per slide, everything
non-essential greyed, the insight in the title.

---

## Grammar of Graphics Reference (plotnine)

Use plotnine when declarative layered structure fits — faceted, grouped, multi-layer
statistical charts. Full geom / stat / scale / facet / theme API, the `theme_nyt()`
integration, Databricks rendering, and "when NOT to use plotnine" are in
`references/grammar-of-graphics.md`.

## Publication Styling Reference (matplotlib)

Venue sizing, colorblind palettes (Okabe-Ito, Tol, Wong, viridis family), spines,
error bars, and multi-panel patterns are in `references/publication-guidelines.md`,
`references/journal-requirements.md`, `references/color-palettes.md`,
`references/style-guide.md`, and `references/matplotlib-examples.md`. The `.mplstyle`
files in `assets/` (`nature`, `publication`, `presentation`, `nyt`) and
`assets/style_presets.py` (`apply_publication_style`, `set_color_palette`,
`configure_for_journal`) implement these.

---

## Databricks Rendering

- Render any matplotlib/plotnine figure inline with `display(fig)` (call `p.draw()`
  first for a plotnine object to get the `Figure`). Plotly renders with `fig.show()`.
- Upload `assets/` helpers to DBFS (or add the repo path to `sys.path`) before
  importing `style_presets` / `swd_style`. Verify the upload before importing.
- Use explicit, reproducible figure sizes; do not rely on the notebook's default DPI.

---

## Resources

### references/ — SWD framework
- `context-setting.md`, `chart-selection.md`, `clutter-elimination.md`,
  `pre-attentive-attributes.md`, `design-principles.md`, `narrative-structure.md`,
  `audience-adaptation.md`

### references/ — styling & grammar
- `grammar-of-graphics.md` — plotnine geom/stat/scale/facet/theme API
- `publication-guidelines.md`, `journal-requirements.md`, `style-guide.md`
- `color-palettes.md`, `matplotlib-examples.md`, `data-visualization.md`

### references/ — general analysis charts
- `model-evaluation-viz.md` — ROC, PR, calibration, confusion-matrix charts
- `causal-inference-charts.md` — uplift, DiD, event-study charts

### assets/
- `swd_style.py` — SWD helpers (declutter, palette, annotate, insight title)
- `style_presets.py`, `color_palettes.py` — publication rcParams & colorblind palettes
- `nature.mplstyle`, `publication.mplstyle`, `presentation.mplstyle`, `nyt.mplstyle`

**Cross-skill:** `../banking-visualization/` for domain charts (KS, PSI, vintage,
fraud, customer analytics) and regulated-audience guidance. `../shared/nyt_theme.py`
for the unified NYT style across matplotlib, Plotly, and plotnine (`apply_nyt_all()`,
`theme_nyt()`, `NYT`, `FIG_SLIDE`). `../plotnine-visualization/` for the full plotnine
API (`import plotnine as p9`) — geoms, stats, scales, facets, themes — when a chart fits
the grammar of graphics but the SWD communication patterns here still apply.
