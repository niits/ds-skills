---
name: plotnine-visualization
description: Grammar-of-graphics visualizations in Python using plotnine (ggplot2 port). Use for EDA, business dashboards, publication figures, and any declarative chart built by layering geoms + aesthetics + scales + themes. Prefer this over matplotlib/seaborn when the data has natural grouping structure, faceting needs, or when ggplot2-style declarative syntax is desired.
license: MIT license
metadata:
    skill-author: ds-skills
    adapted-for: Databricks / Jupyter notebooks
---

# Plotnine Visualization

## Overview

Plotnine implements the **grammar of graphics** — every plot is built from:

```
p9.ggplot(data, p9.aes(...))
  + p9.geom_*()       # what to draw
  + p9.stat_*()       # optional: compute before drawing
  + p9.scale_*()      # map data → visual properties
  + p9.coord_*()      # coordinate system
  + p9.facet_*()      # small multiples
  + p9.theme_*()      # non-data ink (fonts, backgrounds)
  + p9.theme()        # fine-tune individual elements
  + p9.labs()         # titles, axis labels, legend titles
```

### Imports

```python
import plotnine as p9
from plotnine.data import mpg, diamonds, economics, mtcars, seals  # built-in datasets
```

### Saving / displaying

```python
p = p9.ggplot(df, p9.aes("x", "y")) + p9.geom_point()
p.save("plot.png", width=6, height=4, dpi=200)  # export to file

# Databricks inline (preferred):
fig = p.draw()
display(fig)

# Jupyter inline — works automatically when plotnine detects Jupyter:
p  # just evaluate the object
```

---

## Aesthetic Mappings (`p9.aes`)

`p9.aes()` connects **column names** (as strings) to visual channels:

```python
p9.aes(x="col_x", y="col_y", color="group", fill="group",
       size="value", shape="category", alpha="confidence",
       linetype="method", label="text_col")
```

- Map to a **variable** → put inside `p9.aes()`
- Set to a **constant** → put outside `p9.aes()` as a kwarg on the geom

```python
# color mapped to variable
p9.geom_point(p9.aes(color="species"))

# color fixed for all points
p9.geom_point(color="steelblue", size=3)
```

### Staged evaluation

```python
# Use p9.after_stat() to map a stat-computed variable
p9.geom_bar(p9.aes(y=p9.after_stat("count / sum(count)")))   # proportions
p9.stat_density_2d(p9.aes(fill=p9.after_stat("level")), geom="polygon")
```

---

## Geoms — Quick Reference

### Graphical primitives

```python
# Reference lines
+ p9.geom_abline(intercept=0, slope=1)
+ p9.geom_hline(p9.aes(yintercept="val"))
+ p9.geom_vline(p9.aes(xintercept="val"))
+ p9.geom_segment(p9.aes(x="x0", y="y0", xend="x1", yend="y1"))
+ p9.geom_spoke(p9.aes(angle="theta", radius="r"))

# Paths / polygons
+ p9.geom_path()           # connects in data order
+ p9.geom_line()           # connects sorted by x
+ p9.geom_step(direction="hv")
+ p9.geom_polygon(p9.aes(group="id"))
+ p9.geom_rect(p9.aes(xmin="x0", xmax="x1", ymin="y0", ymax="y1"))
+ p9.geom_ribbon(p9.aes(ymin="lo", ymax="hi"))
```

### One continuous variable

```python
+ p9.geom_histogram(binwidth=5)          # aes: x; optional: fill, color
+ p9.geom_freqpoly(binwidth=5)          # aes: x; line version of histogram
+ p9.geom_density(kernel="gaussian")    # smoothed density
+ p9.geom_dotplot()                     # stacked dots per bin
+ p9.geom_area(stat="bin")
+ p9.geom_qq(p9.aes(sample="col"))      # quantile-quantile plot
```

### One discrete variable

```python
+ p9.geom_bar()                         # aes: x; counts rows per category
```

### Two continuous variables

