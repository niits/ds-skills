---
name: scientific-visualization
description: Generates publication-quality figures for scientific manuscripts and ML papers, rendered inline in Databricks notebooks. Handles data-driven charts (line plots, bar charts, scatter, heatmaps, ablations) via matplotlib/seaborn. Use for any figure for a journal or conference paper.
license: MIT license
metadata:
    skill-author: K-Dense Inc. / Orchestra Research (merged)
    adapted-for: Databricks (inline display via display(fig) only)
---

# Scientific Visualization

## Overview

Generate publication-quality figures and display them inline in Databricks notebooks using `display(fig)`. No file export — all output is rendered in the notebook.

---

## Databricks Setup

### Loading style helpers

Upload `scripts/` and `assets/` to DBFS once, then add them to `sys.path`:

```python
import sys
sys.path.insert(0, '/dbfs/FileStore/ds-skills/scientific-visualization/scripts')
sys.path.insert(0, '/dbfs/FileStore/ds-skills/scientific-visualization/assets')

from style_presets import apply_publication_style, configure_for_journal
from color_palettes import apply_palette
```

### Displaying figures inline

Always use `display(fig)` to render in the notebook. Call `plt.close(fig)` after to free memory:

```python
fig, ax = plt.subplots()
# ... plotting code ...
display(fig)
plt.close(fig)
```

### Loading `.mplstyle` files

```python
import matplotlib.pyplot as plt
plt.style.use('/dbfs/FileStore/ds-skills/scientific-visualization/assets/nature.mplstyle')
```

---

## Quick Start

```python
import matplotlib.pyplot as plt
import numpy as np
from style_presets import apply_publication_style

apply_publication_style('default')

fig, ax = plt.subplots(figsize=(3.5, 2.5))  # single column width
x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), label='sin(x)')
ax.plot(x, np.cos(x), label='cos(x)')
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('Amplitude (mV)')
ax.legend(frameon=False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

display(fig)
plt.close(fig)
```

---

## Chart Type Decision Guide

| Data Pattern | Best Chart |
|-------------|------------|
| Trend over time/steps | Line plot |
| Comparing categories | Grouped bar chart |
| Distribution | Violin / box plot |
| Correlation | Scatter plot |
| Grid of values | Heatmap |
| Many methods, one metric | Horizontal bar (leaderboard) |
| Part of whole | Stacked bar (not pie) |

---

## Publication Styling Defaults

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# ML paper defaults (clean, professional)
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.labelsize": 10, "legend.fontsize": 8.5, "legend.frameon": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.15, "grid.linestyle": "-",
    "lines.linewidth": 1.8, "lines.markersize": 5,
})

# "Ocean Dusk" palette — colorblind-safe
COLORS = ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51",
          "#0072B2", "#56B4E9", "#8C8C8C"]
OUR_COLOR = "#E76F51"       # coral — stands out for "our method"
BASELINE_COLOR = "#B0BEC5"  # cool gray — recedes

FIG_SINGLE = (3.25, 2.5)   # single column
FIG_FULL   = (6.75, 2.8)   # full width
```

Or use the style helpers:

```python
from style_presets import apply_publication_style, configure_for_journal

apply_publication_style('nature')               # sets rcParams for Nature
configure_for_journal('icml', 'single')         # sets figsize + rcParams
```

---

## Common Chart Patterns

### Line plot (training curves)

```python
fig, ax = plt.subplots(figsize=FIG_SINGLE)
markers = ["o", "s", "^", "D", "v"]
for i, (method, (mean, std)) in enumerate(results.items()):
    color = OUR_COLOR if method == "Ours" else COLORS[i]
    ax.plot(steps, mean, label=method, color=color,
            marker=markers[i % 5], markevery=max(1, len(steps)//8),
            markersize=4, zorder=3)
    ax.fill_between(steps, mean - std, mean + std, color=color, alpha=0.12)
ax.set_xlabel("Training Steps")
ax.set_ylabel("Accuracy (%)")
ax.legend(loc="lower right")
display(fig)
plt.close(fig)
```

### Grouped bar chart (ablation)

```python
import numpy as np
fig, ax = plt.subplots(figsize=FIG_FULL)
x = np.arange(len(categories))
n = len(methods)
width = 0.7 / n
for i, (method, scores) in enumerate(methods.items()):
    color = OUR_COLOR if method == "Ours" else COLORS[i]
    offset = (i - n / 2 + 0.5) * width
    bars = ax.bar(x + offset, scores, width * 0.9, label=method, color=color,
                  edgecolor="white", linewidth=0.5)
    for bar, s in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"{s:.1f}", ha="center", va="bottom", fontsize=7, color="#444")
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.set_ylabel("Score")
ax.legend(ncol=min(n, 4))
display(fig)
plt.close(fig)
```

### Heatmap

```python
import seaborn as sns
fig, ax = plt.subplots(figsize=(4, 3.5))
sns.heatmap(matrix, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax,
            cbar_kws={"shrink": 0.75, "aspect": 20},
            linewidths=1.5, linecolor="white",
            annot_kws={"size": 8, "weight": "medium"})
