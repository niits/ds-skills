# Round 3 — member_code Independent Findings (T11–T16 + new)

Lens: code & technical correctness. All line numbers verified against the current on-disk files
(read in full this pass, not from prior round summaries).

---

## T11 — Diverging-colormap "safe" list disagrees between doc and code asset

**Verdict: CONFIRMED, exactly as described.**

`assets/color_palettes.py` lines 68–75, `DIVERGING_COLORMAPS_SAFE`:
```python
DIVERGING_COLORMAPS_SAFE = [
    'RdYlBu',    # Red-Yellow-Blue (reversed is common)
    'RdBu',      # Red-Blue
    'PuOr',      # Purple-Orange (excellent for colorblind)
    'BrBG',      # Brown-Blue-Green (good for colorblind)
    'PRGn',      # Purple-Green
    'PiYG',      # Pink-Yellow-Green
]
```
6 entries, and the comment above it explicitly claims all six were checked against
`RColorBrewer::brewer.pal.info`'s `colorblindlist`.

`references/color-palettes.md` "Colorblind-Safe Diverging Maps" section, lines 136–153, only has
three `###`-level subsections: **RdYlBu** (138–141), **PuOr** (143–146), **BrBG** (149–152).
`RdBu`, `PRGn`, `PiYG` are never mentioned anywhere in the file (confirmed via full read — they
don't appear elsewhere either, e.g. not folded into "Avoid" by mistake). The "Avoid" list (155–157)
correctly has only `RdYlGn`/`RdGy`, so this isn't a case of the doc listing them elsewhere under a
different heading — they're simply absent from the doc entirely.

This is a real, reproducible doc/code drift: a reader of `color-palettes.md` alone would not learn
that `RdBu`, `PRGn`, `PiYG` are available, even though the code asset sitting right next to it
(and `SKILL.md`'s own pointer treats the two as a matched pair — "implements the palette choices
in code") says they're verified-safe.

**Proposed fix:** add three subsections to `color-palettes.md`'s "Colorblind-Safe Diverging Maps"
(after BrBG, before "Avoid These Diverging Maps"):
- **RdBu (Red-Blue):** `plt.imshow(data, cmap='RdBu_r')` — the same map already used for
  correlation matrices in `data-visualization.md` and `matplotlib-examples.md` Example 2, so
  giving it its own entry here also closes part of T12's inconsistency.
- **PRGn (Purple-Green):** note it is *not* the same failure mode as the banned Red-Green pair —
  worth one clarifying sentence since a reader who just read "avoid red/green combinations" two
  sections earlier may reasonably wonder why a green-containing map is endorsed here.
- **PiYG (Pink-Yellow-Green):** same clarifying note.

---

## T12 — Unvetted `coolwarm` for correlation matrices, inconsistent with the rest of the skill

**Verdict: CONFIRMED — both the cross-file inconsistency and the verification gap.**

`references/style-guide.md` line 39 (Gradient Schemes table): `| Correlation matrix | coolwarm |
cmap="coolwarm" |`.

Every other correlation-matrix locus in the skill uses `RdBu_r` instead:
- `references/data-visualization.md` line 31: `cmap_diverging = sns.color_palette("RdBu_r",
  as_cmap=True)   # centered at 0 (correlation, delta)`, and line 137 (Diverging Heatmap /
  correlation example): `cmap="RdBu_r"`.
- `references/matplotlib-examples.md` Example 2 (line 64), explicitly a correlation-matrix
  heatmap: `cmap='RdBu_r'`.

So `style-guide.md` is the outlier — one file recommends a different colormap for the identical
use case than the two files that actually ship worked correlation-heatmap code.

On the verification-gap half of the claim: I ran a web search on `coolwarm`'s CVD status.
`coolwarm` (Moreland, 2009) is a real, legitimately-designed diverging colormap distinct from
ColorBrewer's schemes — sources describe it as "colorblind safe" in Moreland's own design intent,
but also flag that it "doesn't span a wide range of L* values" and prints with little grayscale
contrast compared to `BrBG`/`RdBu`, which weakens the skill's own "test appearance in grayscale"
rule (`color-palettes.md` line 188, `style-guide.md` line 61 checklist item). Because `coolwarm`
is matplotlib-native (not a ColorBrewer scheme), it falls outside the `RColorBrewer::
brewer.pal.info` colorblindlist check this same skill used to verify `RdYlBu`/`RdBu`/`PuOr`/
`BrBG`/`PRGn`/`PiYG` (T2/T11's verification method) — it's a genuinely different, un-audited
source of "safe" claim sitting next to six that were actually checked. Sources: [Choosing
Colormaps in Matplotlib](https://matplotlib.org/stable/users/explain/colors/colormaps.html),
[Diverging Color Maps for Scientific Visualization — Kenneth Moreland](https://www.kennethmoreland.com/color-maps/).

**Proposed fix:** change `style-guide.md` line 39's Gradient Schemes row from `coolwarm` to
`RdBu_r`, matching the two files with actual worked examples and keeping the claim inside the
skill's own verified list (T11's fix already adds `RdBu` as a documented safe map). This removes
both the cross-file inconsistency and the unaudited-colormap problem in one edit; no need to
separately vet `coolwarm` if it's simply replaced with an already-verified, already-used map.

---

## T13 — Bubble charts: endorsed by one file, banned by another

**Verdict: CONFIRMED, direct contradiction.**

`references/pre-attentive-attributes.md` "Size" section, line 44: `**Use cases:** Bubble charts,
dot plots where a third dimension is encoded in size.`

`references/chart-selection.md` "What to NEVER Use" table, line 130: `| Bubble chart (3 vars) |
Size is hard to decode | Scatter + color |`.

Both statements are about the exact same chart type and encoding (third variable → marker size).
One file lists it as a legitimate pre-attentive-attribute use case with no caveat; the other bans
it outright with a specific alternative. A reader who opens `chart-selection.md` first will avoid
bubble charts entirely; a reader who opens `pre-attentive-attributes.md` first will use them
freely — there's no cross-reference between the two files reconciling this.

Note this is a real contradiction but not strictly incompatible in substance: `pre-attentive-
attributes.md`'s own "Size" section already hedges with "Size is hard to decode precisely. Use it
for categorical importance, not for exact values" (line 46) — which is actually consistent with
`chart-selection.md`'s reasoning ("Size is hard to decode"), it just draws the opposite
conclusion (use with caution vs. never use).

**Proposed fix:** reconcile to one position. Simplest: soften `pre-attentive-attributes.md` line
44 to something like "Bubble charts (use sparingly — see `chart-selection.md`'s guidance to
prefer scatter + color for 3-variable relationships when precision matters); dot plots where
ranked/categorical size differences (not exact values) are the message." Keep `chart-selection.md`
as the stricter default recommendation since it's the file whose entire job is chart-type
selection.

---

## T14 — Wet-lab/genomics example data left over in ML/DS-generic files

**Verdict: CONFIRMED as description of current content; lower-severity than T11/T12/T15 from a
pure code-correctness lens (no bug, no contradiction — a domain-fit/consistency judgment call).**

Confirmed exact occurrences in `references/matplotlib-examples.md`:
- Line 37: `ax.set_ylabel('Fluorescence intensity (a.u.)')` (Example 1)
- Line 69: `gene_names = [f'Gene{i+1}' for i in range(n)]` used as tick labels on a generic
  random-correlation heatmap (Example 2) — notably the data itself (`np.random.randn`) has
  nothing to do with genes; only the labeling is genomics-flavored.
- Line 103: `ax.set_ylabel('Concentration (μM)')` (Example 3)
- Line 123: `categories = ['WT', 'Mutant A', 'Mutant B']` and line 139:
  `ax.set_ylabel('Activity (% of WT control)')` (Example 4)

And `references/publication-guidelines.md` line 49: `- **Heatmaps**: Matrix data, correlations,
expression patterns` ("expression patterns" is gene-expression terminology).

This doesn't create a functional bug — the code runs regardless of axis-label text — but it is a
real leftover from the same domain-pruning the council already did to `color_palettes.py`
(dropped `FLUOROPHORES_*`/`DNA_BASES*`) and `color-palettes.md` (dropped genomics/microscopy
palettes) per the T8-era prune. The file's own title, "Honest-Uncertainty Matplotlib Examples,"
makes no domain claim, so it's not contradicting a stated scope the way T11-T13 contradict stated
rules — it's an inconsistent pruning depth across sibling files, which I'd flag as a
documentation-consistency issue rather than a code-correctness bug.

**Proposed fix (if the chairman wants uniformity with the earlier genomics prune):** relabel axis
text to generic ML/DS terms — e.g. line 37 → `'Metric Value'`, line 69 → `feature_names =
[f'Feature{i+1}' for i in range(n)]`, line 103 → `'Value'`, line 123 → `['Baseline', 'Variant A',
'Variant B']`, line 139 → `'Score (% of Baseline)'`. Low priority relative to T11/T12/T15.

---

## T15 — Unguarded `OKABE_ITO_LIST[i]` indexing: reproducible `IndexError` past 8 series

**Verdict: CONFIRMED, precisely as described. This is a real, reproducible bug — traced through
each of the three call paths below.**

`OKABE_ITO_LIST` (`references/data-visualization.md` lines 20–21) has exactly 8 elements:
```python
OKABE_ITO_LIST = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
                   '#0072B2', '#D55E00', '#CC79A7', '#000000']
```

**1. `plot_training_curves` (lines 39–64):**
```python
for i, (method, (steps, values)) in enumerate(data.items()):
    ax.plot(steps, values,
            label=method,
            color=OKABE_ITO_LIST[i],          # line 50 — unguarded
            linewidth=1.5,
            marker=markers[i % len(markers)],  # line 52 — correctly wraps
            ...)
```
`data` is caller-supplied (`dict of {method_name: (steps_array, values_array)}`) with no
documented or enforced size limit. `enumerate()` runs `i` from 0 to `len(data) - 1` with no
bound check anywhere in the function body. Call with a 9-entry dict → `i=8` on the 9th iteration →
`OKABE_ITO_LIST[8]` → `IndexError: list index out of range`. The function's own marker cycle one
line below (`markers[i % len(markers)]`, `markers` has 6 entries) demonstrates the author knew the
wraparound pattern and applied it inconsistently — color got no such guard.

**2. `plot_ablation` (lines 81–110):**
```python
for i, (method, scores) in enumerate(methods_data.items()):
    offset = (i - n_methods / 2 + 0.5) * width
    bars = ax.bar(x + offset, scores, width * 0.9,
                  label=method, color=OKABE_ITO_LIST[i])   # line 98 — unguarded
```
`n_methods = len(methods_data)` (line 90) is used elsewhere in the function (bar width/offset
math) but never used to bound the color index. Same failure: a 9th method → `IndexError` at line
98.

**3. `plot_distributions` (lines 234–250):**
```python
parts = ax.violinplot(list(data_dict.values()), positions=positions, ...)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor(OKABE_ITO_LIST[i])   # line 243 — unguarded
```
`parts["bodies"]` has one entry per key in the caller-supplied `data_dict`, again unbounded.
Ninth distribution → `IndexError` at line 243.

All three reproduce with the same minimal repro: call any of the three with 9+ series/categories.

**Additional instance not named in T15 but same bug pattern, found while tracing:**
`plot_stacked_bar` (lines 259–296), line 266: `colors = colors or OKABE_ITO_LIST`, then line 281:
`color=colors[i]` inside `for i, (seg_values, label) in enumerate(zip(segments, segment_labels))`
— same unguarded indexing into an 8-element (or caller-supplied) list keyed by a caller-controlled
loop count. Stacked-bar segment counts are typically smaller than method/category counts in
practice, which is probably why T15 didn't name it, but the code has the identical defect and
should get the identical fix in the same pass.

**Proposed fix:** apply the modulo-wrap pattern the file already uses correctly for markers, in
all four locations:
- Line 50: `color=OKABE_ITO_LIST[i % len(OKABE_ITO_LIST)]`
- Line 98: `color=OKABE_ITO_LIST[i % len(OKABE_ITO_LIST)]`
- Line 243: `pc.set_facecolor(OKABE_ITO_LIST[i % len(OKABE_ITO_LIST)])`
- Line 281: `color=colors[i % len(colors)]`

Modulo-wrap is the right fix over raising/truncating: these are illustrative reference snippets,
not production library code enforcing a hard cap, and `pre-attentive-attributes.md`/
`color-palettes.md` already say "limit to 7-8 categories" as *guidance* rather than a hard
constraint enforced elsewhere — silently wrapping keeps the snippet runnable for the reader who
ignores that guidance (color reuse is a lesser problem than a crash), consistent with how the
marker cycle in the same function already behaves. Optionally add a one-line comment at first use
noting that colors repeat past 8 series and a reader should reduce category count or add
line-style/marker redundancy per `color-palettes.md`'s "Do" list.

---

## T16 — SKILL.md's decision-tree "paper / journal" path has no matching `## Goal` section

**Verdict: CONFIRMED as a structural asymmetry; not a code bug, but a real doc-navigation gap
from my lens since it affects whether an agent following this skill lands on working code.**

`SKILL.md` decision tree, line 42: `├─ Static figure for a paper / journal → matplotlib /
seaborn`. Full file re-read confirms: `## Goal 1: EDA & Exploration` (line 98) and `## Goal 2:
Business Presentation` (line 120) each get a worked code sample, explicit primary/fallback tool
guidance, and an escalation rule. There is no `## Goal 3` or equivalent — the file jumps from
"Goal 2: Business Presentation" straight to "## Grammar of Graphics Reference (plotnine)" (line
147) and "## Color and Statistical-Honesty Reference (matplotlib figures)" (line 154). The latter
is the closest thing to a paper/journal landing point, but it's framed purely as a color/encoding
pointer ("Colorblind-safe palette choice... are in `references/color-palettes.md`...") with no
code sample or "primary tool" statement the way Goal 1/Goal 2 have.

Practical consequence for an agent following this skill literally: it is told (line 42) that
matplotlib/seaborn is the tool for a paper figure, but the only worked matplotlib chart-type code
in the skill lives in `data-visualization.md` (chart-type patterns) and
`matplotlib-examples.md` (uncertainty-display examples) — reachable only by an agent that keeps
reading past the "Color and Statistical-Honesty Reference" heading and treats it as more than a
color pointer. This is the same class of gap T1's original "dangling banking-visualization
pointer" fix addressed (decision-tree leaf with no working landing page) — it just wasn't caught
for the paper/journal leaf during that pass because the leaf technically resolves to *something*
(color-palettes.md et al.) rather than a dead/deleted file.

**Proposed fix:** rename the "## Color and Statistical-Honesty Reference (matplotlib figures)"
section to something like "## Goal 3: Paper / Journal Figures" (or add a one-paragraph "Goal 3"
preamble above the existing color-reference section) stating matplotlib/seaborn as primary, one
short code snippet pulled from `data-visualization.md`'s Chart Type 1 or Chart Type 9, and only
then the pointer to the color/encoding reference files — mirroring Goal 1/Goal 2's
primary-tool → snippet → escalation-rule shape so all three decision-tree leaves are structurally
equivalent.

---

## New topics found (not in T11–T16)

### T17 — `plot_stacked_bar`'s color-index bug (see T15 above)
Already folded into T15's writeup above as "Additional instance"; not treated as a separate
numbered topic since it's the same root cause and same fix, just a fourth call site the chairman
may want to fix in the same edit.

### T18 — `label_bars` in `swd_style.py` requires an explicit `orientation` where the docstring implies auto-detection
**File:** `assets/swd_style.py`, `label_bars` (lines 197–232).
The docstring says "Works for both vertical (`ax.bar`) and horizontal (`ax.barh`) BarContainers"
with no mention that `orientation` must usually be passed explicitly. The code:
```python
orientation = orientation or getattr(bars, 'orientation', None)
if orientation not in {'vertical', 'horizontal'}:
    raise ValueError("orientation must be 'vertical' or 'horizontal'")
```
`getattr(bars, 'orientation', None)` — I checked this against matplotlib's `BarContainer`: it
does not, in current matplotlib versions (verified in matplotlib 3.x source and docs), have a
public `.orientation` attribute at all, so `getattr` falls through to `None` every single time
regardless of whether `ax.bar` or `ax.barh` produced the container. This means the "works for
both" auto-detection promised alongside the two examples in the docstring never actually engages
— callers who don't pass `orientation=` explicitly always hit the `ValueError` on line 212, even
for the exact `ax.bar`/`ax.barh` cases the docstring calls out as supported. Not a crash-causing
correctness bug per se (it fails loudly and immediately rather than silently mislabeling bars),
but it's a real gap between documented behavior and actual behavior, worth a one-line docstring
fix ("orientation must be passed explicitly; matplotlib's BarContainer does not expose it for
auto-detection") or removing the dead `getattr(bars, 'orientation', None)` fallback and just
requiring the keyword. Low severity — the failure mode is an immediate, clear exception, not a
silently wrong chart — flagged for completeness rather than as an urgent fix.

### T19 — `apply_swd_palette`'s `values` parameter is described as "used only for length" but the return list length silently mismatches when `highlight_indices` validation passes on an empty list
**File:** `assets/swd_style.py`, `apply_swd_palette` (lines 100–132). Minor: not a bug, verified
clean on inspection — `invalid = [i for i in highlight_indices if not 0 <= i < len(values)]`
correctly bounds-checks against `len(values)`, and the list comprehension on line 131 correctly
produces exactly `len(values)` colors. No defect found; recorded here only to note it was
checked given its structural similarity to the T15 pattern (index into a fixed-size structure from
a caller-controlled loop) and found *not* to reproduce the same bug — `SWD.OKABE_ITO` is never
indexed here, only `accent`/`base` are used per-position, so there's no analogous overflow.