```python
+ p9.geom_point()                                  # scatter
+ p9.geom_jitter(width=0.2, height=0)             # scatter with noise (for overplotting)
+ p9.geom_text(p9.aes(label="col"))
+ p9.geom_label(p9.aes(label="col"))              # text with background box
+ p9.geom_rug(sides="bl")                         # marginal tick marks
+ p9.geom_smooth(method="lm")                     # trend line with CI; methods: lm, loess, glm
+ p9.geom_quantile()                              # quantile regression lines
```

### One discrete + one continuous

```python
+ p9.geom_col()                                   # bar chart of pre-aggregated values; aes: x, y
+ p9.geom_boxplot()                               # aes: x, y
+ p9.geom_violin(scale="area")                   # aes: x, y
+ p9.geom_dotplot(binaxis="y", stackdir="center")
```

### Two discrete variables

```python
+ p9.geom_count()                                 # bubble size = frequency at (x, y)
```

### Continuous bivariate distribution

```python
+ p9.geom_bin_2d(binwidth=[0.25, 500])           # aes: x, y; heatmap of counts
+ p9.geom_density_2d()                           # contour lines of kernel density
+ p9.geom_density_2d_filled()                   # filled contours
```

### Three continuous variables (z surface)

```python
+ p9.geom_contour(p9.aes(z="z"))
+ p9.geom_contour_filled(p9.aes(fill="z"))
+ p9.geom_raster(p9.aes(fill="z"))              # fast heatmap (equal bins)
+ p9.geom_tile(p9.aes(fill="z"))               # heatmap (arbitrary sizes)
```

### Visualizing error / uncertainty

```python
j = p9.ggplot(df, p9.aes("group", "fit", ymin="fit-se", ymax="fit+se"))
j + p9.geom_pointrange()
j + p9.geom_errorbar(width=0.2)
j + p9.geom_crossbar(fatten=2)
j + p9.geom_linerange()
```

### Maps

```python
import geopandas as gpd
gdf = gpd.read_file(...)
p9.ggplot(gdf) + p9.geom_map(p9.aes(fill="column"))
```

---

## Stats — Statistical Transformations

Stats compute new values before rendering. You can use `p9.stat_*()` directly or override a geom's default `stat=` argument.

```python
# Distribution
+ p9.stat_bin(binwidth=1, boundary=0)
+ p9.stat_count(width=1)
+ p9.stat_density(adjust=1, kernel="gaussian")
+ p9.stat_ecdf(n=40)
+ p9.stat_qq(p9.aes(sample=range(100)))

# Bivariate
+ p9.stat_bin_2d(bins=30)
+ p9.stat_density_2d(contour=True, n=100)
+ p9.stat_ellipse(level=0.95, type="t")          # confidence ellipse
+ p9.stat_contour(p9.aes(z="z"))
+ p9.stat_summary_hex(p9.aes(z="z"), bins=30, fun=max)
+ p9.stat_summary_2d(p9.aes(z="z"), bins=30, fun="mean")

# Models
+ p9.stat_smooth(method="lm", formula="y ~ x", se=True, level=0.95)
+ p9.stat_quantile(quantiles=(0.1, 0.9), formula="y ~ np.log(x)")

# Aggregation
+ p9.stat_boxplot(coef=1.5)
+ p9.stat_ydensity(kernel="gaussian", scale="area")
+ p9.stat_summary(fun_y="mean", fun_ymin=lambda x: x.mean() - x.std(),
                  fun_ymax=lambda x: x.mean() + x.std())

# Arbitrary function
import scipy.stats as stats
p9.ggplot() + p9.lims(x=(-5, 5)) + p9.stat_function(fun=stats.norm.pdf, n=100)
```

---

## Scales

Scales control how data values map to visual properties.

### Position

```python
# Continuous axes
+ p9.scale_x_continuous(name="Label", limits=(0, 100), breaks=[0,25,50,75,100])
+ p9.scale_y_continuous(trans="log10")    # log scale
+ p9.scale_x_log10()                      # shortcut
+ p9.scale_x_sqrt()
+ p9.scale_x_reverse()
+ p9.scale_x_date(date_labels="%b %Y", date_breaks="3 months")
+ p9.scale_x_datetime()

# Discrete axes
+ p9.scale_x_discrete(limits=["a","b","c"])   # reorder / filter categories
```

