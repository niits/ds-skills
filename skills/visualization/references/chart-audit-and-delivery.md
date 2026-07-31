# Chart Audit and Delivery

## Pre-Plot Audit

Before chart selection, record:

- Analysis unit and grain.
- Filters, exclusions, weights, and duplicate handling.
- Time window, interval, cutoff convention, and timezone.
- Missingness by group and time.
- Aggregation level and sample/per-group/bin counts.
- Numerator and denominator for every rate, including changing or zero denominators.

Mark the chart `BLOCKED` when denominator, missing-data treatment, or aggregation cannot
be explained. Preserve this context in a caption, note, accessible table, or adjacent text.

## Statistical and Semantic Audit

- State uncertainty appropriate to the estimand and independent sampling unit.
- Use causal language only when the identification strategy warrants it; otherwise
  describe association or observed differences.
- Do not hide material limitations, subgroup effects, period, source, or denominator.
- Verify that scales, baselines, bins, and axis limits do not distort the comparison.

## Accessibility

- Use redundant markers, line styles, labels, or hatches; colorblind-safe palettes alone
  are insufficient.
- Do not put essential information only in hover.
- Test interactive views near 360 px width, touch targets, and keyboard/focus behavior
  where the platform supports it.
- Provide a concise takeaway, meaningful alt text, and an adjacent accessible table or CSV.

## Rendering and Delivery

- Matplotlib: `display(fig)` in Databricks.
- Plotnine: call `p.draw()` and display the resulting matplotlib figure.
- Plotly: `fig.show()`.
- Use explicit reproducible figure sizes rather than notebook defaults.

Minimal static bundle:

```python
from pathlib import Path

out = Path("figures/model_comparison")
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out.with_suffix(".png"), dpi=300)
plotted_data.to_csv(out.with_suffix(".csv"), index=False)
# Add takeaway and alt text in the surface that embeds the image.
```
