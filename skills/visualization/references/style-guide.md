# Color & Caption Standards for ML Paper Figures

Message-delivery standards for figure color choices and captions. For venue dimensions,
typography, and submission mechanics, see your target venue's author guidelines directly.

## Color Palettes

### Categorical Palette (distinguishing series)

Use the skill's canonical colorblind-safe categorical palette — Okabe-Ito — rather than a
library's default color cycle (seaborn's `"deep"` default, for example, is **not** CVD-safe).
See `references/color-palettes.md` and `assets/color_palettes.py` for the full palette and
usage in matplotlib/seaborn/plotly.

```python
OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
             "#0072B2", "#D55E00", "#CC79A7", "#000000"]
```

### Two-Color Schemes (ours vs. baseline)

```python
# High-contrast, colorblind-safe pair
OURS = "#D55E00"     # vermillion — stands out
BASELINE = "#8C8C8C" # gray — recedes

# Alternative pair
OURS = "#0072B2"     # blue
BASELINE = "#E69F00"  # orange
```

### Gradient Schemes (for heatmaps / continuous data)

| Use Case | Colormap | Code |
|----------|----------|------|
| Single variable (0 to max) | Blues | `cmap="Blues"` |
| Diverging (negative to positive) | RdBu_r | `cmap="RdBu_r"` |
| Perceptually uniform | viridis | `cmap="viridis"` |
| Correlation matrix | RdBu_r | `cmap="RdBu_r"` |
| Attention weights | YlOrRd | `cmap="YlOrRd"` |

### Colors to Avoid

- **Pure red + pure green** — indistinguishable for ~8% of males
- **Rainbow/jet colormap** — perceptually non-uniform, misleading
- **Light yellow on white** — insufficient contrast
- **Neon/saturated colors** — look unprofessional in academic papers

## Caption Best Practices

- **First sentence**: What the figure shows (standalone understanding)
- **Key takeaway**: What the reader should notice
- **Color note**: "Best viewed in color" if color carries meaning
- **No "Figure X shows..."** — the figure number is already there

Good: "Training loss across model sizes. Larger models converge faster and to lower final loss."
Bad: "Figure 3 shows the training loss for different model sizes."

## Accessibility Checklist

- [ ] Figures readable in grayscale (print-friendly)
- [ ] Colorblind-safe palette used (verified, not assumed — see `color-palettes.md`)
- [ ] Different line styles/markers in addition to colors
- [ ] High contrast between data and background
- [ ] Axis labels present and readable
- [ ] Legend clear and non-overlapping, or replaced with direct labels
