"""
NYT Theme — New York Times visual style for matplotlib, plotly, and plotnine.

Default context: SLIDE (16:9, base_size=15).
For notebooks/publication, call apply_nyt_mpl(base_size=11) explicitly
or use apply_nyt_notebook().

Upload to DBFS and import:
    import sys
    sys.path.insert(0, '/dbfs/FileStore/ds-skills/shared')
    from nyt_theme import apply_nyt_mpl, nyt_plotly_template, theme_nyt, NYT

Design principles (from NYT Graphics):
  - No left spine; horizontal gridlines only, very light (#DEDEDE)
  - Title: left-aligned, bold, slightly larger than body
  - Font: Franklin Gothic / Arial Narrow for data; Georgia for narrative titles
  - Tick marks: none visible (length = 0)
  - Colors: muted, sophisticated — blue primary, no primary red/green
  - One accent color; everything else in gray
"""

from __future__ import annotations
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.cycler import cycler


# ─── Color System ─────────────────────────────────────────────────────────────

class NYT:
    """New York Times color constants."""

    # Categorical palette (NYT Graphics team's typical sequence)
    BLUE    = '#326891'   # primary — the NYT blue
    ORANGE  = '#C9553E'   # contrast / decline
    GREEN   = '#3A7D44'   # positive / growth
    PURPLE  = '#7B5EA7'   # 4th category
    TEAL    = '#2A8C8A'   # 5th category
    SAND    = '#C4A35A'   # 6th category (warm neutral)

    # Full categorical sequence for prop_cycle
    PALETTE = [BLUE, ORANGE, GREEN, PURPLE, TEAL, SAND]

    # Grays
    INK     = '#111111'   # main titles
    DARK    = '#333333'   # secondary text
    MID     = '#555555'   # axis labels, annotations (slightly darker for slide legibility)
    LIGHT   = '#888888'   # de-emphasized labels
    RULE    = '#DEDEDE'   # gridlines, dividers
    BG      = '#FFFFFF'   # background

    # SWD-style one-accent pattern
    HIGHLIGHT = BLUE      # the one thing that matters
    BASELINE  = '#CCCCCC' # everything else

    # Semantic
    POSITIVE = '#3A7D44'
    NEGATIVE = '#C9553E'
    NEUTRAL  = '#555555'


# ─── Figure size presets ───────────────────────────────────────────────────────
# Slide layout (16:9, 13.3×7.5"): header ~0.8", figure ~4.2", body text ~0.9",
# footnote ~0.3", margins ~0.4" top+bottom. Usable width ≈ 12.0" (0.65" margins each side).
#
# These sizes represent the FIGURE AREA within the slide — not the full slide.
# Use them as figsize arguments: fig, ax = plt.subplots(figsize=FIG_SLIDE)

FIG_SLIDE        = (12.0, 4.2)   # single chart, full usable width — standard layout
FIG_HALF_SLIDE   = (5.8,  4.2)   # two charts side-by-side (with ~0.4" gap between)
FIG_THIRD_SLIDE  = (3.7,  4.0)   # three charts across a slide
FIG_TALL_SLIDE   = (9.0,  5.0)   # taller chart when body text is only 1 line
FIG_NOTEBOOK     = (7.0,  4.0)   # compact notebook inline
FIG_NOTEBOOK_WIDE = (10.0, 4.5)  # wide notebook inline


# ─── Font priority list ────────────────────────────────────────────────────────
# NYT uses "NYT Franklin" (proprietary). Best open alternatives:
_SANS_NARROW = [
    'Franklin Gothic Medium', 'Arial Narrow', 'Helvetica Neue',
    'Liberation Sans Narrow', 'Arial', 'DejaVu Sans',
]
_SERIF_TITLE = [
    'Cheltenham', 'Georgia', 'Times New Roman', 'DejaVu Serif',
]


# ─── Matplotlib ───────────────────────────────────────────────────────────────

