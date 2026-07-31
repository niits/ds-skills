# Chart-Type Patterns for ML Papers

Working code patterns for the encoding/chart-selection decisions that come up repeatedly in ML
papers: which chart form fits the analytical question, and how to keep the encoding honest.

## Setup

```python
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
```

### Colors

Use a colorblind-safe categorical palette, not the library default. See
`references/color-palettes.md` and `assets/color_palettes.py` for the full set and rationale.

```python
OKABE_ITO_LIST = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
                   '#0072B2', '#D55E00', '#CC79A7', '#000000']
ACCENT = '#D55E00'    # vermillion — "our method" / the one highlighted series
BASELINE = '#8C8C8C'  # gray — recedes, use for non-highlighted comparisons
```

### Colormaps for Continuous Data

```python
cmap_sequential = sns.color_palette("YlOrRd", as_cmap=True)  # intensity, one direction
cmap_diverging = sns.color_palette("RdBu_r", as_cmap=True)   # centered at 0 (correlation, delta)
cmap_uniform = plt.cm.viridis                                 # perceptually uniform, general use
```

## Chart Type 1: Training Curves (Line Plot)

The most common figure in ML papers. Shows loss/accuracy over training steps.

```python
def plot_training_curves(data, metric="Loss", figsize=(4, 3)):
    """
    data: dict of {method_name: (steps_array, values_array)}
    figsize: adjust to your target output width
    """
    fig, ax = plt.subplots(figsize=figsize)

    markers = ["o", "s", "^", "D", "v", "P"]
    for i, (method, (steps, values)) in enumerate(data.items()):
        ax.plot(steps, values,
                label=method,
                color=OKABE_ITO_LIST[i % len(OKABE_ITO_LIST)],
                linewidth=1.5,
                marker=markers[i % len(markers)],
                markevery=max(1, len(steps) // 8),
                markersize=4)

    ax.set_xlabel("Training Steps")
    ax.set_ylabel(metric)
    ax.legend(frameon=False, loc="best")

    # Log scale for loss (common)
    if "loss" in metric.lower():
        ax.set_yscale("log")

    return fig, ax
```

### Shaded Variability or Uncertainty

```python
ax.plot(steps, mean_values, color=OKABE_ITO_LIST[0], linewidth=1.5, label="Our Method")
ax.fill_between(steps, mean_values - std_values, mean_values + std_values,
                 color=OKABE_ITO_LIST[0], alpha=0.2)
```

This is a mean +/- 1 SD band, not a confidence interval. For a CI, compute it across
independent replicates/seeds with a justified bootstrap or sampling model and report `n`.

## Chart Type 2: Grouped Bar Chart (Ablation / Comparison)

```python
def plot_ablation(categories, methods_data, errors_data=None, ylabel="Accuracy (%)", figsize=(6, 3)):
    """
    categories: list of benchmark names
    methods_data: dict of {method_name: list_of_scores}
    errors_data: optional dict of {method_name: list_of_errors}, same shape as methods_data
                 (each entry is a +/- interval half-width per category, or a (2, n_cats) array
                 for asymmetric CIs). Pass replicate-level results or estimates plus intervals
                 here; display uncertainty and independent-replicate n. Prespecify any
                 highlighted method.
    """
    fig, ax = plt.subplots(figsize=figsize)

    n_methods = len(methods_data)
    n_cats = len(categories)
    width = 0.8 / n_methods
    x = np.arange(n_cats)

    for i, (method, scores) in enumerate(methods_data.items()):
        offset = (i - n_methods / 2 + 0.5) * width
        yerr = errors_data.get(method) if errors_data else None
        bars = ax.bar(x + offset, scores, width * 0.9, yerr=yerr, capsize=3,
                      label=method, color=OKABE_ITO_LIST[i % len(OKABE_ITO_LIST)])
        # Value labels on top
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                    f"{score:.1f}", ha="center", va="bottom", fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=0)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False, ncol=min(n_methods, 4), loc="upper right")
    ax.set_ylim(bottom=0)

    return fig, ax
```

## Chart Type 3: Heatmap (Attention / Confusion Matrix)