### Color & Fill

```python
# Discrete
+ p9.scale_color_manual(values=["#E69F00","#56B4E9","#009E73"])
+ p9.scale_color_brewer(type="qual", palette="Set2")   # ColorBrewer palettes
+ p9.scale_fill_brewer(type="seq", palette="Blues")

# Continuous
+ p9.scale_color_gradient(low="white", high="steelblue")
+ p9.scale_color_gradient2(low="blue", mid="white", high="red", midpoint=0)
+ p9.scale_color_gradientn(colors=["#003f5c","#7a5195","#ef5675","#ffa600"])
+ p9.scale_fill_cmap("viridis")           # use any matplotlib colormap
+ p9.scale_fill_cmap_d("tab10")          # discrete version

# Identity (data IS the color)
+ p9.scale_color_identity()
```

### Size, Shape, Alpha, Linetype

```python
+ p9.scale_size_continuous(range=(1, 10))
+ p9.scale_size_area(max_size=10)         # area proportional to value (preferred)
+ p9.scale_shape_manual(values=["o","s","^","D","v"])
+ p9.scale_alpha_continuous(range=(0.2, 1.0))
+ p9.scale_linetype_manual(values=["solid","dashed","dotted"])
```

### Limits & Labels shortcuts

```python
+ p9.lims(x=(0, 100), y=(0, 1))
+ p9.xlim(0, 100)
+ p9.ylim(0, 1)
+ p9.labs(title="Title", x="X Label", y="Y Label", color="Group",
          caption="Source: ...", subtitle="Subtitle")
```

---

## Facets — Small Multiples

```python
# Wrap panels in a grid (1D → 2D)
+ p9.facet_wrap("~ category",             # or facets=("cat1","cat2")
                nrow=2, ncol=3,
                scales="free_y",           # "fixed" | "free" | "free_x" | "free_y"
                labeller="label_both")     # shows variable name + value

# Grid of two variables
+ p9.facet_grid("row_var ~ col_var",
                scales="free",
                space="free_y")           # panel height proportional to data range
```

---

## Coordinate Systems

```python
+ p9.coord_cartesian(xlim=(0, 10), ylim=(0, 5))   # zoom without dropping data
+ p9.coord_flip()                                   # swap x and y axes
+ p9.coord_fixed(ratio=1)                          # equal aspect ratio
+ p9.coord_trans(x="log10", y="sqrt")             # transform coordinates
+ p9.coord_polar(theta="y")                        # polar / pie-like charts
```

---

## Themes

### Built-in complete themes

```python
+ p9.theme_bw()         # white bg, black gridlines — clean default
+ p9.theme_minimal()    # white bg, faint gridlines, no border
+ p9.theme_classic()    # white bg, no gridlines, axis lines only
+ p9.theme_dark()       # dark bg — good for presentations
+ p9.theme_gray()       # default ggplot2 gray bg
+ p9.theme_seaborn()    # mimics seaborn defaults
+ p9.theme_void()       # nothing — useful for maps
+ p9.theme_538()        # FiveThirtyEight style
+ p9.theme_xkcd()       # hand-drawn look
```

All accept `base_size` (font size in pt) and `base_family` (font name).

### Fine-grained customization

```python
+ p9.theme(
    # Text
    axis_title=p9.element_text(size=12, weight="bold"),
    axis_text_x=p9.element_text(angle=45, ha="right"),
    legend_title=p9.element_text(size=10),
    plot_title=p9.element_text(size=14, weight="bold", ha="center"),

    # Lines & rectangles
    panel_grid_major=p9.element_line(color="#e0e0e0", size=0.5),
    panel_grid_minor=p9.element_blank(),
    panel_border=p9.element_rect(color="black", fill=None),

    # Backgrounds
    panel_background=p9.element_rect(fill="white"),
    plot_background=p9.element_rect(fill="white"),
    legend_background=p9.element_rect(fill="white", alpha=0),

    # Legend position
    legend_position="right",    # "top" | "bottom" | "left" | "right" | "none"
    legend_direction="vertical",
)
```

---

## Position Adjustments

Control how multiple geoms at the same x/y are rendered:

