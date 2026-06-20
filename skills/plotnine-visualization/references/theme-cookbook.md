# Theme Cookbook — Plotnine

Ready-to-use theme recipes for common visualization styles.

---

## NYT / Editorial Style

Clean, minimal, serif headline, thin gridlines only on y-axis.

```python
NYT_THEME = (
    theme_minimal(base_size=11)
    + theme(
        plot_title=element_text(size=14, weight="bold", family="Georgia", ha="left"),
        plot_subtitle=element_text(size=11, color="#666666", ha="left"),
        plot_caption=element_text(size=8, color="#999999", ha="left"),
        axis_title_x=element_text(size=9, color="#444444"),
        axis_title_y=element_blank(),
        axis_text=element_text(size=9, color="#444444"),
        panel_grid_major_x=element_blank(),
        panel_grid_minor=element_blank(),
        panel_grid_major_y=element_line(color="#e8e8e8", size=0.5),
        axis_line_x=element_line(color="#333333", size=0.8),
        axis_ticks_x=element_line(color="#333333"),
        axis_ticks_y=element_blank(),
    )
)

(ggplot(df, aes("category", "value"))
 + geom_col(fill="#1f77b4", width=0.6)
 + NYT_THEME
 + labs(title="Chart Title", subtitle="Supporting context here",
        caption="Source: Your data source"))
```

---

## FT (Financial Times) Style

Salmon/pink background, dark text, minimal.

```python
FT_SALMON = "#FFF1E5"
FT_DARK = "#33302E"
FT_BLUE = "#0D6EFD"

FT_THEME = (
    theme_minimal(base_size=11)
    + theme(
        plot_background=element_rect(fill=FT_SALMON),
        panel_background=element_rect(fill=FT_SALMON),
        panel_grid_major=element_line(color="#d4c5b0", size=0.4),
        panel_grid_minor=element_blank(),
        axis_text=element_text(color=FT_DARK),
        axis_title=element_text(color=FT_DARK),
        plot_title=element_text(color=FT_DARK, weight="bold", size=14),
        plot_subtitle=element_text(color="#66605a", size=10),
    )
)
```

---

## Dark / Presentation Mode

High contrast on dark background — good for slides and dashboards.

```python
DARK_THEME = (
    theme_dark(base_size=13)
    + theme(
        plot_background=element_rect(fill="#1a1a2e"),
        panel_background=element_rect(fill="#16213e"),
        panel_grid_major=element_line(color="#2d2d4e", size=0.5),
        panel_grid_minor=element_blank(),
        axis_text=element_text(color="#e0e0e0"),
        axis_title=element_text(color="#e0e0e0"),
        plot_title=element_text(color="#ffffff", weight="bold"),
        legend_background=element_rect(fill="#1a1a2e"),
        legend_text=element_text(color="#e0e0e0"),
        legend_title=element_text(color="#e0e0e0"),
        strip_background=element_rect(fill="#0f3460"),
        strip_text=element_text(color="#e0e0e0"),
    )
)

# Use with bright palette
(ggplot(df, aes("x", "y", color="group"))
 + geom_line(size=1.2)
 + scale_color_manual(values=["#e94560", "#0f3460", "#533483", "#e2b714"])
 + DARK_THEME)
```

---

## Publication / Academic

Minimal, black text, no gridlines — suitable for papers.

```python
PUB_THEME = (
    theme_classic(base_size=11)
    + theme(
        axis_text=element_text(color="black"),
        axis_title=element_text(color="black", size=12),
        plot_title=element_text(weight="bold", size=13),
        panel_border=element_rect(color="black", fill=None, size=0.8),
        axis_line=element_line(color="black", size=0.5),
        axis_ticks=element_line(color="black"),
    )
)
```

---

## Dashboard / Business Style

Clean white, subdued palette, clear hierarchy.

```python
DASHBOARD_THEME = (
    theme_minimal(base_size=10)
    + theme(
        panel_grid_minor=element_blank(),
        panel_grid_major=element_line(color="#f0f0f0"),
        axis_text=element_text(color="#555555", size=9),
        axis_title=element_text(color="#333333", size=10),
        plot_title=element_text(weight="bold", size=12, color="#222222"),
        plot_subtitle=element_text(size=9, color="#777777"),
        strip_background=element_rect(fill="#f5f5f5", color="#e0e0e0"),
        strip_text=element_text(size=9, weight="bold", color="#444444"),
        legend_position="bottom",
        legend_title=element_blank(),
        legend_text=element_text(size=9),
    )
)
```

---

## Rotating x-axis labels

```python
+ theme(axis_text_x=element_text(angle=45, ha="right", size=9))

# or 90 degrees
+ theme(axis_text_x=element_text(angle=90, va="center", size=9))
```

---

## Legend control

```python
# Move legend to bottom
+ theme(legend_position="bottom", legend_direction="horizontal")

# Remove legend
+ theme(legend_position="none")
# or on individual geom:
geom_point(show_legend=False)

# Legend inside plot
+ theme(legend_position=(0.85, 0.85))  # (x, y) as fraction 0-1

# Multi-column legend
+ guides(color=guide_legend(ncol=3))
```

---

## Combining themes

```python
# Start with a base, then override specifics
(ggplot(df, aes("x", "y"))
 + geom_point()
 + theme_bw(base_size=12)                    # base theme
 + theme(panel_grid_minor=element_blank(),   # override specific elements
         plot_title=element_text(weight="bold")))
```

---

## Removing elements

```python
+ theme(
    axis_title_x=element_blank(),    # no x-axis title
    axis_text_y=element_blank(),     # no y-axis tick labels
    axis_ticks=element_blank(),      # no tick marks
    panel_border=element_blank(),    # no panel border
    panel_grid=element_blank(),      # no gridlines
    legend_position="none",          # no legend
)
```
