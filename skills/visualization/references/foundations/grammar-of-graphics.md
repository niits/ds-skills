# Grammar of Graphics

Grammar of Graphics (GoG) describes a chart as a composition rather than a named template. Use it
to plan and critique charts regardless of renderer. Use current official plotnine documentation
for exact APIs rather than relying on a bundled tutorial.

## Contents

- Mental model and tabular data
- Aesthetics, geoms, stats, and positions
- Scales, coordinates, and facets
- Chart autopsy
- Agent checklist and failure modes
- Plotnine implementation resources

## Mental Model

```text
plot = data
     + aesthetic mappings
     + layers(geom, stat, position)
     + scales
     + coordinates
     + facets
     + labels and theme
```

- **Data:** the subject; define what one row represents.
- **Aesthetics:** links from variables to position, color, fill, size, shape, alpha, or group.
- **Geoms:** visible marks such as points, lines, bars, boxes, and areas.
- **Stats:** computations such as counts, bins, summaries, and smoothers.
- **Positions:** arrangements such as identity, stacking, dodging, and jitter.
- **Scales:** translations from data values to visual values, labels, and guides.
- **Coordinates:** the final viewing system or display transformation.
- **Facets:** repeated views for subsets of the data.
- **Labels and theme:** context and presentation that do not change the underlying data.

A layer is one statement in a visual argument. Add a layer only when its meaning can be explained.

## Start With the Table

In tabular data, each row is one observation at a declared grain and each column is one variable
measured or assigned for those observations. Before plotting, identify:

1. Row grain and population.
2. Numeric, categorical, ordinal, and temporal variables.
3. Filters, period, aggregation, and missing-data treatment.
4. Unit and numerator/denominator when applicable.
5. One analytical question; for shared output, one intended takeaway.

## Aesthetic Mappings

Mappings are data-driven; settings are constants. In plotnine, mappings belong inside `aes()` and
settings outside it:

```python
aes(x="month", y="rate", color="segment")  # mappings
geom_line(color="#0072B2")                  # fixed setting
```

Use position first for precise quantitative comparisons. Avoid mapping many channels at once;
every channel adds decoding work and needs a guide or direct explanation.

## Geoms and Questions

| Analytical question | Default representation |
|---|---|
| Relationship between two numeric variables | Points |
| Change over ordered time | Line after sorting time |
| Distribution of one numeric variable | Histogram or density |
| Numeric distribution across categories | Boxplot, violin, or points plus intervals |
| Count observations by category | Counted bars |
| Display already-computed category values | Columns or bars |
| Rank categories | Sorted horizontal bars |
| Compare one measure across groups | Facets or a small number of lines |
| Show total and composition over time | Stacked area, with comparison limits stated |
| Show geographic concentration | Map plus a ranked/count view when area may distort importance |

Choose marks from the question and variable types, not from a memorized catalog. Detailed
selection guidance lives in `chart-selection.md`.

## Stats and Positions

Many geoms hide a computation. A bar geom may count rows; a column geom uses supplied values.
Histograms bin observations and smoothers estimate relationships. State what was computed when
bins, summaries, weighting, or model choices affect interpretation.

- `identity`: draw at the data position.
- `stack`: show totals and composition; middle segments lack a shared baseline.
- `dodge`: place groups side by side; becomes crowded quickly.
- `jitter`: reveal overlap with small displacement; disclose that positions were altered.

## Scales, Coordinates, and Facets

Scales control how values become positions, colors, sizes, labels, and guides. Start bars at zero.
Use logarithmic scales only when justified and label the transformation. Explain non-zero line
baselines.

Coordinates change the final viewing system. For example, flipping coordinates can make category
labels easier to read without changing the underlying mappings.

Facets apply the same grammar to data subsets. Keep scales fixed by default so panels remain
comparable. Use free scales only when the loss of direct comparison is intentional and disclosed.

## Chart Autopsy

Before reproducing an expert chart, reconstruct its grammar:

```text
Question:
Intended takeaway:
Observational unit / row grain:
Population and filters:
x:
y:
color / fill / size / shape / group:
geom(s) and layer order:
statistical transformation:
position adjustment:
scale and coordinate transformations:
facets:
annotations and reference values:
source, period, unit, and denominator:
uncertainty or missing-data treatment:
main conclusion:
possible misinterpretation:
```

Apply this template to Our World in Data's life-expectancy chart
<https://ourworldindata.org/grapher/life-expectancy>. Check whether connected historical
observations imply more continuity than the data supports. For a map, ask whether land area is
being mistaken for affected population.

## Agent Checklist

For GoG teaching and shared chart creation:

1. Apply the audit in `../delivery/audit-and-delivery.md` when the metric or delivery is non-trivial.
2. State the question; add a takeaway only for shared output.
3. Justify the chart from the question and variable types.
4. Express the grammar before implementation.
5. Build the simplest layer first and explain every stat, transform, and added layer.
6. Interpret only after rendering; include a likely misreading or limitation.

## Common Failure Modes

- Mapping a constant or setting a data-driven value.
- Confusing counted bars with supplied values.
- Drawing lines across unordered categories or unsorted time.
- Letting automatic bins, stacking, smoothing, or aggregation hide a decision.
- Using free facet scales without disclosing the lost comparison.
- Using color as decoration or as the sole carrier of meaning.
- Treating a grammatically valid or attractive chart as analytically meaningful.
- Reporting association as causation.
- Reproducing a style without its definitions, source, and methodological notes.

## Plotnine Implementation

Use plotnine when grouped mappings, facets, or statistical layers make the grammar clearer than
imperative matplotlib code. Verify the installed version before relying on newer APIs.

- Overview: <https://plotnine.org/guide/overview.html>
- Aesthetic mappings: <https://plotnine.org/guide/aesthetic-mappings.html>
- API reference: <https://plotnine.org/reference/>

In Databricks, draw the underlying matplotlib figure before display:

```python
fig = p.draw()
display(fig)
```
