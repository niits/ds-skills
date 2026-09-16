# Chart Selection

Choose from the analytical question and variable types. These are defaults, not a catalog of
mandatory templates.

| Question | Default | Important condition |
|---|---|---|
| Distribution of one numeric variable | Histogram or density | Show bin or bandwidth choices when material. |
| Numeric distribution across categories | Boxplot, violin, or points plus intervals | Show support; boxplots hide distribution shape. |
| Relationship between two numeric variables | Scatterplot | Use transparency for overlap; a fit is optional evidence, not decoration. |
| Change over ordered time | Line or points connected in order | Sort time; do not imply continuity unsupported by sampling. |
| Two comparable endpoints across groups | Slope chart | Label both endpoints and absolute or percentage change. |
| Compare category values | Bars or dots | Start bars at zero; sort by rank or a meaningful natural order. |
| Count observations by category | Bars after explicit counting | Distinguish counts from already-computed values. |
| Compare the same measure across groups | Facets or a small number of lines | Keep scales fixed unless the loss of comparison is intentional. |
| Show total and composition | Stacked bars or area | Middle segments lack a shared baseline; do not use for precise comparison. |
| Show geography | Map plus ranked or count view | Area represents land, not affected population. |
| Show one headline value | Number plus benchmark or short trend | Supply denominator, period, and comparison. |

## Layout Defaults

- Prefer horizontal bars for long labels or many categories.
- Prefer direct labels when readable; otherwise use a concise legend.
- Keep labeled axes in Quick EDA. In shared output, remove an axis only when direct labels and
  nearby text preserve the measure, unit, baseline, and scale.
- Add uncertainty when it is material and name the interval or band.
- Use a log scale only when the range or relationship justifies it; disclose it clearly.

## Avoid or Qualify

| Form | Risk | Better default |
|---|---|---|
| 3D chart | Perspective distorts values | 2D position or length |
| Dual y-axis | Arbitrary scales can manufacture relationships | Separate aligned panels or indexed comparison |
| Pie/donut with many slices | Angles are difficult to compare | Sorted bars |
| Radar chart | Multiple radial axes impede comparison | Bars, dots, or small multiples |
| Bubble size for exact values | Area is decoded imprecisely | Position, length, or direct values |
| Stacked area with many series | Middle series are hard to compare | Facets or selected lines |

Bubble size remains acceptable for coarse ordinal magnitude when precise reading is not required.
Pair color-only or size-only encodings with labels or another redundant cue.