ax.set_xlabel("Predicted")
ax.set_ylabel("Actual")
display(fig)
plt.close(fig)
```

### Horizontal bar (leaderboard)

```python
fig, ax = plt.subplots(figsize=FIG_SINGLE)
y_pos = np.arange(len(models))
colors = [OUR_COLOR if m == "Ours" else BASELINE_COLOR for m in models]
bars = ax.barh(y_pos, scores, color=colors, height=0.55,
               edgecolor="white", linewidth=0.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(models)
ax.set_xlabel("Accuracy (%)")
ax.invert_yaxis()
for bar, s in zip(bars, scores):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f"{s:.1f}", va="center", fontsize=8, color="#444")
display(fig)
plt.close(fig)
```

### Multi-panel figure

```python
from string import ascii_uppercase
fig = plt.figure(figsize=(7, 4))
gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.4)
panels = [fig.add_subplot(gs[r, c]) for r in range(2) for c in range(2)]
for i, ax in enumerate(panels):
    # ... fill panel ...
    ax.text(-0.15, 1.05, ascii_uppercase[i], transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top')
display(fig)
plt.close(fig)
```

**More patterns** (violin, scatter+regression, seaborn statistical, error bars): See `references/data-visualization.md` and `references/matplotlib_examples.md`

---

## Core Principles

### Color — Colorblind Accessibility

```python
from color_palettes import apply_palette
apply_palette('okabe_ito')  # applies to default color cycle

# Heatmaps: use viridis, plasma, cividis (NOT jet/rainbow)
# Diverging: PuOr, RdBu, BrBG (NOT red-green)
```

See `references/color_palettes.md` for full palette guide.

### Typography

- Minimum 6-8 pt at final display size
- Sentence case: "Time (hours)" not "TIME (HOURS)"
- Always include units in parentheses
- Remove top and right spines: `ax.spines['top'].set_visible(False)`

### Statistical Rigor

- Always show error bars; specify SD, SEM, or CI in the caption
- Include n in figure or caption
- Mark significance: *, **, ***
- Show individual data points alongside summary statistics when possible

---

## Venue-Specific Sizing

| Venue | Single Column | Full Width |
|-------|--------------|------------|
| NeurIPS | 5.5 in | 5.5 in |
| ICML | 3.25 in | 6.75 in |
| ICLR | 5.5 in | 5.5 in |
| ACL / AAAI | 3.3 in | 6.8–7.0 in |
| Nature | 3.5 in (89 mm) | 7.2 in (183 mm) |
| Science | 2.2 in (55 mm) | 6.9 in (175 mm) |
| Cell | 3.35 in (85 mm) | 7.0 in (178 mm) |

---

## Resources

### references/

- `color_palettes.md` — Colorblind-friendly palettes, colormaps, testing procedures
- `matplotlib_examples.md` — 10 complete working code examples
- `data-visualization.md` — ML paper chart patterns (violin, radar, scaling laws)
- `publication_guidelines.md` — Best practices, typography, layout, full checklist
- `journal_requirements.md` — Technical specs by publisher
- `style-guide.md` — Venue-specific details, accessibility checklist

### scripts/

- `style_presets.py` — `apply_publication_style()`, `configure_for_journal()`, `set_color_palette()`

### assets/

- `color_palettes.py` — Palette constants and `apply_palette()` helper
- `nature.mplstyle` — Nature journal rcParams
- `publication.mplstyle` — General publication style
- `presentation.mplstyle` — Larger fonts for posters/slides

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Colors indistinguishable in print | Colorblind-safe palette + different line styles/markers |
| Figure too large for column | Check venue width limits; use `figsize` in inches |
| Legend overlaps data | Use `bbox_to_anchor` or `loc="upper left"` |
| Font too small | Minimum 6-7 pt; verify at intended display size |
| Blank output in notebook | Use `display(fig)` not `plt.show()` |
| Memory leak from many figures | Call `plt.close(fig)` after each `display(fig)` |