def _nyt_rcparams(base_size: int = 15) -> dict:
    """Return the NYT rcParams dict (does not apply — call apply_nyt_mpl)."""
    s = base_size
    return {
        # Figure — default is single full-width chart in slide content area
        'figure.facecolor':           NYT.BG,
        'figure.edgecolor':           NYT.BG,
        'figure.figsize':             list(FIG_SLIDE),
        'figure.dpi':                 100,
        'figure.constrained_layout.use': True,

        # Font
        'font.family':                'sans-serif',
        'font.sans-serif':            _SANS_NARROW,
        'font.size':                  s,

        # Axes appearance
        'axes.facecolor':             NYT.BG,
        'axes.edgecolor':             NYT.RULE,
        'axes.linewidth':             1.0,
        'axes.labelsize':             s - 1,
        'axes.labelcolor':            NYT.MID,
        'axes.labelpad':              8,
        'axes.titlesize':             s + 2,
        'axes.titleweight':           'bold',
        'axes.titlecolor':            NYT.INK,
        'axes.titlelocation':         'left',   # always left-aligned
        'axes.titlepad':              12,

        # Spines: only bottom; no left — gridlines carry the y-axis reference
        'axes.spines.top':            False,
        'axes.spines.right':          False,
        'axes.spines.left':           False,
        'axes.spines.bottom':         True,

        'axes.axisbelow':             True,

        # Grid: horizontal only, very light
        'axes.grid':                  True,
        'axes.grid.axis':             'y',
        'grid.color':                 NYT.RULE,
        'grid.linewidth':             0.8,
        'grid.linestyle':             '-',
        'grid.alpha':                 1.0,

        # Ticks: no visible tick marks
        'xtick.major.size':           0,
        'xtick.minor.size':           0,
        'ytick.major.size':           0,
        'ytick.minor.size':           0,
        'xtick.major.pad':            8,
        'ytick.major.pad':            6,
        'xtick.labelsize':            s - 2,
        'ytick.labelsize':            s - 2,
        'xtick.color':                NYT.MID,
        'ytick.color':                NYT.MID,

        # Lines — heavier for slide legibility
        'lines.linewidth':            2.5,
        'lines.solid_capstyle':       'round',
        'lines.dash_capstyle':        'round',
        'lines.markersize':           7,

        # Patches (bars, etc.)
        'patch.edgecolor':            NYT.BG,
        'patch.linewidth':            0.5,

        # Legend
        'legend.frameon':             False,
        'legend.fontsize':            s - 2,
        'legend.labelcolor':          NYT.DARK,
        'legend.borderaxespad':       0,

        # Color cycle
        'axes.prop_cycle':            cycler('color', NYT.PALETTE),

        # Savefig — 150 dpi is sufficient for slides exported to PDF/PNG
        'savefig.dpi':                150,
        'savefig.facecolor':          NYT.BG,
        'savefig.bbox':               'tight',
        'savefig.pad_inches':         0.15,
    }


def apply_nyt_mpl(base_size: int = 15) -> None:
    """
    Apply the NYT style to matplotlib globally (slide-optimized defaults).

    Parameters
    ----------
    base_size : int
        Base font size. Default 15 for slides. Use 11 for notebooks.

    Usage
    -----
    apply_nyt_mpl()                    # slide context (default)
    apply_nyt_mpl(base_size=11)        # notebook/publication context

    fig, ax = plt.subplots(figsize=FIG_HALF_SLIDE)
    ax.plot(x, y)
    ax.set_title("Title IS the takeaway")   # left-aligned automatically
    display(fig); plt.close(fig)
    """
    plt.rcParams.update(_nyt_rcparams(base_size))


def apply_nyt_notebook() -> None:
    """Apply NYT style tuned for notebook inline display (base_size=11)."""
    apply_nyt_mpl(base_size=11)
    # Override figsize to notebook default
    plt.rcParams.update({
        'figure.figsize': list(FIG_NOTEBOOK),
        'lines.linewidth': 2.0,
        'lines.markersize': 5,
    })


def nyt_ax(ax: plt.Axes, title: str = '', subtitle: str = '') -> plt.Axes:
    """
    Apply per-axes NYT finishing touches after apply_nyt_mpl().

    - Adds a top rule line (thick dark line above the chart, NYT convention)
    - Sets title and optional subtitle in different weights
    - Removes y-axis label if gridlines make it redundant

    Parameters
    ----------
    ax       : The axes to style
    title    : Chart title (the insight/takeaway)
    subtitle : Optional subtitle in lighter weight below the title

    Returns
    -------
    ax (mutated, also returned for chaining)
    """
    fs = plt.rcParams.get('axes.titlesize', 17)
    fs_sub = max(fs - 3, 10)

    if title:
        ax.set_title(title, loc='left', fontsize=fs, fontweight='bold',
                     color=NYT.INK, pad=12)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes,
                fontsize=fs_sub, color=NYT.MID, ha='left', va='bottom')

    # Top rule: a thick dark line spanning the top of the figure area
    ax.axhline(y=ax.get_ylim()[1], color=NYT.INK, linewidth=2.5,
               xmin=0, xmax=1, clip_on=False, zorder=5)

    ax.tick_params(axis='both', length=0)
    return ax


