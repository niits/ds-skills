# Quick EDA With Matplotlib

## Goal

Answer one analytical question quickly. The plot is provisional evidence, not a polished artifact.
Use matplotlib only: no seaborn, Plotly, or plotnine.

## Workflow

1. State one analytical question.
2. Check row grain, plotted column types, missingness, duplicates, range, category support, and any
   aggregation used.
3. Choose the simplest view:

| Question | Matplotlib method |
|---|---|
| One numeric distribution | `ax.hist(...)` |
| Two numeric variables | `ax.scatter(...)` |
| Change over ordered time | `ax.plot(...)` |
| Numeric distribution by category | `ax.boxplot(...)` |
| Category counts or values | Explicitly compute values, then `ax.bar(...)` |

4. Use `matplotlib.pyplot.subplots()` and the object-oriented `fig, ax` API.
5. Label axes with variables and units. Sort time before lines and ranked categories before bars.
   Start bars at zero and disclose transformations.
6. Render and inspect impossible values, sparse groups, outliers, overlap, and scale effects.
7. Report one observed pattern and one caveat. If execution or data access is unavailable, return
   code plus inspection checks and do not invent a finding.

Do not add an insight title, extensive annotation, custom theme, or delivery bundle unless the
user promotes the plot to a shared artifact.

## Minimal Pattern

```python
import matplotlib.pyplot as plt

plot_df = df[["amount", "frequency"]].dropna()

fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(plot_df["amount"], plot_df["frequency"], alpha=0.35, s=18)
ax.set(
    xlabel="Amount (USD)",
    ylabel="Purchase frequency (orders/month)",
    title="EDA: amount versus purchase frequency",
)
fig.tight_layout()
plt.show()  # In Databricks, use display(fig).
```

## Output

Return chart code, the observed pattern after rendering, and one caveat. If the chart becomes a
shared deliverable, switch to `slide-infographic.md`.