```python
def plot_heatmap(matrix, xlabels, ylabels, title="", fmt=".2f", cmap="Blues"):
    """
    matrix: 2D numpy array
    """
    fig, ax = plt.subplots(figsize=(max(4, len(xlabels) * 0.6), max(3, len(ylabels) * 0.5)))

    sns.heatmap(matrix, annot=True, fmt=fmt, cmap=cmap, ax=ax,
                xticklabels=xlabels, yticklabels=ylabels,
                cbar_kws={"shrink": 0.8}, linewidths=0.5, linecolor="white",
                annot_kws={"size": 8})

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    if title:
        ax.set_title(title, pad=12)

    return fig, ax
```

### Diverging Heatmap (correlation)

```python
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="RdBu_r",
            center=0, vmin=-1, vmax=1, ax=ax)
```

## Chart Type 4: Scatter Plot

```python
def plot_scatter(x, y, labels=None, xlabel="", ylabel="", figsize=(4, 3.5)):
    fig, ax = plt.subplots(figsize=figsize)

    ax.scatter(x, y, c=OKABE_ITO_LIST[0], s=30, alpha=0.7, edgecolors="white", linewidth=0.5)

    if labels is not None:
        for i, label in enumerate(labels):
            ax.annotate(label, (x[i], y[i]), fontsize=7,
                        xytext=(5, 5), textcoords="offset points")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    return fig, ax
```

### Scatter with regression line

```python
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
line_x = np.linspace(min(x), max(x), 100)
ax.plot(line_x, slope * line_x + intercept, color=OKABE_ITO_LIST[1],
        linestyle="--", linewidth=1, label=f"$R^2$={r_value**2:.3f}")
```

## Chart Type 5: Horizontal Bar (Leaderboard)

Sorted, with the subject of the message accented and everything else grayed — the "one accent,
rest gray" pattern from `pre-attentive-attributes.md` applied to a ranked comparison.

```python
def plot_leaderboard(models, scores, errors=None, highlight_idx=-1, xlabel="Score", figsize=(4, 3)):
    """
    errors: optional list of +/- interval half-widths, same length as scores (or a (2, n)
    array for asymmetric CIs). Use estimates with intervals; highlight only by a
    prespecified criterion.
    """
    fig, ax = plt.subplots(figsize=figsize)

    y_pos = np.arange(len(models))
    colors = [BASELINE] * len(models)
    if highlight_idx >= 0:
        colors[highlight_idx] = ACCENT

    bars = ax.barh(y_pos, scores, xerr=errors, capsize=3, color=colors, height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(models)
    ax.set_xlabel(xlabel)
    ax.invert_yaxis()

    # Value labels
    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{score:.1f}", va="center", fontsize=8)

    return fig, ax
```

## Chart Type 6: Multi-Panel Figure

```python
def plot_multi_panel(data_per_panel, panel_titles, figsize_per_panel=(3.25, 2.5)):
    """Create a 1xN figure with shared styling."""
    n = len(data_per_panel)
    w, h = figsize_per_panel
    fig, axes = plt.subplots(1, n, figsize=(w * n, h), sharey=True)
    if n == 1:
        axes = [axes]

    for ax, data, title in zip(axes, data_per_panel, panel_titles):
        # Plot each panel (customize per use case)
        ax.set_title(title, fontsize=10, fontweight="bold")

    # Only label left y-axis
    axes[0].set_ylabel("Metric")

    # Shared x-label
    fig.supxlabel("Training Steps", fontsize=11)
    fig.tight_layout()
    return fig, axes
```

### Subplot label convention (a, b, c)

```python
for i, ax in enumerate(axes):
    ax.text(-0.12, 1.05, f"({chr(97 + i)})", transform=ax.transAxes,
            fontsize=12, fontweight="bold", va="top")
```

## Chart Type 7: Violin / Box Plot (Distribution)

```python
def plot_distributions(data_dict, ylabel="Score", figsize=(4, 3)):
    """data_dict: {method_name: array_of_values}"""
    fig, ax = plt.subplots(figsize=figsize)

    positions = range(len(data_dict))
    parts = ax.violinplot(list(data_dict.values()), positions=positions,
                          showmeans=True, showmedians=True)

    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(OKABE_ITO_LIST[i % len(OKABE_ITO_LIST)])
        pc.set_alpha(0.7)

    ax.set_xticks(positions)
    ax.set_xticklabels(list(data_dict.keys()))
    ax.set_ylabel(ylabel)

    return fig, ax
```