# ─── Plotly ───────────────────────────────────────────────────────────────────

def nyt_plotly_template(context: str = 'slide') -> dict:
    """
    Return a Plotly template dict implementing the NYT style.

    Parameters
    ----------
    context : 'slide' (default) or 'notebook'
        'slide'    — larger fonts (16/14/13), heavier lines, wider margins
        'notebook' — compact fonts (12/11/10), standard lines

    Usage
    -----
    import plotly.graph_objects as go
    import plotly.io as pio

    pio.templates['nyt'] = go.layout.Template(nyt_plotly_template())
    pio.templates.default = 'nyt'

    # Or per-figure:
    fig = go.Figure(layout_template=nyt_plotly_template())
    """
    if context == 'slide':
        title_size  = 20
        base_size   = 16
        tick_size   = 14
        legend_size = 14
        line_width  = 3
        marker_size = 9
        margin      = dict(l=50, r=30, t=80, b=60)
    else:
        title_size  = 16
        base_size   = 12
        tick_size   = 10
        legend_size = 11
        line_width  = 2
        marker_size = 6
        margin      = dict(l=40, r=20, t=60, b=40)

    return dict(
        layout=dict(
            # Background
            paper_bgcolor=NYT.BG,
            plot_bgcolor=NYT.BG,

            # Font — data labels and axis text
            font=dict(
                family=', '.join(_SANS_NARROW),
                size=base_size,
                color=NYT.MID,
            ),

            # Title: left-aligned bold
            title=dict(
                font=dict(size=title_size, color=NYT.INK,
                          family=', '.join(_SANS_NARROW)),
                x=0.0,
                xanchor='left',
                pad=dict(t=10, b=6),
            ),

            # Axes
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=True,
                linecolor=NYT.RULE,
                linewidth=1,
                ticks='',
                tickfont=dict(size=tick_size, color=NYT.MID),
                title_font=dict(size=tick_size, color=NYT.MID),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=NYT.RULE,
                gridwidth=0.8,
                zeroline=False,
                showline=False,
                ticks='',
                tickfont=dict(size=tick_size, color=NYT.MID),
                title_font=dict(size=tick_size, color=NYT.MID),
            ),

            # Legend
            legend=dict(
                bgcolor='rgba(0,0,0,0)',
                borderwidth=0,
                font=dict(size=legend_size, color=NYT.DARK),
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='left',
                x=0,
            ),

            # Color sequence
            colorway=NYT.PALETTE,

            # Margin
            margin=margin,

            # Hoverlabel
            hoverlabel=dict(
                bgcolor=NYT.BG,
                bordercolor=NYT.RULE,
                font=dict(size=base_size, color=NYT.INK),
            ),
        ),
        data=dict(
            scatter=[dict(
                line=dict(width=line_width),
                marker=dict(size=marker_size, line=dict(width=0)),
            )],
            bar=[dict(
                marker=dict(line=dict(width=0)),
            )],
        ),
    )


def register_nyt_plotly(context: str = 'slide') -> None:
    """
    Register 'nyt' as a named Plotly template and set as default.

    Parameters
    ----------
    context : 'slide' (default) or 'notebook'

    Call once at the top of your notebook.

    Usage
    -----
    register_nyt_plotly()
    import plotly.express as px
    fig = px.line(df, x='date', y='value', title='Title IS the takeaway')
    fig.show()
    """
    try:
        import plotly.graph_objects as go
        import plotly.io as pio
        pio.templates['nyt'] = go.layout.Template(nyt_plotly_template(context))
        pio.templates.default = 'nyt'
        print(f"✓ Plotly 'nyt' template registered and set as default (context={context})")
    except ImportError:
        print("plotly not available — skipping Plotly template registration")


# ─── Plotnine ─────────────────────────────────────────────────────────────────

