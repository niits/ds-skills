# Goal-Based Visualization Workflows

## Interactive EDA

Use Plotly first because hover, zoom, and selection support iterative investigation.

```python
import plotly.express as px

fig = px.scatter(
    df,
    x="amount",
    y="frequency",
    color="segment",
    hover_data=["customer_id"],
    opacity=0.6,
)
fig.show()
```

Use plotnine when statistical layers, facets, and declarative composition fit better;
fall back to matplotlib for unsupported or highly customized charts. Even exploratory
charts need one question, readable axes, and accessible colors.

## Static Paper or Journal Figure

Use matplotlib/seaborn by default and plotnine for naturally faceted/grouped/layered
structures. Route detailed needs as follows:

- Chart patterns: `data-visualization.md`.
- Uncertainty examples: `matplotlib-examples.md`.
- Palette selection: `color-palettes.md`.
- Caption and accessibility standards: `style-guide.md` and `publication-guidelines.md`.
- Venue dimensions, fonts, DPI, and file formats: target venue author guidelines.

## Stakeholder Presentation

Use matplotlib with wide sizing, large fonts, high contrast, direct labels, and one Big
Idea per slide. De-emphasize non-essential series.

```python
import matplotlib.pyplot as plt
from swd_style import apply_swd_palette, declutter, insight_title, label_bars

plt.rcParams.update({"font.size": 16, "axes.titlesize": 20})
fig, ax = plt.subplots(figsize=(13.33, 7.5))
# Plot, then apply declutter(), insight_title(), highlighting, and direct labels.
display(fig)
```

Use plotnine for grammar-based faceted/grouped slide charts. Use Plotly when the audience
must drill into an interactive dashboard or report.

## Runtime Helpers

`assets/swd_style.py` provides `declutter`, `apply_swd_palette`, `annotate_insight`,
`insight_title`, and `label_bars`. `assets/color_palettes.py` provides palette and
colormap selection. Upload helpers to DBFS or add the repository path to `sys.path`, and
verify availability before importing.
