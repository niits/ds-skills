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
ggplot(data, aes(...))
  + geom_*()        # what to draw
  + stat_*()        # optional: compute before drawing
  + scale_*()       # map data → visual properties
  + coord_*()       # coordinate system
  + facet_*()       # small multiples
  + theme_*()       # non-data ink (fonts, backgrounds)
  + theme()         # fine-tune individual elements
  + labs()          # titles, axis labels, legend titles
```

### Imports

```python
from plotnine import *
from plotnine.data import mpg, diamonds, economics, mtcars  # built-in datasets
```

### Saving / displaying

```python
p = ggplot(df, aes("x", "y")) + geom_point()
p.save("plot.png", width=6, height=4, dpi=200)  # export to file

# Databricks inline (preferred):
fig = p.draw()
display(fig)

# Jupyter inline — works automatically when plotnine detects Jupyter:
p  # just evaluate the object
```

---

## Aesthetic Mappings (`aes`)

`aes()` connects **column names** (as strings) to visual channels:

```python
aes(x="col_x", y="col_y", color="group", fill="group",
    size="value", shape="category", alpha="confidence",
    linetype="method", label="text_col")
```

- Map to a **variable** → put inside `aes()`
- Set to a **constant** → put outside `aes()` as a kwarg on the geom

```python
# color mapped to variable
geom_point(aes(color="species"))

# color fixed for all points
geom_point(color="steelblue", size=3)
```

### Staged evaluation

```python
# Use after_stat() to map a stat-computed variable
geom_bar(aes(y=after_stat("count / sum(count)")))  # proportions
stat_density_2d(aes(fill=after_stat("level")), geom="polygon")
```

---

## Geoms — Quick Reference

### Graphical primitives

```python
# Reference lines
+ geom_abline(intercept=0, slope=1)
+ geom_hline(aes(yintercept="val"))
+ geom_vline(aes(xintercept="val"))
+ geom_segment(aes(x="x0", y="y0", xend="x1", yend="y1"))
+ geom_spoke(aes(angle="theta", radius="r"))

# Paths / polygons
+ geom_path()           # connects in data order
+ geom_line()           # connects sorted by x
+ geom_step(direction="hv")
+ geom_polygon(aes(group="id"))
+ geom_rect(aes(xmin="x0", xmax="x1", ymin="y0", ymax="y1"))
+ geom_ribbon(aes(ymin="lo", ymax="hi"))
```

### One continuous variable

```python
+ geom_histogram(binwidth=5)              # aes: x; optional: fill, color
+ geom_freqpoly(binwidth=5)              # aes: x; line version of histogram
+ geom_density(kernel="gaussian")        # smoothed density
+ geom_dotplot()                         # stacked dots per bin
+ geom_area(stat="bin")
+ geom_qq(aes(sample="col"))             # quantile-quantile plot
```

### One discrete variable

```python
+ geom_bar()                             # aes: x; counts rows per category
```

### Two continuous variables

```python
+ geom_point()                           # scatter
+ geom_jitter(width=0.2, height=0)      # scatter with noise (for overplotting)
+ geom_text(aes(label="col"))
+ geom_label(aes(label="col"))          # text with background box
+ geom_rug(sides="bl")                  # marginal tick marks
+ geom_smooth(method="lm")              # trend line with CI; methods: lm, loess, glm
+ geom_quantile()                       # quantile regression lines
```

### One discrete + one continuous

```python
+ geom_col()                             # bar chart of pre-aggregated values; aes: x, y
+ geom_boxplot()                         # aes: x, y
+ geom_violin(scale="area")             # aes: x, y
+ geom_dotplot(binaxis="y", stackdir="center")
```

### Two discrete variables

```python
+ geom_count()                           # bubble size = frequency at (x, y)
```

### Continuous bivariate distribution

```python
+ geom_bin_2d(binwidth=[0.25, 500])     # aes: x, y; heatmap of counts
+ geom_density_2d()                     # contour lines of kernel density
+ geom_density_2d_filled()             # filled contours
```

### Three continuous variables (z surface)

```python
+ geom_contour(aes(z="z"))
+ geom_contour_filled(aes(fill="z"))
+ geom_raster(aes(fill="z"))            # fast heatmap (equal bins)
+ geom_tile(aes(fill="z"))             # heatmap (arbitrary sizes)
```

### Visualizing error / uncertainty

```python
j = ggplot(df, aes("group", "fit", ymin="fit-se", ymax="fit+se"))
j + geom_pointrange()
j + geom_errorbar(width=0.2)
j + geom_crossbar(fatten=2)
j + geom_linerange()
```

### Maps

```python
import geopandas as gpd
gdf = gpd.read_file(...)
ggplot(gdf) + geom_map(aes(fill="column"))
```

---

## Stats — Statistical Transformations

Stats compute new values before rendering. You can use `stat_*()` directly or override a geom's default `stat=` argument.

```python
# Distribution
+ stat_bin(binwidth=1, boundary=0)
+ stat_count(width=1)
+ stat_density(adjust=1, kernel="gaussian")
+ stat_ecdf(n=40)
+ stat_qq(aes(sample=range(100)))

