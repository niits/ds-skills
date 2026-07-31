# Scientific Color Palettes and Guidelines

## Overview

Color choice in scientific visualization is critical for accessibility, clarity, and accurate data representation. This reference provides colorblind-friendly palettes and best practices for color usage.

## Colorblind-Friendly Palettes

### Okabe-Ito Palette (Recommended for Categories)

The Okabe-Ito palette is specifically designed to be distinguishable by people with all forms of color blindness.

```python
# Okabe-Ito colors (RGB values)
okabe_ito = {
    'orange': '#E69F00',      # RGB: (230, 159, 0)
    'sky_blue': '#56B4E9',    # RGB: (86, 180, 233)
    'bluish_green': '#009E73', # RGB: (0, 158, 115)
    'yellow': '#F0E442',      # RGB: (240, 228, 66)
    'blue': '#0072B2',        # RGB: (0, 114, 178)
    'vermillion': '#D55E00',  # RGB: (213, 94, 0)
    'reddish_purple': '#CC79A7', # RGB: (204, 121, 167)
    'black': '#000000'        # RGB: (0, 0, 0)
}
```

**Usage in Matplotlib:**
```python
import matplotlib.pyplot as plt

colors = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
          '#0072B2', '#D55E00', '#CC79A7', '#000000']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
```

**Usage in Seaborn:**
```python
import seaborn as sns

okabe_ito_palette = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
                      '#0072B2', '#D55E00', '#CC79A7']
sns.set_palette(okabe_ito_palette)
```

**Usage in Plotly:**
```python
import plotly.graph_objects as go

okabe_ito_plotly = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
                     '#0072B2', '#D55E00', '#CC79A7']
fig = go.Figure()
# Apply to discrete color scale
```

### Wong Palette (same colors, different citation)

Bang Wong's 2011 Nature Methods "Points of View" column popularized this exact palette — it is
the same 8 colors as Okabe-Ito above (just commonly listed with black first). It is not a
perceptually distinct second option; use it only if your audience specifically expects the
"Wong palette" citation.

```python
wong_palette = {
    'black': '#000000',
    'orange': '#E69F00',
    'sky_blue': '#56B4E9',
    'green': '#009E73',
    'yellow': '#F0E442',
    'blue': '#0072B2',
    'vermillion': '#D55E00',
    'purple': '#CC79A7'
}
```

### Paul Tol Palettes

Paul Tol has designed multiple scientifically-optimized palettes for different use cases.

**Bright Palette (up to 7 categories):**
```python
tol_bright = ['#4477AA', '#EE6677', '#228833', '#CCBB44',
              '#66CCEE', '#AA3377', '#BBBBBB']
```

**Muted Palette (up to 9 categories):**
```python
tol_muted = ['#332288', '#88CCEE', '#44AA99', '#117733',
             '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']
```

**High Contrast (3 categories only):**
```python
tol_high_contrast = ['#004488', '#DDAA33', '#BB5566']
```

## Sequential Colormaps (Continuous Data)

Sequential colormaps represent data from low to high values with a single hue.

### Perceptually Uniform Colormaps

These colormaps have uniform perceptual change across the color scale.

**Viridis (default in Matplotlib):**
- Colorblind-friendly
- Prints well in grayscale
- Perceptually uniform
```python
plt.imshow(data, cmap='viridis')
```

**Cividis:**
- Optimized for colorblind viewers
- Designed specifically for deuteranopia/protanopia
```python
plt.imshow(data, cmap='cividis')
```

**Plasma, Inferno, Magma:**
- Perceptually uniform alternatives to viridis
- Good for different aesthetic preferences
```python
plt.imshow(data, cmap='plasma')
```

### When to Use Sequential Maps
- Heatmaps showing intensity
- Geographic elevation data
- Probability distributions
- Any single-variable continuous data (low → high)

## Diverging Colormaps (Negative to Positive)

Diverging colormaps have a neutral middle color with two contrasting colors at extremes.

### Colorblind-Safe Diverging Maps

Verified against `RColorBrewer::brewer.pal.info`'s `colorblindlist`. This table must stay in
sync with `assets/color_palettes.py`'s `DIVERGING_COLORMAPS_SAFE` — same six maps, no more, no
less; update both together.

| Colormap | Matplotlib name | Notes |
|---|---|---|
| Red-Yellow-Blue | `RdYlBu` (or `RdYlBu_r`) | `_r` reverses: blue (low) to red (high) |
| Red-Blue | `RdBu` (or `RdBu_r`) | Standard choice for correlation/delta data |
| Purple-Orange | `PuOr` | Excellent for colorblind viewers |
| Brown-Blue-Green | `BrBG` | Good colorblind accessibility |
| Purple-Green | `PRGn` | Confirmed safe (not "use with caution") |
| Pink-Yellow-Green | `PiYG` | Confirmed safe (not "use with caution") |

```python
plt.imshow(data, cmap='RdBu_r')  # example usage, any map above works the same way
```

### Avoid These Diverging Maps
- **RdYlGn (Red-Yellow-Green)**: Problematic for red-green colorblindness
- **RdGy (Red-Gray)**: Same issue

### When to Use Diverging Maps
- Correlation matrices
- Change/difference data (positive vs. negative)
- Deviation from a central value
- Temperature anomalies