```python
p9.geom_bar(position="stack")        # default for bar — stack on top
p9.geom_bar(position="dodge")        # side by side
p9.geom_bar(position="fill")         # normalize to 100%
p9.geom_point(position=p9.position_jitter(width=0.2, height=0))
p9.geom_point(position=p9.position_jitterdodge(jitter_width=0.1, dodge_width=0.8))
```

---

## Common Patterns

### Scatter with trend line

```python
(p9.ggplot(df, p9.aes("x", "y", color="group"))
 + p9.geom_point(alpha=0.6, size=2)
 + p9.geom_smooth(method="lm", se=True)
 + p9.scale_color_brewer(type="qual", palette="Set1")
 + p9.labs(title="X vs Y by Group", x="X Label", y="Y Label")
 + p9.theme_minimal(base_size=11))
```

### Distribution comparison (violin + boxplot overlay)

```python
(p9.ggplot(df, p9.aes("category", "value", fill="category"))
 + p9.geom_violin(alpha=0.6, show_legend=False)
 + p9.geom_boxplot(width=0.1, fill="white", outlier_alpha=0.3)
 + p9.scale_fill_brewer(type="qual", palette="Pastel1")
 + p9.coord_flip()
 + p9.theme_bw())
```

### Histogram with density overlay

```python
(p9.ggplot(df, p9.aes("value"))
 + p9.geom_histogram(p9.aes(y=p9.after_stat("density")), binwidth=0.5,
                     fill="#4292c6", color="white", alpha=0.7)
 + p9.geom_density(color="#08519c", size=1)
 + p9.theme_classic())
```

### Heatmap (tile)

```python
(p9.ggplot(df, p9.aes("col_var", "row_var", fill="value"))
 + p9.geom_tile(color="white", size=0.5)
 + p9.geom_text(p9.aes(label="value"), size=8, color="black")
 + p9.scale_fill_gradient2(low="#2166ac", mid="white", high="#d6604d", midpoint=0)
 + p9.theme_minimal()
 + p9.theme(axis_text_x=p9.element_text(angle=45, ha="right")))
```

### Faceted small multiples

```python
(p9.ggplot(df, p9.aes("x", "y"))
 + p9.geom_line(p9.aes(color="metric"))
 + p9.facet_wrap("~ segment", nrow=2, scales="free_y")
 + p9.scale_color_manual(values=["#E69F00", "#56B4E9", "#009E73"])
 + p9.labs(title="Metrics by Segment")
 + p9.theme_bw(base_size=10)
 + p9.theme(strip_background=p9.element_rect(fill="#f0f0f0"),
            strip_text=p9.element_text(weight="bold")))
```

### Bar chart with value labels

```python
agg = df.groupby("category", as_index=False)["value"].mean()
(p9.ggplot(agg, p9.aes("reorder('category', 'value')", "value"))
 + p9.geom_col(fill="#2c7bb6", width=0.7)
 + p9.geom_text(p9.aes(label="value"), nudge_y=0.5, size=9)
 + p9.coord_flip()
 + p9.labs(x=None, y="Mean Value")
 + p9.theme_minimal()
 + p9.theme(panel_grid_major_y=p9.element_blank()))
```

### Time series with ribbon (confidence band)

```python
(p9.ggplot(df, p9.aes("date", "mean_val"))
 + p9.geom_ribbon(p9.aes(ymin="lo", ymax="hi"), alpha=0.2, fill="#2c7bb6")
 + p9.geom_line(color="#2c7bb6", size=1)
 + p9.scale_x_date(date_labels="%b %Y", date_breaks="3 months")
 + p9.theme_bw()
 + p9.theme(axis_text_x=p9.element_text(angle=30, ha="right")))
```

### Bubble chart (size = 3rd variable)

```python
(p9.ggplot(df, p9.aes("x", "y", size="count", color="group"))
 + p9.geom_point(alpha=0.7)
 + p9.scale_size_area(max_size=20)
 + p9.scale_color_brewer(type="qual", palette="Set2")
 + p9.theme_minimal())
```

---

## Grammar Cheat Sheet

