---
name: visualization
description: Make charts that communicate for data science on Databricks. Use when building exploratory, publication, model-evaluation, causal-inference, or stakeholder figures.
allowed-tools: Read Write Edit Bash
license: MIT; third-party notices apply
metadata:
    skill-author: ds-skills
    domain: general
    adapted-for: Databricks (display(fig) for inline rendering; %md cells for narrative)
---

# Visualization for Data Scientists

## Principles

Apply Storytelling with Data (SWD) to every chart and choose the renderer by output goal,
not habit. Publication submission mechanics such as venue-specific dimensions and DPI
remain governed by the target venue.

## Library Routing

- **Interactive EDA:** Plotly first; fall back to plotnine for grammar-based statistical
  layers, then matplotlib for full control.
- **Static paper/journal figure:** matplotlib/seaborn; plotnine for naturally faceted,
  grouped, or layered grammar-of-graphics work.
- **Stakeholder slide:** matplotlib with slide-scale typography and direct labels.
- **Interactive dashboard/report:** Plotly.
- **Model evaluation:** `references/model-evaluation-viz.md`.
- **Causal inference:** `references/causal-inference-charts.md`.

Implementation patterns and fallbacks are in `references/goal-based-workflows.md`.

## Workflow

1. **Audit before plotting.** Establish grain, filters, time semantics, missingness,
   duplicates, weights, aggregation, denominator, and support. Use
   `references/chart-audit-and-delivery.md`.
2. **State one Big Idea.** If the intended takeaway cannot be written in one sentence,
   do not plot yet. Use `references/context-setting.md`.
3. **Choose the chart.** Match form to message with `references/chart-selection.md`.
4. **Declutter.** Remove non-informative borders, gridlines, legends, and decoration via
   `references/clutter-elimination.md`.
5. **Focus attention.** Use position, color, size, labels, and redundant encodings from
   `references/pre-attentive-attributes.md` and `references/color-palettes.md`.
6. **Design and narrate.** Apply alignment, whitespace, typography, an insight title,
   and useful annotation using `references/design-principles.md`,
   `references/narrative-structure.md`, and `references/audience-adaptation.md`.
7. **Validate and deliver.** Check statistical honesty, accessibility, rendering, and
   adjacent data using `references/chart-audit-and-delivery.md`.

## Hard Rules

- `BLOCKED`: denominator, aggregation, or missing-data treatment cannot be explained.
- Use causal language only when the identification design supports it.
- Retain material uncertainty, limitations, subgroup harms, period, denominator, and source.
- Do not encode essential meaning with color or hover alone.
- Every delivered chart needs a concise takeaway, meaningful alt text, and accessible
  adjacent data or a downloadable table.
- In Databricks, use `display(fig)` for matplotlib; call `p.draw()` before displaying a
  plotnine figure; use `fig.show()` for Plotly.

## References

- `references/goal-based-workflows.md` - renderer choice and goal-specific implementation.
- `references/chart-audit-and-delivery.md` - pre-plot audit, accessibility, and delivery.
- `references/context-setting.md`, `chart-selection.md`, `clutter-elimination.md` - SWD setup.
- `references/pre-attentive-attributes.md`, `design-principles.md`,
  `narrative-structure.md`, `audience-adaptation.md` - focus and communication.
- `references/grammar-of-graphics.md` - plotnine API and appropriate uses.
- `references/data-visualization.md`, `matplotlib-examples.md` - patterns and code.
- `references/color-palettes.md`, `publication-guidelines.md`, `style-guide.md` - color,
  rigor, captions, and accessibility.
- `references/model-evaluation-viz.md`, `causal-inference-charts.md` - specialist charts.
- `assets/swd_style.py`, `assets/color_palettes.py` - reusable matplotlib helpers.
