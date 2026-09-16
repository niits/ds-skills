# Color Selection and Validation

Color must encode category, magnitude, or focus. It is not decoration, and essential meaning must
not depend on color alone. The executable definitions live in `../../assets/color_palettes.py`.

## Categorical Color

Use the Okabe-Ito palette when categories must remain distinct:

```python
OKABE_ITO = [
    "#E69F00", "#56B4E9", "#009E73", "#F0E442",
    "#0072B2", "#D55E00", "#CC79A7", "#000000",
]
```

Bang Wong's commonly cited palette is the same set in a different order, not a second palette.
Paul Tol's palettes in `../../assets/color_palettes.py` provide alternatives for different category
counts.

- Keep category-color mappings consistent across a deliverable.
- Add direct labels, marker shapes, line styles, or hatching when category identity is essential.
- Check contrast for light colors on a white background.
- If more than about eight categories must be distinguished simultaneously, reduce, group, or
  facet them rather than cycling colors.

## Continuous Color

Use a **sequential** map for low-to-high magnitude. `viridis` and `cividis` are useful defaults.
Use a **diverging** map only when the data has a meaningful center such as zero or a target.
Always include a labeled colorbar.

The table below must match `DIVERGING_COLORMAPS_SAFE` in `../../assets/color_palettes.py`.

| Matplotlib map | Typical use |
|---|---|
| `RdYlBu` / `RdYlBu_r` | Ordered deviation with a visible midpoint |
| `RdBu` / `RdBu_r` | Correlation or signed delta |
| `PuOr` | Signed contrast |
| `BrBG` | Signed contrast |
| `PRGn` | Signed contrast |
| `PiYG` | Signed contrast |

Avoid `jet`, rainbow scales, `RdYlGn`, and `RdGy`: they are perceptually misleading or unsafe for
common color-vision deficiencies.

## Focus Versus Category

- When one item is the message, use one accent and neutral context.
- When several categories must remain identifiable, use a qualitative palette instead of graying
  them all.
- Do not use red and green as the sole positive/negative distinction. Add position, signs, labels,
  or line styles.

## Validation

1. Inspect the rendered chart at final size.
2. Convert it to grayscale and verify that the message survives.
3. Use a color-vision-deficiency simulator when available.
4. Check labels and fills for sufficient foreground/background contrast.
5. Record simulation as performed or pending; do not claim a test that was not run.

```python
from PIL import Image

fig.savefig("figure.png", dpi=150)
Image.open("figure.png").convert("L").save("figure-gray.png")
```

Useful external checks include Coblis, Color Oracle, Viz Palette, and ColorBrewer's colorblind-safe
filter. These checks do not replace redundant encoding.

## Sources

- Okabe and Ito, *Color Universal Design* (2008).
- Bang Wong, “Points of View: Color blindness,” *Nature Methods* (2011).
- Paul Tol, *Colour Schemes*.
- Matplotlib colormap guidance: <https://matplotlib.org/stable/users/explain/colors/colormaps.html>