def theme_nyt(base_size: int = 15):
    """
    Return a plotnine theme implementing the NYT style (slide-optimized defaults).

    Parameters
    ----------
    base_size : int
        Base font size. Default 15 for slides. Use 11 for notebooks.

    Usage
    -----
    import plotnine as p9
    from nyt_theme import theme_nyt, NYT

    (
        p9.ggplot(df, p9.aes('date', 'value', color='group'))
        + p9.geom_line(size=1.5)
        + p9.scale_color_manual(values=NYT.PALETTE)
        + p9.labs(title='Title IS the takeaway', x='', y='')
        + theme_nyt()                   # slide (default)
        + theme_nyt(base_size=11)       # notebook
    )
    """
    try:
        from plotnine import theme, element_text, element_line, element_rect, element_blank
    except ImportError:
        raise ImportError("plotnine is not installed. Install with: pip install plotnine")

    font_family = ', '.join(_SANS_NARROW)

    return theme(
        # Background
        plot_background=element_rect(fill=NYT.BG, color=NYT.BG),
        panel_background=element_rect(fill=NYT.BG),

        # Panel grid: horizontal only, very light
        panel_grid_major_y=element_line(color=NYT.RULE, size=0.6),
        panel_grid_minor_y=element_blank(),
        panel_grid_major_x=element_blank(),
        panel_grid_minor_x=element_blank(),

        # Panel border: only bottom line
        panel_border=element_blank(),
        axis_line_x=element_line(color=NYT.RULE, size=1.0),
        axis_line_y=element_blank(),

        # Ticks: none
        axis_ticks=element_blank(),
        axis_ticks_length=0,

        # Axis text
        axis_text=element_text(
            family=font_family, size=base_size - 2, color=NYT.MID,
        ),
        axis_text_x=element_text(margin={'t': 8}),
        axis_text_y=element_text(margin={'r': 6}),

        # Axis titles
        axis_title=element_text(
            family=font_family, size=base_size - 1, color=NYT.MID,
        ),
        axis_title_x=element_text(margin={'t': 10}),
        axis_title_y=element_text(margin={'r': 10}),

        # Plot title: bold, left-aligned, near-black
        plot_title=element_text(
            family=font_family,
            size=base_size + 4,
            weight='bold',
            color=NYT.INK,
            ha='left',
            margin={'b': 6},
        ),

        # Subtitle
        plot_subtitle=element_text(
            family=font_family,
            size=base_size,
            color=NYT.MID,
            ha='left',
            margin={'b': 10},
        ),

        # Caption (source line)
        plot_caption=element_text(
            family=font_family,
            size=base_size - 3,
            color=NYT.LIGHT,
            ha='left',
            margin={'t': 10},
        ),

        # Legend
        legend_background=element_rect(fill=NYT.BG, color=NYT.BG),
        legend_key=element_rect(fill=NYT.BG),
        legend_text=element_text(
            family=font_family, size=base_size - 2, color=NYT.DARK,
        ),
        legend_title=element_blank(),

        # Strip (facet labels)
        strip_background=element_rect(fill=NYT.BG),
        strip_text=element_text(
            family=font_family, size=base_size - 1,
            color=NYT.DARK, weight='bold',
        ),

        # Margins — slightly more breathing room for slides
        plot_margin=0.03,
    )


# ─── Convenience: apply all at once ──────────────────────────────────────────

def apply_nyt_all(base_size: int = 15, context: str = 'slide') -> None:
    """
    Apply NYT style to matplotlib and register Plotly template in one call.
    Call once at the top of a notebook.

    Parameters
    ----------
    base_size : int
        Base font size. Default 15 for slides; use 11 for notebooks.
    context   : 'slide' (default) or 'notebook'
        Controls Plotly template font sizes and margins.

    Usage
    -----
    apply_nyt_all()                         # slide context (default)
    apply_nyt_all(base_size=11, context='notebook')   # notebook context
    """
    apply_nyt_mpl(base_size)
    register_nyt_plotly(context)
    print(f"✓ NYT theme active (context={context}, base_size={base_size})")
    print(f"  matplotlib rcParams updated  |  Plotly template registered")
    print(f"  For plotnine: add + theme_nyt(base_size={base_size}) to any ggplot object")
    print(f"  Slide sizes : FIG_SLIDE={FIG_SLIDE}  FIG_HALF_SLIDE={FIG_HALF_SLIDE}  FIG_THIRD_SLIDE={FIG_THIRD_SLIDE}")
    print(f"  Note: these are figure content area sizes (header+body+footnote handled outside the figure)")


# ─── Quick reference ─────────────────────────────────────────────────────────

def nyt_color_swatch() -> None:
    """Display a quick color swatch of the NYT palette."""
    print("NYT Palette:")
    for name, hex_ in [
        ('BLUE (primary)',  NYT.BLUE),
        ('ORANGE',          NYT.ORANGE),
        ('GREEN',           NYT.GREEN),
        ('PURPLE',          NYT.PURPLE),
        ('TEAL',            NYT.TEAL),
        ('SAND',            NYT.SAND),
        ('INK (title)',     NYT.INK),
        ('MID (labels)',    NYT.MID),
        ('RULE (grid)',     NYT.RULE),
    ]:
        print(f"  {hex_}  {name}")