| Component | Function | What it controls |
|-----------|----------|-----------------|
| Data | `p9.ggplot(data, p9.aes(...))` | Default dataset + mappings |
| Geom | `p9.geom_*()` | Visual mark type |
| Stat | `p9.stat_*()` | Pre-render computation |
| Scale | `p9.scale_*_*()` | Data → visual channel mapping |
| Coord | `p9.coord_*()` | Coordinate space |
| Facet | `p9.facet_wrap()` / `p9.facet_grid()` | Panel layout |
| Theme | `p9.theme_*()` + `p9.theme()` | Non-data styling |
| Labels | `p9.labs()` / `p9.xlim()` / `p9.ylim()` | Titles and axis labels |

### Aesthetic defaults by geom type

| Geom | Required aes | Common optional aes |
|------|-------------|---------------------|
| `p9.geom_point` | x, y | color, fill, shape, size, alpha |
| `p9.geom_line` | x, y | color, linetype, size, group |
| `p9.geom_bar` | x | fill, color, alpha, weight |
| `p9.geom_col` | x, y | fill, color, alpha |
| `p9.geom_histogram` | x | fill, color, binwidth |
| `p9.geom_boxplot` | x, y | color, fill, outlier_* |
| `p9.geom_violin` | x, y | fill, color, scale |
| `p9.geom_tile` | x, y, fill | color, width, height |
| `p9.geom_text` | x, y, label | color, size, angle, hjust, vjust |
| `p9.geom_smooth` | x, y | color, fill, method, se |
| `p9.geom_errorbar` | x, ymin, ymax | color, width, size |

---

## Common Property Values

| Property | Values |
|----------|--------|
| `color`/`fill` | CSS name (`"steelblue"`) or hex (`"#2c7bb6"`) |
| `linetype` | `"solid"`, `"dashed"`, `"dotted"`, `"dashdot"` or tuple |
| `shape` | `"o"` (circle), `"s"` (square), `"^"` (triangle), `"D"` (diamond), `"+"`, `"x"` |
| `size` | numeric, in points |
| `alpha` | 0.0 (transparent) to 1.0 (opaque) |
| `fontface` | `"plain"`, `"bold"`, `"italic"`, `"bold.italic"` |
| `hjust` | 0 (left) to 1 (right), 0.5 (center) |
| `vjust` | 0 (bottom) to 1 (top), 0.5 (middle) |

---

## Working with DataFrames

Plotnine works with **pandas** DataFrames (default) and **polars** DataFrames.

```python
import pandas as pd
import polars as pl
import plotnine as p9

# Pandas
df_pd = pd.DataFrame({"x": [1,2,3], "y": [4,5,6], "g": ["a","b","c"]})
p9.ggplot(df_pd, p9.aes("x", "y", color="g")) + p9.geom_point()

# Polars
df_pl = pl.DataFrame({"x": [1,2,3], "y": [4,5,6], "g": ["a","b","c"]})
p9.ggplot(df_pl, p9.aes("x", "y", color="g")) + p9.geom_point()
```

### Reorder categorical axis

```python
# pandas: use Categorical with ordered=True
df["category"] = pd.Categorical(
    df["category"],
    categories=df.groupby("category")["value"].mean().sort_values().index,
    ordered=True,
)
# then map normally
p9.aes(x="category", y="value")

# inline reorder in aes
p9.aes(x="reorder('category', 'value')", y="value")
```

---

## Colorblind-Safe Palettes

```python
# Okabe-Ito (8 colors, verified colorblind-safe)
OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
             "#0072B2", "#D55E00", "#CC79A7", "#000000"]

p9.scale_color_manual(values=OKABE_ITO)

# ColorBrewer (built-in)
p9.scale_color_brewer(type="qual", palette="Set2")   # 8 colors
p9.scale_color_brewer(type="qual", palette="Dark2")  # 8 colors, darker

# Sequential (for ordered/continuous data)
p9.scale_fill_cmap("viridis")   # viridis, plasma, cividis — perceptually uniform
p9.scale_fill_cmap("Blues")
```

---

## Databricks Display

