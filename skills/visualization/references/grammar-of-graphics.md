# Grammar of Graphics Reference (plotnine)

plotnine is a Python port of ggplot2. Reach for it when a chart's structure *is*
the grammar of graphics — layered geoms, faceting, grouped aesthetics — and you
want declarative code instead of imperative matplotlib calls. For one-off static
figures, matplotlib is usually less overhead; for interactive EDA, prefer Plotly.
plotnine's sweet spot is **faceted / grouped / multi-layer statistical charts**.

```python
from plotnine import *   # ggplot, aes, geom_*, facet_*, scale_*, theme_*, labs, ...
import pandas as pd
```

Every plot is `ggplot(data, aes(...)) + layers + scales + facets + theme`.

---

## 1. `aes()` — aesthetic mappings

Map data columns to visual channels. Mappings go in `aes()`; constants go outside.

```python
ggplot(df, aes(x="month", y="default_rate", color="segment"))
# constant (not data-driven) → outside aes:
geom_line(color="#0072B2", size=1.2)
```

Common aesthetics: `x`, `y`, `color`/`colour` (line/point outline), `fill` (area),
`shape`, `size`, `alpha`, `group` (force grouping without a visual channel),
`linetype`.

---

## 2. Geoms — the visual layer

| Geom | Use for |
|------|---------|
| `geom_point()` | scatter |
| `geom_line()` / `geom_path()` | trends (line sorts by x; path follows row order) |
| `geom_bar(stat="count")` / `geom_col()` | bars from counts / from explicit y values |
| `geom_histogram(bins=30)` | distribution of one continuous variable |
| `geom_boxplot()` / `geom_violin()` | distribution by category |
| `geom_density()` | smoothed distribution (KS-style overlays) |
| `geom_tile()` | heatmaps / migration matrices |
| `geom_area()` / `geom_ribbon()` | filled area / CI band (`ymin`, `ymax`) |
| `geom_errorbar()` | error bars / confidence intervals |
| `geom_smooth(method="lm")` | trend line with CI |
| `geom_hline()` / `geom_vline()` | reference / threshold lines |
| `geom_text()` / `geom_label()` | direct labels (declutter: label instead of legend) |

Layers stack in order — later geoms draw on top.

```python
(ggplot(df, aes("score", fill="outcome"))
 + geom_density(alpha=0.5)
 + geom_vline(xintercept=cutoff, linetype="dashed"))
```

---

## 3. Stats — computed transforms

Many geoms wrap a stat. Use `stat_*` or the geom's `stat=` argument when you want a
computed layer: `stat_summary` (mean/median per group), `stat_smooth`,
`stat_bin`, `stat_ecdf` (empirical CDF — handy for KS-style cumulative curves).

```python
geom_point(stat="summary", fun_y=np.mean)   # mean per x group
```

---

## 4. Scales — control how data maps to the channel

```python
+ scale_x_log10()
+ scale_y_continuous(labels=lambda v: [f"{x:.0%}" for x in v])   # percent axis
+ scale_color_manual(values=["#0072B2", "#D55E00", "#009E73"])   # Okabe-Ito subset
+ scale_fill_brewer(type="seq", palette="Blues")
+ scale_color_cmap(cmap_name="viridis")                          # colorblind-safe
```

Rules that carry over from the rest of this skill: prefer **colorblind-safe**
palettes (`viridis`/`cividis` for continuous, Okabe-Ito for categorical), and
format axes in the reader's units (%, $, bps) via `labels=`.

---

## 5. Facets — small multiples

The reason to choose plotnine over matplotlib for many charts.

```python
+ facet_wrap("~ segment", ncol=3)              # one panel per segment
+ facet_grid("region ~ product")               # rows × columns
+ facet_wrap("~ cohort", scales="free_y")      # independent y per panel (use with care)
```

`scales="free"` lets each panel rescale — powerful but can mislead; keep scales
fixed unless the panels genuinely live on different ranges.

---

## 6. Themes & labels

```python
+ labs(title="Default rate is rising in the subprime segment",
       x="Month", y="Default rate", color="Segment")
+ theme_minimal(base_size=12)
+ theme(figure_size=(10, 5),
        legend_position="none",          # declutter: direct-label instead
        panel_grid_minor=element_blank())
```

### NYT slide theme

The shared NYT style is available for plotnine. Add `theme_nyt()` to any ggplot
for slide-first, decluttered defaults (matching the matplotlib/Plotly NYT styling):

```python
from shared.nyt_theme import theme_nyt   # ../shared/nyt_theme.py
(ggplot(df, aes("month", "default_rate"))
 + geom_line(size=1.2)
 + theme_nyt(base_size=15))
```

---

## 7. Rendering on Databricks

plotnine returns a ggplot object; draw it, then `display()` the underlying figure.

```python
p = (ggplot(df, aes("month", "default_rate", color="segment")) + geom_line())
fig = p.draw()            # -> matplotlib Figure
display(fig)              # Databricks inline render
# or save: p.save("chart.png", dpi=200, width=10, height=5, units="in")
```

---

## When NOT to use plotnine

- **Interactive exploration** → Plotly (hover, zoom, brushing). plotnine is static.
- **A single, heavily customized publication figure** → matplotlib gives finer,
  imperative control over every artist; plotnine's abstraction gets in the way.
- **Anything plotnine doesn't support** (3D, some annotations) → fall back to
  matplotlib. See the library decision tree in `SKILL.md`.
