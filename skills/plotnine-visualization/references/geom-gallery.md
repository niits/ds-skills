# Geom Gallery — Plotnine

Visual reference for choosing the right geom. Each entry shows the minimum working example.

---

## One Variable

### Continuous distribution

```python
# Histogram
(ggplot(mpg, aes("hwy"))
 + geom_histogram(binwidth=2, fill="#4292c6", color="white"))

# Density curve
(ggplot(mpg, aes("hwy"))
 + geom_density(fill="#4292c6", alpha=0.5))

# Frequency polygon (histogram as lines)
(ggplot(mpg, aes("hwy", color="drv"))
 + geom_freqpoly(binwidth=2))

# Dotplot (stacked dots)
(ggplot(mpg, aes("hwy"))
 + geom_dotplot(binwidth=1))

# ECDF (cumulative distribution)
(ggplot(mpg, aes("hwy"))
 + stat_ecdf())
```

### Discrete counts

```python
# Bar chart (count rows)
(ggplot(mpg, aes("class"))
 + geom_bar(fill="#4292c6"))
```

---

## Two Variables

### Continuous × Continuous

```python
# Scatter
(ggplot(mpg, aes("cty", "hwy"))
 + geom_point())

# Scatter with overplotting fix
(ggplot(mpg, aes("cty", "hwy"))
 + geom_jitter(width=0.3, height=0.3, alpha=0.5))

# Trend line
(ggplot(mpg, aes("displ", "hwy"))
 + geom_point()
 + geom_smooth(method="lm", se=True))

# Quantile regression
(ggplot(mpg, aes("displ", "hwy"))
 + geom_quantile(quantiles=(0.25, 0.5, 0.75)))

# 2D histogram (bin_2d)
(ggplot(diamonds, aes("carat", "price"))
 + geom_bin_2d(binwidth=(0.1, 500)))

# 2D density contours
(ggplot(mpg, aes("cty", "hwy"))
 + geom_density_2d())
```

### Discrete × Continuous

```python
# Boxplot
(ggplot(mpg, aes("class", "hwy"))
 + geom_boxplot()
 + coord_flip())

# Violin
(ggplot(mpg, aes("class", "hwy", fill="class"))
 + geom_violin()
 + geom_boxplot(width=0.1, fill="white")
 + coord_flip()
 + theme(legend_position="none"))

# Column (pre-aggregated bar)
import pandas as pd
agg = mpg.groupby("class", as_index=False)["hwy"].mean()
(ggplot(agg, aes("class", "hwy"))
 + geom_col(fill="#4292c6")
 + coord_flip())

# Points with error bars
(ggplot(agg, aes("class", "hwy"))
 + geom_point(size=3)
 + geom_errorbar(aes(ymin="hwy-2", ymax="hwy+2"), width=0.2)
 + coord_flip())
```

### Discrete × Discrete

```python
# Count bubbles
(ggplot(mpg, aes("class", "drv"))
 + geom_count())
```

---

## Three Variables

### z-surface (continuous x, y, z)

```python
import polars as pl
seals = pl.DataFrame(seals).with_columns(
    z=(pl.col("delta_long")**2 + pl.col("delta_lat")**2).sqrt()
)

# Contour lines
(ggplot(seals, aes("long", "lat"))
 + geom_contour(aes(z="z")))

# Filled contours
(ggplot(seals, aes("long", "lat"))
 + geom_contour_filled(aes(fill="z")))

# Raster (fast heatmap for equal-spaced grids)
(ggplot(seals, aes("long", "lat"))
 + geom_raster(aes(fill="z")))

# Tile (heatmap for arbitrary grid)
(ggplot(df, aes("x_cat", "y_cat", fill="value"))
 + geom_tile(color="white", size=0.5)
 + scale_fill_gradient2(low="#2166ac", mid="white", high="#d6604d", midpoint=0))
```

---

## Time Series

```python
# Line chart
(ggplot(economics, aes("date", "unemploy"))
 + geom_line())

# With confidence band
(ggplot(df, aes("date", "value"))
 + geom_ribbon(aes(ymin="lo", ymax="hi"), alpha=0.2)
 + geom_line())

# Step function (e.g., cumulative events)
(ggplot(economics, aes("date", "unemploy"))
 + geom_step())
```

---

## Text & Annotations

```python
# Label each point
(ggplot(mtcars, aes("wt", "mpg", label="rownames"))
 + geom_point()
 + geom_text(size=8, nudge_y=0.3))

# Label with background box
(ggplot(mtcars, aes("wt", "mpg", label="rownames"))
 + geom_point()
 + geom_label(size=8, nudge_y=0.3, alpha=0.8))

# Manual annotation
from plotnine import annotate
(ggplot(mpg, aes("displ", "hwy"))
 + geom_point()
 + annotate("text", x=4, y=40, label="Outlier region", color="red", size=10))
```

---

## Error / Uncertainty

```python
import pandas as pd
df = pd.DataFrame({
    "group": ["A", "B", "C"],
    "mean": [4.2, 5.8, 3.1],
    "se": [0.5, 0.8, 0.3]
}).assign(lo=lambda d: d["mean"] - d["se"],
          hi=lambda d: d["mean"] + d["se"])

# Pointrange (combines point + linerange)
(ggplot(df, aes("group", "mean", ymin="lo", ymax="hi"))
 + geom_pointrange())

# Crossbar
(ggplot(df, aes("group", "mean", ymin="lo", ymax="hi"))
 + geom_crossbar(fatten=2))
```

---

## Faceted Layouts

```python
# Wrap by one variable
(ggplot(mpg, aes("displ", "hwy"))
 + geom_point()
 + facet_wrap("~ class", nrow=2))

# Grid by two variables
(ggplot(mpg, aes("displ", "hwy"))
 + geom_point()
 + facet_grid("drv ~ cyl"))

# Free scales (each panel auto-ranges)
(ggplot(mpg, aes("displ", "hwy"))
 + geom_point()
 + facet_wrap("~ class", scales="free"))
```
