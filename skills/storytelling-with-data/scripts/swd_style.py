"""
swd_style.py — Storytelling with Data style helpers for Databricks notebooks.

Upload to DBFS and import:
    import sys
    sys.path.insert(0, '/dbfs/FileStore/ds-skills/storytelling-with-data/scripts')
    from swd_style import declutter, apply_swd_palette, annotate_insight, SWD
    from swd_style import risk_colormap, psi_status, fmt_pct, fmt_bps

General helpers : declutter, apply_swd_palette, annotate_insight,
                  insight_title, label_bars, highlight_region
Domain helpers  : risk_colormap, psi_status, fmt_pct, fmt_bps, waterfall_colors
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------

class SWD:
    """Storytelling with Data color system."""
    ACCENT       = '#E8664A'   # coral — the ONE thing that matters
    ACCENT_BLUE  = '#1A77B5'   # blue — second emphasis (use sparingly)
    ACCENT_GREEN = '#27AE60'   # green — positive outcome / goal achieved
    ACCENT_RED   = '#C0392B'   # red — negative / loss / critical (financial contexts)

    GRAY_LIGHT   = '#CCCCCC'   # supporting / context data
    GRAY_MED     = '#888888'   # secondary labels and annotations
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
    accent = accent_color or SWD.ACCENT
    base   = base_color   or SWD.GRAY_LIGHT

    if highlight_indices is None:
        return [base] * len(values)

    if isinstance(highlight_indices, int):
        highlight_indices = [highlight_indices]

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
        xytext=(x + offset[0], y + offset[1]),
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
               highlight_indices=None, fontsize=9):
    """
    Add direct value labels above / beside each bar.

    Works for both vertical (ax.bar) and horizontal (ax.barh) bars.
    """
    if highlight_indices is None:
        highlight_indices = []
    if isinstance(highlight_indices, int):
        highlight_indices = [highlight_indices]

    max_val = max(abs(v) for v in values) if values else 1
    offset  = max_val * offset_frac

    for i, (bar, val) in enumerate(zip(bars, values)):
        color  = SWD.ACCENT if i in highlight_indices else SWD.GRAY_MED
        weight = 'bold'   if i in highlight_indices else 'normal'
        label  = fmt.format(val)

        # Detect orientation
        if bar.get_width() > bar.get_height() * 2:
            # Horizontal bar
            ax.text(bar.get_width() + offset,
                    bar.get_y() + bar.get_height() / 2,
                    label, va='center', ha='left',
                    fontsize=fontsize, color=color, fontweight=weight)
        else:
            # Vertical bar
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + offset,
                    label, va='bottom', ha='center',
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
        mid = (x_start + x_end) / 2
        ymax = ax.get_ylim()[1]
        ax.text(mid, ymax * 0.97, label,
                ha='center', va='top', fontsize=8,
                color=c, style='italic')


# ---------------------------------------------------------------------------
# Domain helpers — credit and risk analytics
# ---------------------------------------------------------------------------

def risk_colormap(kind: str = 'rate'):
    """
    Return a (cmap, norm) pair suitable for risk heatmaps.

    kind='rate'     → 0–100% range, red=high risk  (RdYlGn_r)
    kind='change'   → diverging around 0,            (RdBu_r)
    kind='volume'   → sequential 0→max,              (YlOrRd)

    Usage:
        cmap, norm = risk_colormap('rate')
        sns.heatmap(df, cmap=cmap, vmin=0, vmax=100)
    """
    import matplotlib.colors as mcolors

    if kind == 'rate':
        return 'RdYlGn_r', None
    elif kind == 'change':
        return 'RdBu_r', None
    elif kind == 'volume':
        return 'YlOrRd', None
    else:
        raise ValueError(f"kind must be 'rate', 'change', or 'volume', got {kind!r}")


def psi_status(psi_value: float) -> tuple:
    """
    Return (color, label) for a PSI value using industry convention.

      < 0.10        → stable
      0.10 – 0.25   → moderate shift
      > 0.25        → significant shift

    Returns
    -------
    (color_hex: str, label: str)
    """
    if psi_value < 0.10:
        return SWD.ACCENT_GREEN, 'Stable'
    elif psi_value < 0.25:
        return '#F39C12', 'Moderate shift — monitor'
    else:
        return SWD.ACCENT, 'Significant shift — investigate'


def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format a float as a percentage string. fmt_pct(0.1234) → '12.3%'"""
    return f'{value * 100:.{decimals}f}%'


def fmt_bps(value: float) -> str:
    """Format a float as basis points. fmt_bps(0.0025) → '25 bps'"""
    return f'{value * 10000:.0f} bps'


def waterfall_colors(shap_values) -> list:
    """
    Return color list for a SHAP waterfall chart.
    Positive SHAP (increases prediction) → accent coral.
    Negative SHAP (decreases prediction) → accent blue.
    """
    return [SWD.ACCENT if v > 0 else SWD.ACCENT_BLUE for v in shap_values]
