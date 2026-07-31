# Honest-Uncertainty Matplotlib Examples

## Overview

A small set of worked examples for the habit that matters most for message accuracy: always
showing the uncertainty behind a plotted value, and saying explicitly what kind of uncertainty
it is. Colors are from the colorblind-safe Okabe-Ito palette (`references/color-palettes.md`).

## Example 1: Line Plot with Error Bars

```python
import matplotlib.pyplot as plt
import numpy as np

# Generate sample data reproducibly
rng = np.random.default_rng(42)
x = np.linspace(0, 10, 50)
y1 = 2 * x + 1 + rng.normal(0, 1, 50)

# Calculate means and standard errors for binned data
bins = np.linspace(0, 10, 11)
y1_mean = [y1[(x >= bins[i]) & (x < bins[i+1])].mean() for i in range(len(bins)-1)]
y1_sem = [y1[(x >= bins[i]) & (x < bins[i+1])].std(ddof=1) /
          np.sqrt(len(y1[(x >= bins[i]) & (x < bins[i+1])]))
          for i in range(len(bins)-1)]
x_binned = (bins[:-1] + bins[1:]) / 2

fig, ax = plt.subplots(figsize=(4, 3))

# Plot with error bars — never plot the mean alone if a dispersion/uncertainty
# measure is available
ax.errorbar(x_binned, y1_mean, yerr=y1_sem,
            marker='o', markersize=4, capsize=3, capthick=0.5,
            label='Method A (mean ± SEM)', color='#0072B2', linewidth=1.5)

ax.set_xlabel('Time (hours)')
ax.set_ylabel('Metric value (a.u.)')
ax.legend(frameon=False, loc='upper left')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

fig.tight_layout()
fig.savefig('line_plot_with_errors.pdf', bbox_inches='tight')
plt.show()
```

## Example 2: Heatmap with Colorbar

A heatmap without a colorbar is not interpretable — the colorbar is required, not decorative,
because it's the only place the color-to-value mapping is defined.

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
n = 10
A = np.random.randn(n, n)
corr_matrix = np.corrcoef(A)

fig, ax = plt.subplots(figsize=(4, 3.5))

# Diverging colormap centered at 0 — correlation has a meaningful midpoint
im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')

cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Correlation coefficient', rotation=270, labelpad=15)

feature_names = [f'Feature{i+1}' for i in range(n)]
ax.set_xticks(np.arange(n))
ax.set_yticks(np.arange(n))
ax.set_xticklabels(feature_names, rotation=45, ha='right')
ax.set_yticklabels(feature_names)

fig.tight_layout()
fig.savefig('correlation_heatmap.pdf', bbox_inches='tight')
plt.show()
```

## Example 3: Time Series with Shaded Error

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
epochs = np.linspace(0, 24, 100)
n_runs = 5

data = np.array([10 * np.exp(-epochs/10) + np.random.normal(0, 0.5, 100)
                 for _ in range(n_runs)])

mean = data.mean(axis=0)
sem = data.std(axis=0, ddof=1) / np.sqrt(n_runs)

fig, ax = plt.subplots(figsize=(4, 2.5))

ax.plot(epochs, mean, linewidth=1.5, color='#0072B2', label='Mean ± SEM')
ax.fill_between(epochs, mean - sem, mean + sem,
                alpha=0.3, color='#0072B2', linewidth=0)

ax.set_xlabel('Epoch')
ax.set_ylabel('Validation loss')
ax.legend(frameon=False, loc='upper right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlim(0, 24)

fig.tight_layout()
fig.savefig('timeseries_shaded.pdf', bbox_inches='tight')
plt.show()
```

## Example 4: Grouped Bar Plot with Uncertainty

State explicitly, in the chart itself, what the error bars represent — a reader should never
have to guess whether they're seeing SD, SEM, or a CI.

```python
import matplotlib.pyplot as plt
import numpy as np

categories = ['Baseline', 'Variant A', 'Variant B']
control_means = [100, 85, 70]
control_ci95 = [10, 12, 10]  # CI half-widths from independent replicates
treatment_means = [100, 120, 140]
treatment_ci95 = [12, 16, 18]

x = np.arange(len(categories))
width = 0.35

fig, ax = plt.subplots(figsize=(4, 3))

bars1 = ax.bar(x - width/2, control_means, width, yerr=control_ci95,
               capsize=3, label='Control', color='#0072B2', alpha=0.8)
bars2 = ax.bar(x + width/2, treatment_means, width, yerr=treatment_ci95,
               capsize=3, label='Treatment', color='#E69F00', alpha=0.8)

ax.set_ylabel('Metric (% of baseline)')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend(frameon=False, loc='upper left')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylim(0, 180)

# Say exactly what the error bars are — this sentence is not optional
ax.text(0.98, 0.02, 'Bars show means; error bars are 95% CIs (report n and method)',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=6)

fig.tight_layout()
fig.savefig('grouped_bar_uncertainty.pdf', bbox_inches='tight')
plt.show()
```

## Resources

- Matplotlib documentation: https://matplotlib.org/
- Seaborn gallery: https://seaborn.pydata.org/examples/index.html