## Color Usage Best Practices

### Categorical Data (Qualitative Color Schemes)

**Do:**
- Use distinct, saturated colors from Okabe-Ito or Wong palette
- Limit to 7-8 categories max in one plot
- Use consistent colors for same categories across figures
- Add patterns/markers when colors alone might be insufficient
- Remember that color-vision-safe does not guarantee sufficient contrast on white.
  Use dark borders/text for light fills and redundant line styles/markers for thin lines.

**Don't:**
- Use red/green combinations
- Use rainbow (jet) colormap for categories
- Use similar hues that are hard to distinguish

### Continuous Data (Sequential/Diverging Schemes)

**Do:**
- Use perceptually uniform colormaps (viridis, plasma, cividis)
- Choose diverging maps when data has meaningful center point
- Include colorbar with labeled ticks
- Test appearance in grayscale

**Don't:**
- Use rainbow (jet) colormap - not perceptually uniform
- Use red-green diverging maps
- Omit colorbar on heatmaps

## Testing for Colorblind Accessibility

### Online Simulators
- **Coblis**: https://www.color-blindness.com/coblis-color-blindness-simulator/
- **Color Oracle**: Free downloadable tool for Windows/Mac/Linux
- **Sim Daltonism**: Mac application

### Types of Color Vision Deficiency
- **Deuteranomaly** (~5% of males): Green-weak (anomalous trichromacy) — the most common CVD;
  green hues appear shifted/muted, not indistinguishable
- **Protanomaly** (~1% of males): Red-weak (anomalous trichromacy) — similar, milder shift
- **Deuteranopia** (~1% of males): Green-blind (dichromacy) — cannot distinguish red from green
- **Protanopia** (~1% of males): Red-blind (dichromacy) — cannot distinguish red from green
- **Tritanopia/Tritanomaly** (~0.01% combined, both sexes): Blue-yellow confusion; rare and
  autosomal (unlike the X-linked red-green types above)

Combined, deuteranomaly + protanomaly + deuteranopia + protanopia account for the skill's
"~8% of males" figure used elsewhere in this reference set.

### Python Tools
```python
# Using colorspacious to simulate colorblind vision on an RGB image array
from colorspacious import cspace_convert

def simulate_cvd(image_rgb, cvd_type="deuteranomaly", severity=100):
    """
    Simulate color vision deficiency on an RGB image (float array, 0-1 range).

    cvd_type: 'deuteranomaly' (green-weak, most common), 'protanomaly' (red-weak),
              or 'tritanomaly' (blue-weak, rare)
    severity: 0-100, where 100 is full dichromacy
    """
    cvd_space = {"name": "sRGB1+CVD", "cvd_type": cvd_type, "severity": severity}
    return cspace_convert(image_rgb, cvd_space, "sRGB1").clip(0, 1)
```

## Implementation Examples

### Setting Global Matplotlib Style
```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set Okabe-Ito as default color cycle
okabe_ito_colors = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
                     '#0072B2', '#D55E00', '#CC79A7']
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=okabe_ito_colors)

# Set default colormap to viridis
mpl.rcParams['image.cmap'] = 'viridis'
```

### Seaborn with Custom Palette
```python
import seaborn as sns

# Set Paul Tol muted palette
tol_muted = ['#332288', '#88CCEE', '#44AA99', '#117733',
             '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']
sns.set_palette(tol_muted)

# For heatmaps
sns.heatmap(data, cmap='viridis', annot=True)
```

### Plotly with Discrete Colors
```python
import plotly.express as px

# Use Okabe-Ito for categorical data
okabe_ito_plotly = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
                     '#0072B2', '#D55E00', '#CC79A7']

fig = px.scatter(df, x='x', y='y', color='category',
                 color_discrete_sequence=okabe_ito_plotly)
```

## Grayscale Compatibility

All figures should remain interpretable in grayscale. Test by converting to grayscale:

```python
# Render, then convert the exported image for a grayscale preview
from PIL import Image
fig.savefig('figure.png', dpi=300)
Image.open('figure.png').convert('L').save('figure_gray.png')
```

**Strategies for grayscale compatibility:**
1. Use different line styles (solid, dashed, dotted)
2. Use different marker shapes (circles, squares, triangles)
3. Add hatching patterns to bars
4. Ensure sufficient luminance contrast between colors

## Common Mistakes

1. **Using jet/rainbow colormap**: Not perceptually uniform; avoid
2. **Red-green combinations**: ~8% of males cannot distinguish
3. **Too many colors**: More than 7-8 becomes difficult to distinguish
4. **Inconsistent color meaning**: Same color should mean same thing across figures
5. **Missing colorbar**: Always include for continuous data
6. **Low contrast**: Ensure colors differ sufficiently
7. **Relying solely on color**: Add texture, patterns, or markers

## Resources

- **ColorBrewer**: http://colorbrewer2.org/ - Choose palettes by colorblind-safe option
- **Paul Tol's palettes**: https://personal.sron.nl/~pault/
- **Okabe-Ito palette origin**: "Color Universal Design" (Okabe & Ito, 2008)
- **Matplotlib colormaps**: https://matplotlib.org/stable/tutorials/colors/colormaps.html
- **Seaborn palettes**: https://seaborn.pydata.org/tutorial/color_palettes.html
