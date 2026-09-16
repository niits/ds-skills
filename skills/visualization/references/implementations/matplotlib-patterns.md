# Matplotlib Patterns for Non-Obvious Cases

These are focused implementation patterns, not reusable chart APIs. Adapt labels, units,
estimands, and dimensions to the task. Use only matplotlib in Quick EDA.

```python
import matplotlib.pyplot as plt
import numpy as np
```

## Named Uncertainty Band

Do not draw an unnamed band. Compute uncertainty at the independent analysis unit and state
whether the band is SD, SEM, a confidence interval, a prediction interval, or another quantity.

```python
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(x, estimate, color="#0072B2", label="Mean estimate")
ax.fill_between(x, lower_ci, upper_ci, color="#0072B2", alpha=0.2,
                label="95% confidence interval")
ax.set(xlabel="Period", ylabel="Metric (unit)")
ax.legend(frameon=False)
fig.tight_layout()
```

## Grouped Estimates With Intervals

```python
labels = ["Baseline", "Variant A", "Variant B"]
estimate = np.array([0.62, 0.68, 0.71])
ci_half_width = np.array([0.03, 0.025, 0.028])
x = np.arange(len(labels))

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(x, estimate, yerr=ci_half_width, capsize=4, color="#0072B2")
ax.set(xticks=x, xticklabels=labels, ylabel="Rate", ylim=(0, 1))
ax.text(1, 0.02, "Error bars: 95% CI; report n and method", ha="center")
fig.tight_layout()
```

For model comparisons, prefer a paired interval for the difference rather than comparing overlap
between marginal intervals.

## Heatmap With Explicit Scale

```python
fig, ax = plt.subplots(figsize=(6, 5))
image = ax.imshow(matrix, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
colorbar = fig.colorbar(image, ax=ax)
colorbar.set_label("Correlation coefficient")
ax.set(xticks=np.arange(len(names)), yticks=np.arange(len(names)))
ax.set_xticklabels(names, rotation=45, ha="right")
ax.set_yticklabels(names)
fig.tight_layout()
```

Use a shared, meaningful domain. A heatmap without a labeled colorbar is not interpretable.

## Comparable Small Multiples

```python
fig, axes = plt.subplots(1, len(groups), figsize=(4 * len(groups), 3), sharex=True, sharey=True)
axes = np.atleast_1d(axes)

for ax, (name, group) in zip(axes, groups.items()):
    ax.scatter(group["x"], group["y"], alpha=0.5, s=18)
    ax.set_title(name)

fig.supxlabel("x (unit)")
fig.supylabel("y (unit)")
fig.tight_layout()
```

Keep scales shared by default. If free scales are necessary, disclose that panels no longer
support direct magnitude comparison.

## Log-Log Relationship

```python
fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(size, metric, color="#0072B2")
ax.set(xscale="log", yscale="log", xlabel="Size (log scale)", ylabel="Metric (log scale)")
fig.tight_layout()
```

Use log scales because the data range or hypothesized relationship requires them, not to make a
chart look smoother. Check zero and negative values before transforming.
