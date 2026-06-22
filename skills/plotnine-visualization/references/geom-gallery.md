# Geom Gallery — Plotnine

Visual reference for choosing the right geom. Each entry shows the minimum working example.

```python
import plotnine as p9
from plotnine.data import mpg, diamonds, economics, mtcars, seals
```

---

## One Variable

### Continuous distribution

```python
# Histogram
(p9.ggplot(mpg, p9.aes("hwy"))
 + p9.geom_histogram(binwidth=2, fill="#4292c6", color="white"))

# Density curve
(p9.ggplot(mpg, p9.aes("hwy"))
 + p9.geom_density(fill="#4292c6", alpha=0.5))

# Frequency polygon (histogram as lines)
(p9.ggplot(mpg, p9.aes("hwy", color="drv"))
 + p9.geom_freqpoly(binwidth=2))

# Dotplot (stacked dots)
(p9.ggplot(mpg, p9.aes("hwy"))
 + p9.geom_dotplot(binwidth=1))

# ECDF (cumulative distribution)
(p9.ggplot(mpg, p9.aes("hwy"))
 + p9.stat_ecdf())
```

### Discrete counts

```python
# Bar chart (count rows)
(p9.ggplot(mpg, p9.aes("class"))
 + p9.geom_bar(fill="#4292c6"))
```

---

## Two Variables

### Continuous × Continuous

```python
# Scatter
(p9.ggplot(mpg, p9.aes("cty", "hwy"))
 + p9.geom_point())

# Scatter with overplotting fix
(p9.ggplot(mpg, p9.aes("cty", "hwy"))
 + p9.geom_jitter(width=0.3, height=0.3, alpha=0.5))

# Trend line
(p9.ggplot(mpg, p9.aes("displ", "hwy"))
 + p9.geom_point()
 + p9.geom_smooth(method="lm", se=True))

# Quantile regression
(p9.ggplot(mpg, p9.aes("displ", "hwy"))
 + p9.geom_quantile(quantiles=(0.25, 0.5, 0.75)))

# 2D histogram (bin_2d)
(p9.ggplot(diamonds, p9.aes("carat", "price"))
 + p9.geom_bin_2d(binwidth=(0.1, 500)))

# 2D density contours
(p9.ggplot(mpg, p9.aes("cty", "hwy"))
 + p9.geom_density_2d())
```

### Discrete × Continuous

```python
# Boxplot
(p9.ggplot(mpg, p9.aes("class", "hwy"))
 + p9.geom_boxplot()
 + p9.coord_flip())

# Violin
(p9.ggplot(mpg, p9.aes("class", "hwy", fill="class"))
 + p9.geom_violin()
 + p9.geom_boxplot(width=0.1, fill="white")
 + p9.coord_flip()
 + p9.theme(legend_position="none"))

# Column (pre-aggregated bar)
import pandas as pd
agg = mpg.groupby("class", as_index=False)["hwy"].mean()
(p9.ggplot(agg, p9.aes("class", "hwy"))
 + p9.geom_col(fill="#4292c6")
 + p9.coord_flip())

# Points with error bars
(p9.ggplot(agg, p9.aes("class", "hwy"))
 + p9.geom_point(size=3)
 + p9.geom_errorbar(p9.aes(ymin="hwy-2", ymax="hwy+2"), width=0.2)
 + p9.coord_flip())
```

### Discrete × Discrete

```python
# Count bubbles
(p9.ggplot(mpg, p9.aes("class", "drv"))
 + p9.geom_count())
```

---

## Three Variables

### z-surface (continuous x, y, z)

```python
import polars as pl

seals_pl = pl.DataFrame(seals).with_columns(
    z=(pl.col("delta_long")**2 + pl.col("delta_lat")**2).sqrt()
)

# Contour lines
(p9.ggplot(seals_pl, p9.aes("long", "lat"))
 + p9.geom_contour(p9.aes(z="z")))

# Filled contours
(p9.ggplot(seals_pl, p9.aes("long", "lat"))
 + p9.geom_contour_filled(p9.aes(fill="z")))

# Raster (fast heatmap for equal-spaced grids)
(p9.ggplot(seals_pl, p9.aes("long", "lat"))
 + p9.geom_raster(p9.aes(fill="z")))

# Tile (heatmap for arbitrary grid)
(p9.ggplot(df, p9.aes("x_cat", "y_cat", fill="value"))
 + p9.geom_tile(color="white", size=0.5)
 + p9.scale_fill_gradient2(low="#2166ac", mid="white", high="#d6604d", midpoint=0))
```

---

## Time Series

```python
# Line chart
(p9.ggplot(economics, p9.aes("date", "unemploy"))
 + p9.geom_line())

# With confidence band
(p9.ggplot(df, p9.aes("date", "value"))
 + p9.geom_ribbon(p9.aes(ymin="lo", ymax="hi"), alpha=0.2)
 + p9.geom_line())

# Step function (e.g., cumulative events)
(p9.ggplot(economics, p9.aes("date", "unemploy"))
 + p9.geom_step())
```

---

## Text & Annotations

```python
import pandas as pd
mtcars_df = pd.DataFrame(mtcars).assign(model=mtcars.index)

# Label each point
(p9.ggplot(mtcars_df, p9.aes("wt", "mpg", label="model"))
 + p9.geom_point()
 + p9.geom_text(size=8, nudge_y=0.3))

# Label with background box
(p9.ggplot(mtcars_df, p9.aes("wt", "mpg", label="model"))
 + p9.geom_point()
 + p9.geom_label(size=8, nudge_y=0.3, alpha=0.8))

# Manual annotation
(p9.ggplot(mpg, p9.aes("displ", "hwy"))
 + p9.geom_point()
 + p9.annotate("text", x=4, y=40, label="Outlier region", color="red", size=10))
```

---

## Error / Uncertainty

```python
import pandas as pd
df = pd.DataFrame({
    "group": ["A", "B", "C"],
    "mean": [4.2, 5.8, 3.1],
    "se": [0.5, 0.8, 0.3],
}).assign(lo=lambda d: d["mean"] - d["se"],
          hi=lambda d: d["mean"] + d["se"])

# Pointrange (combines point + linerange)
(p9.ggplot(df, p9.aes("group", "mean", ymin="lo", ymax="hi"))
 + p9.geom_pointrange())

# Crossbar
(p9.ggplot(df, p9.aes("group", "mean", ymin="lo", ymax="hi"))
 + p9.geom_crossbar(fatten=2))
```

---

## Faceted Layouts

```python
# Wrap by one variable
(p9.ggplot(mpg, p9.aes("displ", "hwy"))
 + p9.geom_point()
 + p9.facet_wrap("~ class", nrow=2))

# Grid by two variables
(p9.ggplot(mpg, p9.aes("displ", "hwy"))
 + p9.geom_point()
 + p9.facet_grid("drv ~ cyl"))

# Free scales (each panel auto-ranges)
(p9.ggplot(mpg, p9.aes("displ", "hwy"))
 + p9.geom_point()
 + p9.facet_wrap("~ class", scales="free"))
```