## Chart Type 8: Stacked Horizontal Bar

Preferred over pie charts for showing proportions — position and length are easier to compare
precisely than angle/area, and it composes cleanly across multiple categories.

```python
def plot_stacked_bar(categories, segments, segment_labels, colors=None, figsize=(6, 3)):
    """
    categories: list of row labels
    segments: list of lists (each inner list = values per segment)

    CAUTION: colors wrap (via modulo) past len(colors) — with the default
    OKABE_ITO_LIST that's 8 colors. Stacked-bar segment counts routinely exceed 8
    (unlike training-curve/ablation/violin series counts), so two segments in the
    same bar can silently get the same color. Pass an explicit `colors` list sized
    to your segment count, or collapse small segments into an "Other" bucket, once
    you're past ~8 segments.
    """
    fig, ax = plt.subplots(figsize=figsize)
    y_pos = np.arange(len(categories))
    colors = colors or OKABE_ITO_LIST
    from matplotlib.colors import to_rgb

    def label_color(fill):
        rgb = np.array(to_rgb(fill))
        linear = np.where(rgb <= 0.04045, rgb / 12.92,
                          ((rgb + 0.055) / 1.055) ** 2.4)
        luminance = np.dot(linear, [0.2126, 0.7152, 0.0722])
        black_contrast = (luminance + 0.05) / 0.05
        white_contrast = 1.05 / (luminance + 0.05)
        return "black" if black_contrast >= white_contrast else "white"

    left = np.zeros(len(categories))
    for i, (seg_values, label) in enumerate(zip(segments, segment_labels)):
        color = colors[i % len(colors)]
        ax.barh(y_pos, seg_values, left=left, height=0.6,
                label=label, color=color)
        text_color = label_color(color)
        for j, v in enumerate(seg_values):
            if v > 5:  # Only label segments > 5%
                ax.text(left[j] + v / 2, y_pos[j], f"{v:.0f}%",
                        ha="center", va="center", fontsize=7, color=text_color)
        left += seg_values

    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories)
    ax.set_xlabel("Percentage (%)")
    ax.legend(frameon=False, loc="upper right", ncol=2)
    ax.invert_yaxis()

    return fig, ax
```

## Chart Type 9: Scaling Law Plot (Log-Log)

Common in LLM papers for compute/data/parameter scaling. Log-log axes turn a power law into a
straight line — the correct encoding for "does this relationship follow N^k," not a cosmetic
choice.

```python
def plot_scaling(sizes, metrics, fit_line=True, xlabel="Parameters",
                 ylabel="Loss", figsize=(4, 3)):
    fig, ax = plt.subplots(figsize=figsize)

    ax.scatter(sizes, metrics, color=OKABE_ITO_LIST[0], s=40, zorder=5)

    if fit_line:
        log_sizes = np.log(sizes)
        log_metrics = np.log(metrics)
        coeffs = np.polyfit(log_sizes, log_metrics, 1)
        fit_x = np.linspace(min(log_sizes), max(log_sizes), 100)
        ax.plot(np.exp(fit_x), np.exp(np.polyval(coeffs, fit_x)),
                color=OKABE_ITO_LIST[1], linestyle="--", linewidth=1.5,
                label=f"$L \\propto N^{{{coeffs[0]:.2f}}}$")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if fit_line:
        ax.legend(frameon=False)

    return fig, ax
```

## Seaborn Integration

Seaborn is built on matplotlib and useful for statistical plots.

```python
# Use seaborn styling with matplotlib control
sns.set_theme(style="whitegrid", font_scale=0.9, rc={
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Pair plot (exploratory: many pairwise relationships at once)
g = sns.pairplot(df, hue="method", palette=OKABE_ITO_LIST[:3])

# Joint plot (scatter + marginal distributions — shows the relationship and each
# variable's shape in one view)
g = sns.jointplot(data=df, x="param_count", y="accuracy",
                  kind="reg", color=OKABE_ITO_LIST[0])
```
