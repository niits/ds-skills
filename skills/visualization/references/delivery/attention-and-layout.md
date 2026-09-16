# Attention, Layout, and Decluttering

Use this reference during the communication workflow, after the chart's evidence and encoding are
correct. Design should clarify the argument, not compensate for weak analysis.

## Perceptual Priorities

Prefer visual channels people compare accurately:

1. Position on a common scale.
2. Length.
3. Angle or slope.
4. Area or size.
5. Color intensity or hue.

Use size only for coarse magnitude, not precise values. Use color for category identity or focus,
not as the sole carrier of a quantitative claim.

## Direct Attention

- When one item is the message, use one accent and neutral context.
- When category identity matters, use a verified qualitative palette and redundant labels,
  markers, or line styles. Do not gray categories that readers must distinguish.
- Use bold text or larger type for the main number; keep supporting text visually subordinate.
- Shade a range only when the range itself has meaning, such as an intervention period or target
  zone, and label it directly.
- Connect points only when order or continuity is meaningful. Do not draw lines across unordered
  categories.
- Use rank order when rank is the message. Otherwise use a meaningful temporal, ordinal,
  geographic, conventional, or lookup-friendly order.

Palette definitions and color validation live in `color-palettes.md`.

## Gestalt Rules With Practical Value

- **Proximity:** Place labels next to what they label and group related items spatially.
- **Similarity:** Keep category colors and line styles consistent across a deliverable.
- **Enclosure:** Use a subtle boundary or shaded region to group related evidence.
- **Continuity:** Lines imply sequence; viewers will infer intermediate values.
- **Figure-ground:** Make focal evidence prominent and context quiet.

## Declutter Pass

For each element ask: “If I remove this, is information lost?” Remove it if not; de-emphasize it
if it is only supporting structure.

- Remove 3D effects, shadows, decorative gradients, background images, and redundant borders.
- Keep only gridlines needed to estimate values; make them lighter than the data.
- Prefer direct labels when they remain readable. Otherwise keep a concise, non-overlapping
  legend. Never remove a legend before replacing its information.
- Label notable points, endpoints, or exceptions rather than every point.
- A shared chart may remove a quantitative axis only when direct labels and nearby text preserve
  the measure, unit, baseline, and scale. Quick EDA keeps labeled axes.
- Keep chart titles, annotations, axis labels, and tick labels when each contributes distinct
  context. Remove duplicated wording.

## Layout

- Use whitespace to separate ideas, not to decorate.
- Align titles, plot areas, and annotations to a simple grid.
- Use one readable font family and vary weight before changing family.
- Inspect at final dimensions; avoid rotated labels when horizontal bars or shorter labels work.
- Use small multiples for repeated comparisons. Keep scales shared by default so panels remain
  comparable.

Accessibility validation, source notes, and adjacent-data requirements live in
`audit-and-delivery.md`.