```python
# Method 1: draw() + display()
p = (p9.ggplot(df, p9.aes("x", "y")) + p9.geom_point())
fig = p.draw()
display(fig)

# Method 2: save to BytesIO and display
import io, base64
buf = io.BytesIO()
p.save(buf, format="png", width=8, height=5, dpi=150, verbose=False)
buf.seek(0)
displayHTML(f'<img src="data:image/png;base64,{base64.b64encode(buf.read()).decode()}">')
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| `Column 'x' not in dataframe` | Column names in `p9.aes()` must match exactly — they are strings |
| Bars showing counts instead of values | Use `p9.geom_col()` (pre-aggregated) not `p9.geom_bar()` |
| Categorical ordering wrong | Set `pd.Categorical` with `ordered=True` or use `reorder()` in `p9.aes()` |
| Legend key order wrong | Use `p9.scale_*_manual(breaks=[...])` to specify order |
| Overlapping x-axis labels | Add `+ p9.theme(axis_text_x=p9.element_text(angle=45, ha="right"))` |
| Plot not showing in Databricks | Use `display(p.draw())` not `p.show()` or bare `p` |
| Color not mapping correctly | Ensure column is categorical/string type, not numeric |
| Smoothing line ignores groups | Add `p9.aes(group="group_col")` to `p9.geom_smooth()` |
| `after_stat` not recognized | Use `p9.after_stat("var_name")` — don't call it bare |

---

## Shared NYT Theme (cross-skill)

The shared `nyt_theme.py` module provides a unified NYT visual style used across matplotlib, Plotly, and plotnine. Use it instead of the local NYT recipe in `theme-cookbook.md` when working within the `visualization` (Storytelling-with-Data) framework.

```python
import sys
sys.path.insert(0, '/dbfs/FileStore/ds-skills/shared')

import plotnine as p9
from nyt_theme import theme_nyt, NYT

(p9.ggplot(df, p9.aes("date", "value", color="group"))
 + p9.geom_line(size=1.5)
 + p9.scale_color_manual(values=NYT.PALETTE)
 + p9.labs(title="Title IS the takeaway", x="", y="")
 + theme_nyt()              # base_size=15 — slide default
 # + theme_nyt(base_size=11)  # for notebook / Databricks inline
)
```

Key exports from `nyt_theme.py`:
- `theme_nyt(base_size=15)` — plotnine theme object, add with `+`
- `NYT.PALETTE` — ordered list of NYT colors
- `NYT.HIGHLIGHT` — blue accent (positive emphasis)
- `NYT.BASELINE` — `#CCCCCC` gray (context series)
- `NYT.INK`, `NYT.MID`, `NYT.LIGHT` — text shades

---

## Domain Chart Patterns

When building charts for **credit & risk analytics, fraud, customer analytics, or causal inference**, the `visualization` and `banking-visualization` skills have ready-to-run code for specialized charts:

| Domain | Charts | Reference |
|--------|--------|-----------|
| Credit & Risk | KS curve, vintage, migration matrix, PSI, bullet chart | `../banking-visualization/references/credit-risk-charts.md` |
| Model Evaluation | ROC, calibration, SHAP waterfall, lift/gain | `../visualization/references/model-evaluation-viz.md` |
| Fraud | Anomaly time series, calendar heatmap, rolling z-score | `../banking-visualization/references/fraud-detection-charts.md` |
| Customer | Cohort retention, funnel, A/B test CI | `../banking-visualization/references/customer-analytics-charts.md` |
| Causal Inference | Coefficient plot, parallel trends, RDD | `../visualization/references/causal-inference-charts.md` |

Those charts use matplotlib/seaborn. For new work where the domain chart can be built declaratively, prefer plotnine + the patterns in this skill.

---

## See Also

- `references/geom-gallery.md` — Visual examples of every geom
- `references/theme-cookbook.md` — Theme recipes (NYT, FT, dark mode, academic)
- `../shared/nyt_theme.py` — Shared NYT style for matplotlib + Plotly + plotnine
- `../visualization/SKILL.md` — Communication framework + domain chart patterns
- Plotnine docs: https://plotnine.org
- Cheatsheet: https://posit.co/resources/cheatsheets/ (plotnine)