# Bivariate
+ stat_bin_2d(bins=30)
+ stat_density_2d(contour=True, n=100)
+ stat_ellipse(level=0.95, type="t")   # confidence ellipse
+ stat_contour(aes(z="z"))
+ stat_summary_hex(aes(z="z"), bins=30, fun=max)
+ stat_summary_2d(aes(z="z"), bins=30, fun="mean")

# Models
+ stat_smooth(method="lm", formula="y ~ x", se=True, level=0.95)
+ stat_quantile(quantiles=(0.1, 0.9), formula="y ~ np.log(x)")

# Aggregation
+ stat_boxplot(coef=1.5)
+ stat_ydensity(kernel="gaussian", scale="area")
+ stat_summary(fun_y="mean", fun_ymin=lambda x: x.mean() - x.std(),
               fun_ymax=lambda x: x.mean() + x.std())

# Arbitrary function
import scipy.stats as stats
ggplot() + lims(x=(-5, 5)) + stat_function(fun=stats.norm.pdf, n=100)
```

---

## Scales

Scales control how data values map to visual properties.

### Position

```python
# Continuous axes
+ scale_x_continuous(name="Label", limits=(0, 100), breaks=[0,25,50,75,100])
+ scale_y_continuous(trans="log10")    # log scale
+ scale_x_log10()                      # shortcut
+ scale_x_sqrt()
+ scale_x_reverse()
+ scale_x_date(date_labels="%b %Y", date_breaks="3 months")
+ scale_x_datetime()

# Discrete axes
+ scale_x_discrete(limits=["a","b","c"])  # reorder / filter categories
```

### Color & Fill

```python
# Discrete
+ scale_color_manual(values=["#E69F00","#56B4E9","#009E73"])
+ scale_color_brewer(type="qual", palette="Set2")   # ColorBrewer palettes
+ scale_fill_brewer(type="seq", palette="Blues")

# Continuous
+ scale_color_gradient(low="white", high="steelblue")
+ scale_color_gradient2(low="blue", mid="white", high="red", midpoint=0)
+ scale_color_gradientn(colors=["#003f5c","#7a5195","#ef5675","#ffa600"])
+ scale_fill_cmap("viridis")            # use any matplotlib colormap
+ scale_fill_cmap_d("tab10")           # discrete version

# Identity (data IS the color)
+ scale_color_identity()
```

### Size, Shape, Alpha, Linetype

```python
+ scale_size_continuous(range=(1, 10))
+ scale_size_area(max_size=10)         # area proportional to value (preferred)
+ scale_shape_manual(values=["o","s","^","D","v"])
+ scale_alpha_continuous(range=(0.2, 1.0))
+ scale_linetype_manual(values=["solid","dashed","dotted"])
```

### Limits & Labels shortcuts

```python
+ lims(x=(0, 100), y=(0, 1))          # shorthand for limits
+ xlim(0, 100)
+ ylim(0, 1)
+ labs(title="Title", x="X Label", y="Y Label", color="Group",
       caption="Source: ...", subtitle="Subtitle")
```

---

## Facets — Small Multiples

```python
# Wrap panels in a grid (1D → 2D)
+ facet_wrap("~ category",            # or facets=("cat1","cat2")
             nrow=2, ncol=3,
             scales="free_y",          # "fixed" | "free" | "free_x" | "free_y"
             labeller="label_both")    # shows variable name + value

# Grid of two variables
+ facet_grid("row_var ~ col_var",
             scales="free",
             space="free_y")          # panel height proportional to data range
