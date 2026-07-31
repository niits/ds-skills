# Figure Guidelines: Accuracy, Clarity, and Accessibility

## Core Principles

Figures must be clear, accurate, and accessible:

1. **Clarity**: Information should be immediately understandable
2. **Accuracy**: Data representation must be truthful and unmanipulated
3. **Accessibility**: Figures should be interpretable by all readers, including those with
   visual impairments

## Color Usage

### Color Selection Principles
1. **Colorblind-friendly**: ~8% of males have color vision deficiency
   - Avoid red/green combinations
   - Use blue/orange, blue/yellow, or add texture/pattern
   - Test with colorblindness simulators
2. **Purposeful color**: Color should convey meaning, not just aesthetics
   - Use color to distinguish categories or highlight key data
   - Maintain consistency across figures (same treatment = same color)

### Recommended Color Palettes
- **Qualitative (categories)**: ColorBrewer, Okabe-Ito palette — see `color-palettes.md`
- **Sequential (low to high)**: Viridis, Cividis, Blues, Oranges
- **Diverging (negative to positive)**: colorblind-safe diverging colormap — see `color-palettes.md`

### Grayscale Compatibility
- All figures should be interpretable in grayscale
- Use different line styles (solid, dashed, dotted) and markers
- Add patterns/hatching to bars and areas

## Data Representation Best Practices

### Statistical Rigor
- **Uncertainty**: Show the quantity appropriate to the estimand and design (SD for
  dispersion, SEM for mean sampling uncertainty, CI, prediction interval, or
  cluster/bootstrap interval) and define its computation and independent unit
- **Sample size**: Indicate n in figure or caption
- **Inference**: Report effect size and interval. If a test is relevant, state the
  estimand, test, assumptions, `n`, exact multiplicity-adjusted p-value, and avoid stars alone.
- **Replicates**: Show individual data points when possible, not just summary statistics

### Appropriate Chart Types
- **Bar plots**: Comparing discrete categories; always start y-axis at zero
- **Line plots**: Time series or continuous relationships
- **Scatter plots**: Correlation between variables; add regression line if appropriate
- **Box plots**: Distribution comparisons; show outliers
- **Heatmaps**: Matrix data, correlations, attention/activation patterns
- **Violin plots**: Distribution shape comparison (better than box plots for bimodal data)

### Avoiding Distortion
- **No 3D effects**: Distorts perception of values
- **No unnecessary decorations**: No gradients, shadows, or chart junk
- **Consistent scales**: Use same scale for comparable panels
- **No truncated axes**: Unless clearly indicated and scientifically justified
- **Linear vs. log scales**: Choose appropriate scale; always label clearly

## Accessibility

### Colorblind Considerations
- Test with online simulators (e.g., Coblis, Color Oracle)
- Use patterns/textures in addition to color
- Provide alternative representations in supplementary materials if needed

### Visual Impairment
- High contrast between elements
- Thick enough lines (minimum 0.5 pt)
- Clear, uncluttered layouts

### Data Availability
- Include data tables in supplementary materials
- Provide source data files for graphs

## Common Mistakes to Avoid

1. **Chart junk**: Unnecessary grid lines, 3D effects, decorations
2. **Poor color choices**: Red/green combinations, low contrast
3. **Missing elements**: No axis labels, units, denominator, sample size, or appropriate
   uncertainty
4. **Data distortion**: Truncated axes, inappropriate scales, 3D effects
5. **Too much information**: Cramming too many data series into one plot
6. **Inaccessible legends**: Legends outside the figure boundary after export
