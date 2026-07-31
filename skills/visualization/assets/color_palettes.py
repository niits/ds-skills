"""
Colorblind-Friendly Color Palettes for Scientific Visualization

This module provides carefully curated color palettes optimized for
scientific publications and accessibility.

Usage:
    from color_palettes import OKABE_ITO, apply_palette
    import matplotlib.pyplot as plt

    apply_palette('okabe_ito')
    plt.plot([1, 2, 3], [1, 4, 9])
"""

# Okabe-Ito Palette (2008)
# The most widely recommended colorblind-friendly palette
OKABE_ITO = {
    'orange': '#E69F00',
    'sky_blue': '#56B4E9',
    'bluish_green': '#009E73',
    'yellow': '#F0E442',
    'blue': '#0072B2',
    'vermillion': '#D55E00',
    'reddish_purple': '#CC79A7',
    'black': '#000000'
}

OKABE_ITO_LIST = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
                   '#0072B2', '#D55E00', '#CC79A7', '#000000']

# Wong Palette (Nature Methods, 2011) — the same 8 colors as Okabe-Ito, just
# reordered (black moved to front). Wong's paper is the citation that popularized
# Okabe & Ito's 2008 palette; it is not a perceptually distinct alternative. Kept
# here as a named alias for readers who know the "Wong palette" citation, not as a
# second option to choose between.
WONG = ['#000000', '#E69F00', '#56B4E9', '#009E73',
        '#F0E442', '#0072B2', '#D55E00', '#CC79A7']

# Paul Tol Palettes (https://personal.sron.nl/~pault/)
TOL_BRIGHT = ['#4477AA', '#EE6677', '#228833', '#CCBB44',
              '#66CCEE', '#AA3377', '#BBBBBB']

TOL_MUTED = ['#332288', '#88CCEE', '#44AA99', '#117733',
             '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']

TOL_LIGHT = ['#77AADD', '#EE8866', '#EEDD88', '#FFAABB',
             '#99DDFF', '#44BB99', '#BBCC33', '#AAAA00', '#DDDDDD']

TOL_HIGH_CONTRAST = ['#004488', '#DDAA33', '#BB5566']

# Sequential colormaps (for continuous data)
SEQUENTIAL_COLORMAPS = [
    'viridis',   # Default, perceptually uniform
    'plasma',    # Perceptually uniform
    'inferno',   # Perceptually uniform
    'magma',     # Perceptually uniform
    'cividis',   # Optimized for colorblind viewers
    'YlOrRd',    # Yellow-Orange-Red
    'YlGnBu',    # Yellow-Green-Blue
    'Blues',     # Single hue
    'Greens',    # Single hue
    'Purples',   # Single hue
]

# Diverging colormaps (for data with meaningful center). Safety verified against
# RColorBrewer::brewer.pal.info's colorblindlist (mirrors colorbrewer2.org's own
# "colorblind safe" filter) — all six below are confirmed safe, no exceptions.
# This list must match references/color-palettes.md's "Colorblind-Safe Diverging Maps"
# table 1:1 (no CI to catch drift mechanically — update both together).
DIVERGING_COLORMAPS_SAFE = [
    'RdYlBu',    # Red-Yellow-Blue (reversed is common)
    'RdBu',      # Red-Blue
    'PuOr',      # Purple-Orange (excellent for colorblind)
    'BrBG',      # Brown-Blue-Green (good for colorblind)
    'PRGn',      # Purple-Green
    'PiYG',      # Pink-Yellow-Green
]

# Diverging colormaps to AVOID (red-green combinations)
DIVERGING_COLORMAPS_AVOID = [
    'RdYlGn',    # Red-Yellow-Green (problematic!)
    'RdGy',      # Red-Gray (problematic!)
]


def apply_palette(palette_name='okabe_ito'):
    """
    Apply a color palette to matplotlib's default color cycle.

    Parameters
    ----------
    palette_name : str
        Name of the palette to apply. Options:
        'okabe_ito', 'wong', 'tol_bright', 'tol_muted',
        'tol_light', 'tol_high_contrast'

    Returns
    -------
    list
        List of colors in the palette

    Examples
    --------
    >>> apply_palette('okabe_ito')
    >>> plt.plot([1, 2, 3], [1, 4, 9])  # Uses Okabe-Ito colors
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed")
        return None

    palettes = {
        'okabe_ito': OKABE_ITO_LIST,
        'wong': WONG,
        'tol_bright': TOL_BRIGHT,
        'tol_muted': TOL_MUTED,
        'tol_light': TOL_LIGHT,
        'tol_high_contrast': TOL_HIGH_CONTRAST,
    }

    if palette_name not in palettes:
        available = ', '.join(palettes.keys())
        raise ValueError(f"Palette '{palette_name}' not found. Available: {available}")

    colors = palettes[palette_name]
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
    return colors


def get_palette(palette_name='okabe_ito'):
    """
    Get a color palette as a list.

    Parameters
    ----------
    palette_name : str
        Name of the palette

    Returns
    -------
    list
        List of color hex codes
    """
    palettes = {
        'okabe_ito': OKABE_ITO_LIST,
        'wong': WONG,
        'tol_bright': TOL_BRIGHT,
        'tol_muted': TOL_MUTED,
        'tol_light': TOL_LIGHT,
        'tol_high_contrast': TOL_HIGH_CONTRAST,
    }

    if palette_name not in palettes:
        available = ', '.join(palettes.keys())
        raise ValueError(f"Palette '{palette_name}' not found. Available: {available}")

    return palettes[palette_name]


if __name__ == "__main__":
    print("Available colorblind-friendly palettes:")
    print(f"  - Okabe-Ito: {len(OKABE_ITO_LIST)} colors")
    print(f"  - Wong: {len(WONG)} colors")
    print(f"  - Tol Bright: {len(TOL_BRIGHT)} colors")
    print(f"  - Tol Muted: {len(TOL_MUTED)} colors")
    print(f"  - Tol Light: {len(TOL_LIGHT)} colors")
    print(f"  - Tol High Contrast: {len(TOL_HIGH_CONTRAST)} colors")

    print("\nOkabe-Ito palette (most recommended):")
    for name, color in OKABE_ITO.items():
        print(f"  {name:15s}: {color}")