```

---

## Coordinate Systems

```python
+ coord_cartesian(xlim=(0, 10), ylim=(0, 5))   # zoom without dropping data
+ coord_flip()                                   # swap x and y axes
+ coord_fixed(ratio=1)                          # equal aspect ratio
+ coord_trans(x="log10", y="sqrt")             # transform coordinates
+ coord_polar(theta="y")                        # polar / pie-like charts
```

---

## Themes

### Built-in complete themes

```python
+ theme_bw()            # white bg, black gridlines — clean default
+ theme_minimal()       # white bg, faint gridlines, no border
+ theme_classic()       # white bg, no gridlines, axis lines only
+ theme_dark()          # dark bg — good for presentations
+ theme_gray()          # default ggplot2 gray bg
+ theme_seaborn()       # mimics seaborn defaults
+ theme_void()          # nothing — useful for maps
+ theme_538()           # FiveThirtyEight style
+ theme_xkcd()          # hand-drawn look
```

All accept `base_size` (font size in pt) and `base_family` (font name).

### Fine-grained customization

```python
+ theme(
    # Text
    axis_title=element_text(size=12, weight="bold"),
    axis_text_x=element_text(angle=45, ha="right"),
    legend_title=element_text(size=10),
    plot_title=element_text(size=14, weight="bold", ha="center"),

    # Lines & rectangles
    panel_grid_major=element_line(color="#e0e0e0", size=0.5),
    panel_grid_minor=element_blank(),
    panel_border=element_rect(color="black", fill=None),

    # Backgrounds
    panel_background=element_rect(fill="white"),
    plot_background=element_rect(fill="white"),
    legend_background=element_rect(fill="white", alpha=0),

    # Legend position
    legend_position="right",           # "top" | "bottom" | "left" | "right" | "none"
    legend_direction="vertical",
)
```

---

## Position Adjustments

Control how multiple geoms at the same x/y are rendered:

```python
geom_bar(position="stack")        # default for bar — stack on top
geom_bar(position="dodge")        # side by side
geom_bar(position="fill")         # normalize to 100%
geom_point(position=position_jitter(width=0.2, height=0))
geom_point(position=position_jitterdodge(jitter_width=0.1, dodge_width=0.8))
```

---

## Common Patterns

### Scatter with trend line

```python
(ggplot(df, aes("x", "y", color="group"))
 + geom_point(alpha=0.6, size=2)
 + geom_smooth(method="lm", se=True)
 + scale_color_brewer(type="qual", palette="Set1")
 + labs(title="X vs Y by Group", x="X Label", y="Y Label")
 + theme_minimal(base_size=11))
```

### Distribution comparison (violin + boxplot overlay)

```python
(ggplot(df, aes("category", "value", fill="category"))
 + geom_violin(alpha=0.6, show_legend=False)
 + geom_boxplot(width=0.1, fill="white", outlier_alpha=0.3)
 + scale_fill_brewer(type="qual", palette="Pastel1")
 + coord_flip()
 + theme_bw())
```

### Histogram with density overlay

```python
(ggplot(df, aes("value"))
 + geom_histogram(aes(y=after_stat("density")), binwidth=0.5,
                  fill="#4292c6", color="white", alpha=0.7)
 + geom_density(color="#08519c", size=1)
 + theme_classic())
```

### Heatmap (tile)

```python
(ggplot(df, aes("col_var", "row_var", fill="value"))
 + geom_tile(color="white", size=0.5)
 + geom_text(aes(label="value"), size=8, color="black")
 + scale_fill_gradient2(low="#2166ac", mid="white", high="#d6604d", midpoint=0)
 + theme_minimal()
 + theme(axis_text_x=element_text(angle=45, ha="right")))
```

### Faceted small multiples

```python
(ggplot(df, aes("x", "y"))
 + geom_line(aes(color="metric"))
 + facet_wrap("~ segment", nrow=2, scales="free_y")
 + scale_color_manual(values=["#E69F00", "#56B4E9", "#009E73"])
 + labs(title="Metrics by Segment")
 + theme_bw(base_size=10)
 + theme(strip_background=element_rect(fill="#f0f0f0"),
         strip_text=element_text(weight="bold")))
```

### Bar chart with value labels

```python
agg = df.groupby("category", as_index=False)["value"].mean()
(ggplot(agg, aes("reorder('category', 'value')", "value"))
 + geom_col(fill="#2c7bb6", width=0.7)
 + geom_text(aes(label="value"), nudge_y=0.5, size=9)
 + coord_flip()
 + labs(x=None, y="Mean Value")
 + theme_minimal()
 + theme(panel_grid_major_y=element_blank()))
```

### Time series with ribbon (confidence band)

```python
(ggplot(df, aes("date", "mean_val"))
 + geom_ribbon(aes(ymin="lo", ymax="hi"), alpha=0.2, fill="#2c7bb6")
 + geom_line(color="#2c7bb6", size=1)
 + scale_x_date(date_labels="%b %Y", date_breaks="3 months")
 + theme_bw()
 + theme(axis_text_x=element_text(angle=30, ha="right")))
```

### Bubble chart (size = 3rd variable)

```python
(ggplot(df, aes("x", "y", size="count", color="group"))
 + geom_point(alpha=0.7)
 + scale_size_area(max_size=20)
 + scale_color_brewer(type="qual", palette="Set2")
 + theme_minimal())
