# Chart Audit and Delivery

## Pre-Plot Audit

Before chart selection, record:

- Analysis unit and grain.
- Filters, exclusions, weights, and duplicate handling.
- Time window, interval, cutoff convention, and timezone.
- Missingness by group and time.
- Aggregation level and sample/per-group/bin counts.
- Numerator and denominator for every rate, share, ratio, or normalized metric, including
  changing or zero denominators.

Mark the chart `BLOCKED` when aggregation or material missing-data treatment cannot be explained,
or when an applicable numerator or denominator is unknown. Preserve this context in a caption,
note, accessible table, or adjacent text for shared charts.

For Quick EDA, this audit may be a terse code-and-reasoning check. The full delivery requirements
below apply when the chart is shared as a slide, infographic, report, or publication artifact.

## Statistical and Semantic Audit

- State uncertainty appropriate to the estimand and independent sampling unit. Name its
  computation: for example SD for dispersion, a confidence interval for estimation uncertainty,
  or a prediction interval for future observations.
- Report `n` and material group/bin support. When inference is relevant, report effect size and
  interval; identify the test, assumptions, and multiplicity handling rather than using stars
  alone.
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
- Inspect static output at final dimensions and in grayscale. Use a color-vision-deficiency
  simulator when available; otherwise record that simulation was not performed and rely on
  redundant encodings rather than color alone.
- Report checks as performed or pending. Do not claim accessibility or rendering validation that
  the environment did not permit.
- Provide a concise takeaway, meaningful alt text, and an adjacent accessible table or CSV.

## Rendering and Delivery

- Matplotlib: `plt.show()` in a standard Python environment or `display(fig)` in Databricks.
- Plotnine, when selected for a layered or faceted communication chart: call `p.draw()` and
  display the resulting matplotlib figure in Databricks.
- Use explicit reproducible figure sizes rather than notebook defaults.

For a standalone caption or adjacent note, include what is shown, the main takeaway, population,
period, unit, uncertainty definition, source, and material limitation. Follow the destination's
author guidelines for dimensions, format, typography, and other submission mechanics.

Minimal static bundle:

```python
from pathlib import Path

out = Path("figures/model_comparison")
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out.with_suffix(".png"), dpi=300)
plotted_data.to_csv(out.with_suffix(".csv"), index=False)
# Add takeaway and alt text in the surface that embeds the image.
```
