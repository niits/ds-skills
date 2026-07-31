"""
swd_style.py — Storytelling with Data style helpers for Databricks notebooks.

Upload to DBFS and import:
    import sys
    sys.path.insert(0, '/dbfs/FileStore/ds-skills/visualization/assets')
    from swd_style import declutter, apply_swd_palette, annotate_insight, SWD
    from swd_style import insight_title, label_bars, highlight_region, fmt_pct

Functions: declutter, apply_swd_palette, annotate_insight,
           insight_title, label_bars, highlight_region, fmt_pct
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------

class SWD:
    """Storytelling with Data color system."""
    ACCENT       = '#C0392B'   # red — the ONE thing that matters (contrast-verified: 5.44:1
                                # vs white, 3.39:1 vs GRAY_LIGHT, clears WCAG 3:1 non-text minimum)

    # Positive/negative pair: never use red+green as the sole differentiator
    # (~8% of men can't reliably distinguish them). This pair is colorblind-safe.
    ACCENT_POSITIVE = '#0072B2'  # blue (Okabe-Ito) — goal achieved, up vs target only
    ACCENT_NEGATIVE = '#D55E00'  # vermillion (Okabe-Ito) — financial loss, error states only

    GRAY_LIGHT   = '#CCCCCC'   # supporting / context data
    GRAY_MED     = '#767676'   # secondary labels and annotations (4.5:1 on white)
    GRAY_DARK    = '#444444'   # primary body text
    NEAR_BLACK   = '#222222'   # chart titles

    BACKGROUND   = '#FFFFFF'
    GRID         = '#EEEEEE'

    # Colorblind-safe alternative palette (Okabe-Ito)
    OKABE_ITO = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
                 '#0072B2', '#D55E00', '#CC79A7', '#000000']


# ---------------------------------------------------------------------------
# Declutter
# ---------------------------------------------------------------------------

def declutter(ax,
              keep_left_spine: bool = False,
              keep_bottom_spine: bool = True,
              gridlines: str = 'horizontal') -> plt.Axes:
    """
    Apply standard Storytelling with Data decluttering to a matplotlib Axes.

    Parameters
    ----------
    ax                : matplotlib.axes.Axes
    keep_left_spine   : Keep the left axis spine (False when using direct labels)
    keep_bottom_spine : Keep the bottom axis spine (False for horizontal bar)
    gridlines         : 'horizontal' | 'both' | 'none'

    Returns
    -------
    ax (mutated in place, also returned for chaining)
    """
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(keep_left_spine)
    ax.spines['bottom'].set_visible(keep_bottom_spine)

    if keep_left_spine:
        ax.spines['left'].set_color(SWD.GRID)
    if keep_bottom_spine:
        ax.spines['bottom'].set_color(SWD.GRID)

    ax.tick_params(length=0, colors=SWD.GRAY_MED, labelsize=9)

    ax.set_facecolor(SWD.BACKGROUND)
    ax.figure.patch.set_facecolor(SWD.BACKGROUND)

    if gridlines == 'horizontal':
        ax.yaxis.grid(True, color=SWD.GRID, linewidth=0.8, zorder=0)
        ax.xaxis.grid(False)
        ax.set_axisbelow(True)
    elif gridlines == 'both':
        ax.grid(True, color=SWD.GRID, linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
    else:
        ax.grid(False)

    return ax


# ---------------------------------------------------------------------------
# Palette helper
# ---------------------------------------------------------------------------

def apply_swd_palette(values: list,
                      highlight_indices=None,
                      accent_color: str = None,
                      base_color: str = None) -> list:
    """
    Build a color list using the SWD pattern: one accent, rest gray.

    Parameters
    ----------
    values           : List of values (used only for length)
    highlight_indices: int or list of ints — indices that get accent color
    accent_color     : Override accent (default: SWD.ACCENT)
    base_color       : Override base gray (default: SWD.GRAY_LIGHT)

    Returns
    -------
    List of color strings, one per value.
    """
    values = list(values)
    accent = accent_color or SWD.ACCENT
    base   = base_color   or SWD.GRAY_LIGHT

    if highlight_indices is None:
        return [base] * len(values)

    if isinstance(highlight_indices, int):
        highlight_indices = [highlight_indices]
    invalid = [i for i in highlight_indices if not 0 <= i < len(values)]
    if invalid:
        raise IndexError(f"highlight indices out of range: {invalid}")

    return [accent if i in highlight_indices else base
            for i in range(len(values))]


# ---------------------------------------------------------------------------
# Annotation helper
# ---------------------------------------------------------------------------

def annotate_insight(ax,
                     x, y,
                     text: str,
                     offset=(3, 5),
                     color: str = None,
                     fontsize: int = 9,
                     arrow: bool = True) -> None:
    """
    Add a narrative annotation with an arrow to a specific data point.

    Parameters
    ----------
    ax     : matplotlib Axes
    x, y   : Data coordinates of the annotated point
    text   : Annotation text (use \\n for line breaks)
    offset : (dx, dy) offset from the data point to the text box
    color  : Text and arrow color (default: SWD.GRAY_DARK)
    fontsize: Font size
    arrow  : Whether to draw an arrow
    """
    c = color or SWD.GRAY_DARK

    arrow_props = (dict(arrowstyle='->', color=c, lw=1.2,
                        connectionstyle='arc3,rad=0.15')
                   if arrow else None)

    ax.annotate(
        text=text,
        xy=(x, y),
        xytext=offset,
        textcoords='offset points',
        arrowprops=arrow_props,
        fontsize=fontsize,
        color=c,
        ha='left',
        va='bottom',
        zorder=10,
    )


# ---------------------------------------------------------------------------
# Title helper
# ---------------------------------------------------------------------------

def insight_title(ax, title: str, fontsize: int = 11) -> None:
    """
    Set a left-aligned, bold insight title — the SWD way.
    The title should be the takeaway, not the topic.
    """
    ax.set_title(title, loc='left', pad=10,
                 fontsize=fontsize, fontweight='bold',
                 color=SWD.NEAR_BLACK)


# ---------------------------------------------------------------------------
# Bar value labels
# ---------------------------------------------------------------------------

def label_bars(ax, bars, values, fmt='{:.0f}', offset_frac=0.02,
               highlight_indices=None, fontsize=9, orientation=None):
    """
    Add direct value labels above / beside each bar.

    Works for both vertical (ax.bar) and horizontal (ax.barh) BarContainers.
    """
    if highlight_indices is None:
        highlight_indices = []
    if isinstance(highlight_indices, int):
        highlight_indices = [highlight_indices]

    values = list(values)
    orientation = orientation or getattr(bars, 'orientation', None)
    if orientation not in {'vertical', 'horizontal'}:
        raise ValueError("orientation must be 'vertical' or 'horizontal'")
    max_val = max((abs(v) for v in values), default=1) or 1
    offset  = max_val * offset_frac

    for i, (bar, val) in enumerate(zip(bars, values)):
        color  = SWD.GRAY_DARK
        weight = 'bold'   if i in highlight_indices else 'normal'
        label  = fmt.format(val)

        if orientation == 'horizontal':
            x = bar.get_width() + (offset if val >= 0 else -offset)
            ax.text(x,
                    bar.get_y() + bar.get_height() / 2,
                    label, va='center', ha='left' if val >= 0 else 'right',
                    fontsize=fontsize, color=color, fontweight=weight)
        else:
            y = bar.get_height() + (offset if val >= 0 else -offset)
            ax.text(bar.get_x() + bar.get_width() / 2,
                    y,
                    label, va='bottom' if val >= 0 else 'top', ha='center',
                    fontsize=fontsize, color=color, fontweight=weight)


# ---------------------------------------------------------------------------
# Highlight region
# ---------------------------------------------------------------------------

def highlight_region(ax, x_start, x_end, label: str = '',
                     color: str = None, alpha: float = 0.12) -> None:
    """Shade a vertical band to enclose / highlight a time period."""
    c = color or SWD.ACCENT
    ax.axvspan(x_start, x_end, alpha=alpha, color=c, zorder=0)
    if label:
        mid = x_start + (x_end - x_start) / 2
        ax.text(mid, 0.97, label, transform=ax.get_xaxis_transform(),
                ha='center', va='top', fontsize=8,
                color=c, style='italic')


# ---------------------------------------------------------------------------
# Formatting helper
# ---------------------------------------------------------------------------

def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format a float as a percentage string. fmt_pct(0.1234) → '12.3%'"""
    return f'{value * 100:.{decimals}f}%'