```

---

## Grammar Cheat Sheet

| Component | Function | What it controls |
|-----------|----------|-----------------|
| Data | `ggplot(data, aes(...))` | Default dataset + mappings |
| Geom | `geom_*()` | Visual mark type |
| Stat | `stat_*()` | Pre-render computation |
| Scale | `scale_*_*()` | Data → visual channel mapping |
| Coord | `coord_*()` | Coordinate space |
| Facet | `facet_wrap()` / `facet_grid()` | Panel layout |
| Theme | `theme_*()` + `theme()` | Non-data styling |
| Labels | `labs()` / `xlab()` / `ylab()` | Titles and axis labels |

### Aesthetic defaults by geom type

| Geom | Required aes | Common optional aes |
|------|-------------|---------------------|
| `geom_point` | x, y | color, fill, shape, size, alpha |
| `geom_line` | x, y | color, linetype, size, group |
| `geom_bar` | x | fill, color, alpha, weight |
| `geom_col` | x, y | fill, color, alpha |
| `geom_histogram` | x | fill, color, binwidth |
| `geom_boxplot` | x, y | color, fill, outlier_* |
| `geom_violin` | x, y | fill, color, scale |
| `geom_tile` | x, y, fill | color, width, height |
| `geom_text` | x, y, label | color, size, angle, hjust, vjust |
| `geom_smooth` | x, y | color, fill, method, se |
| `geom_errorbar` | x, ymin, ymax | color, width, size |

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

# Pandas
df_pd = pd.DataFrame({"x": [1,2,3], "y": [4,5,6], "g": ["a","b","c"]})
ggplot(df_pd, aes("x", "y", color="g")) + geom_point()

# Polars
df_pl = pl.DataFrame({"x": [1,2,3], "y": [4,5,6], "g": ["a","b","c"]})
ggplot(df_pl, aes("x", "y", color="g")) + geom_point()
```

### Reorder categorical axis

```python
# pandas: use Categorical with ordered=True
df["category"] = pd.Categorical(df["category"],
                                 categories=df.groupby("category")["value"].mean()
                                              .sort_values().index,
                                 ordered=True)
# then map normally
aes(x="category", y="value")

# in aes directly (reorder by another column)
aes(x="reorder('category', 'value')", y="value")
```

---

## Colorblind-Safe Palettes

```python
# Okabe-Ito (8 colors, verified colorblind-safe)
OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
             "#0072B2", "#D55E00", "#CC79A7", "#000000"]

scale_color_manual(values=OKABE_ITO)

# ColorBrewer (built-in)
scale_color_brewer(type="qual", palette="Set2")   # 8 colors
scale_color_brewer(type="qual", palette="Dark2")  # 8 colors, darker

# Sequential (for ordered/continuous data)
scale_fill_cmap("viridis")   # viridis, plasma, cividis — perceptually uniform
scale_fill_cmap("Blues")
```

---

## Databricks Display

```python
# Method 1: draw() + display()
p = (ggplot(df, aes("x", "y")) + geom_point())
fig = p.draw()
display(fig)

# Method 2: save to BytesIO and display
import io
buf = io.BytesIO()
p.save(buf, format="png", width=8, height=5, dpi=150, verbose=False)
buf.seek(0)
displayHTML(f'<img src="data:image/png;base64,{__import__("base64").b64encode(buf.read()).decode()}">')
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| `Column 'x' not in dataframe` | Column names in `aes()` must match exactly — they are strings |
| Bars showing counts instead of values | Use `geom_col()` (pre-aggregated) not `geom_bar()` |
| Categorical ordering wrong | Set `pd.Categorical` with `ordered=True` or use `reorder()` in `aes()` |
| Legend key order wrong | Use `scale_*_manual(breaks=[...])` to specify order |
| Overlapping x-axis labels | Add `+ theme(axis_text_x=element_text(angle=45, ha="right"))` |
| Plot not showing in Databricks | Use `display(p.draw())` not `p.show()` or bare `p` |
| Color not mapping correctly | Ensure column is categorical/string type, not numeric |
| Smoothing line ignores groups | Add `aes(group="group_col")` to `geom_smooth()` |
| `after_stat` not recognized | Use full `after_stat("var_name")` syntax, not shorthand |

---

## See Also

- `references/geom-gallery.md` — Visual examples of every geom
- `references/theme-cookbook.md` — Theme recipes for common styles (NYT, FT, dark mode)
- Plotnine docs: https://plotnine.org
- Cheatsheet: https://posit.co/resources/cheatsheets/ (plotnine)
