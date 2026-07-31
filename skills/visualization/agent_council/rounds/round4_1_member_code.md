# Round 4 — member_code Independent Findings (T19–T23)

Lens: code & technical correctness (docstring/implementation match, correct library API usage,
claimed behavior verified). Files re-read in full this pass: `references/data-visualization.md`,
`references/publication-guidelines.md`, `references/color-palettes.md`, `assets/swd_style.py`,
`assets/color_palettes.py`, `references/causal-inference-charts.md`, plus the full
`debate_log.md` history (T1–T18, all resolved — nothing below duplicates a closed topic).
matplotlib 3.10.8 installed locally; `bar`/`barh` signatures and `yerr`/`xerr` behavior verified
directly against `help(Axes.bar)` / `help(Axes.barh)`, not assumed from memory.

---

## T19 — Docstrings promise uncertainty display that the code doesn't implement

**Verdict: CONFIRMED, exactly as described, for both functions. This is the clearest bug of the
five topics — a literal contract violation between docstring and body, same class as T15.**

`references/data-visualization.md`, `plot_ablation` (lines 81–110):
- Signature: `def plot_ablation(categories, methods_data, ylabel="Accuracy (%)", figsize=(6, 3)):`
  — no interval/error parameter anywhere.
- Docstring (line 85–86): *"For model comparison, pass replicate-level results or estimates plus
  intervals; display uncertainty and independent-replicate n."*
- Body (line 97–98): `bars = ax.bar(x + offset, scores, width * 0.9, label=method,
  color=OKABE_ITO_LIST[i % len(OKABE_ITO_LIST)])` — no `yerr`, no error bars drawn, `scores` is
  the only numeric input actually consumed. `n` is never displayed anywhere in the body either.

`references/data-visualization.md`, `plot_leaderboard` (lines 176–197):
- Signature: `def plot_leaderboard(models, scores, highlight_idx=-1, xlabel="Score",
  figsize=(4, 3)):` — same gap.
- Docstring (line 177): *"Use estimates with intervals; highlight only by a prespecified
  criterion."*
- Body (line 185): `bars = ax.barh(y_pos, scores, color=colors, height=0.6)` — no `xerr`.

Both docstrings tell the reader to *pass* something the signature has no slot for. A reader who
follows the docstring literally has nowhere to put the interval data; a reader who copies the
function as-is ships a bar chart with no uncertainty display while believing the docstring's
instruction was satisfied by supplying `scores`. This directly contradicts the "always show
appropriate uncertainty" rule stated in `publication-guidelines.md`'s Statistical Rigor section
and demonstrated correctly elsewhere in the same file's own Chart Type 1 ("Shaded Variability or
Uncertainty" — a real `fill_between` mean±1SD implementation with an accuracy caveat) and Chart
Type 9. This is a real hole in "message-delivery-breaking" content that survived multiple prune
passes because those passes checked color/palette correctness in these files, not
docstring/body parity.

### Verified matplotlib API for the fix

Confirmed via `help(matplotlib.axes.Axes.bar)` / `help(matplotlib.axes.Axes.barh)` on matplotlib
3.10.8 (both delegate to the same underlying error-bar logic, x/y-swapped):

- `Axes.bar(x, height, width=0.8, bottom=None, *, align='center', data=None, **kwargs)` accepts
  `xerr, yerr : float or array-like of shape(N,) or shape(2, N), optional` — *"If not None, add
  horizontal / vertical errorbars to the bar tips."* Shape `(N,)` = symmetric +/- per bar; shape
  `(2, N)` = separate lower/upper rows. Also accepts `ecolor` (default `'black'`), `capsize`
  (default `rcParams['errorbar.capsize']`, which is `0` — i.e. **no visible caps unless you pass
  `capsize` explicitly**), and `error_kw` (forwarded to `Axes.errorbar`).
- `Axes.barh(y, width, height=0.8, left=None, *, align='center', data=None, **kwargs)` — same
  `xerr, yerr`/`ecolor`/`capsize`/`error_kw` parameters. For a horizontal bar, the value axis is
  the bar *length* (x-direction), so `xerr` is the one that renders on the bar tip; passing
  `yerr` to `barh` is valid syntactically but draws bars in the wrong (categorical) direction and
  is not what you want here.

### Proposed minimal fix

`plot_ablation` — add an optional `errors_data=None` parameter mirroring `methods_data`'s shape
(`{method_name: list_of_errors}`), pass through as `yerr` with an explicit `capsize` so caps are
visible by default:

```python
def plot_ablation(categories, methods_data, errors_data=None, ylabel="Accuracy (%)", figsize=(6, 3)):
    """
    categories: list of benchmark names
    methods_data: dict of {method_name: list_of_scores}
    errors_data: optional dict of {method_name: list_of_errors}, same shape as methods_data.
                 Each entry is +/- interval half-width per category (or a (2, n_cats) array for
                 asymmetric CIs). Pass replicate-level results or estimates plus intervals;
                 always populate this when reporting model comparisons, and report n.
    """
    ...
    for i, (method, scores) in enumerate(methods_data.items()):
        offset = (i - n_methods / 2 + 0.5) * width
        yerr = errors_data.get(method) if errors_data else None
        bars = ax.bar(x + offset, scores, width * 0.9, yerr=yerr, capsize=3,
                      label=method, color=OKABE_ITO_LIST[i % len(OKABE_ITO_LIST)])
```

`plot_leaderboard` — add an optional `errors=None` parameter (list/array same length as `scores`,
or shape `(2, len(scores))` for asymmetric), pass through as `xerr`:

```python
def plot_leaderboard(models, scores, errors=None, highlight_idx=-1, xlabel="Score", figsize=(4, 3)):
    """Use estimates with intervals (pass via `errors`); highlight only by a prespecified criterion."""
    ...
    bars = ax.barh(y_pos, scores, xerr=errors, capsize=3, color=colors, height=0.6)
```

Secondary, non-blocking note for whoever implements this: `plot_leaderboard`'s value-label loop
(`ax.text(bar.get_width() + 0.3, ...)`) places the label a fixed 0.3 units past the bar tip; with
an error bar now rendered at the tip, that fixed offset may visually collide with the error cap
for wide intervals. Not a correctness bug (nothing crashes, nothing is factually wrong) — just
worth a one-line mention in the docstring or a `+ (errors[i] if errors is not None else 0) + 0.3`
adjustment if whoever fixes T19 wants to polish it in the same pass. I would not block T19's
resolution on this.

**Confidence: high.** Verified against installed matplotlib 3.10.8 docstrings directly, not
assumed. The docstring/body mismatch is unambiguous and mechanically checkable (grep for `yerr`/
`xerr` in either function body returns nothing).

---

## T20 — `publication-guidelines.md`'s diverging-safe colormap list is a stale partial subset

**Verdict: CONFIRMED as described. Not a code bug (no code asset backs this particular line —
`publication-guidelines.md` line 26 is prose-only, not a `DIVERGING_COLORMAPS_SAFE`-style Python
list), but it is the same drift pattern T11 fixed twice already (T11 itself, then again per the
Round 3 ruling's sync-comment addition), now recurring a third time in a file the T11 fix never
touched.**

Confirmed current state:
- `references/color-palettes.md` lines 142–149: 6-row table — `RdYlBu`, `RdBu`, `PuOr`, `BrBG`,
  `PRGn`, `PiYG` — carrying the T11 sync comment ("This table must stay in sync with
  `assets/color_palettes.py`'s `DIVERGING_COLORMAPS_SAFE`").
- `assets/color_palettes.py` lines 70–77: same 6 maps, same sync comment pointing back.
- `references/publication-guidelines.md` line 26: `**Diverging (negative to positive)**: RdBu,
  PuOr, BrBG (colorblind-safe)` — 3 of the 6, no pointer to the authoritative table, no sync
  comment.

From the code-correctness angle specifically: nothing here is *false* (all three named maps are
genuinely on the safe list), so this isn't a T2-style contradiction. It's an incomplete/stale
duplication with no drift guard, in a file that otherwise reads as authoritative guidance.

**Proposed fix (my preference, but this is primarily a standards/documentation-structure call —
flagging for that lens):** rather than adding the other three maps inline a third time (which
just relocates the drift risk instead of closing it — a future edit to the six-map table still
won't touch this line), replace the inline list with a pointer: `**Diverging (negative to
positive)**: see color-palettes.md's Colorblind-Safe Diverging Maps table for the full
verified list.` This matches the pattern this same file already uses for Accessibility
("pointer, deduplicated against design-principles.md" per the Round 2 ruling) and permanently
closes the third-location-drift risk instead of requiring a human to remember to update three
places in sync. If the standards lens prefers keeping an inline list for
scanability-without-a-click, the fallback is: list all six + add the same one-line sync comment
used in the other two files.

**Confidence: high** that the current state is a stale subset (mechanically verified: grep for
`RdBu\|PuOr\|BrBG\|PRGn\|PiYG` in the three files). **Medium** on which fix direction (pointer vs.
inline six) — deferring the final call to the standards/color lens since it's a documentation-
architecture judgment, not a correctness one.

---

## T21 — `swd_style.py`'s `SWD` class carries two unverified, redundant accent-color constants

**Verdict: CONFIRMED, and the investigation found a cleaner root cause than "two blues with
different hex values" — `ACCENT_BLUE` is dead code, not a live redundant constant.**

Grepped the current `assets/swd_style.py` (258 lines) for every use of `SWD.ACCENT_BLUE`: it
appears exactly once, in its own definition (line 26, `ACCENT_BLUE = '#1A77B5'   # blue — second
emphasis (use sparingly)`). No function body in the file — `declutter`, `apply_swd_palette`,
`annotate_insight`, `insight_title`, `label_bars`, `highlight_region`, `fmt_pct` — references it.
Cross-checking `agent_council/rounds/round1_member_color.md` (lines 25–26) confirms why:
`ACCENT_BLUE` was the accent color used by `waterfall_colors()`, one of the four banking-specific
helpers (`risk_colormap`, `psi_status`, `fmt_bps`, `waterfall_colors`) that T1's Round-1-cycle fix
deleted from this file. The constant itself was left behind when its only caller was cut — this
is orphaned dead code from a prior council fix, the same failure mode as T4's dead branches, not
a fresh design decision to have two blues.

`SWD.ACCENT` (`#E8664A`, coral) is different: it's very much alive — it's the actual default for
both `apply_swd_palette()` (line 119: `accent = accent_color or SWD.ACCENT`) and
`highlight_region()` (line 242: `c = color or SWD.ACCENT`), i.e. the color most call sites of the
"one accent, rest gray" pattern will actually render. Unlike `ACCENT_POSITIVE`/`ACCENT_NEGATIVE`,
which carry an explicit inline comment tying them to the Okabe-Ito verification ("This pair is
colorblind-safe"), `ACCENT` carries no such claim or citation anywhere in the file or in
`color-palettes.md`/`color_palettes.py`. Structurally this is lower-risk than a two-hue pair
(it's used alone against gray, so hue-discrimination-against-another-hue isn't the failure mode
red/green pairs have — luminance contrast against `GRAY_LIGHT`/background is what actually
matters for a single accent), but a reader can freely combine `SWD.ACCENT` with
`SWD.ACCENT_POSITIVE`/`SWD.ACCENT_NEGATIVE` in the same figure (nothing in the code prevents it),
at which point three hues are on one chart and only two are verified.

### Proposed fix

1. **Delete `ACCENT_BLUE`.** It's confirmed dead code post-T1, not a documented alternative
   awaiting a future caller. This is the unambiguous part of the fix — high confidence, no
   tradeoff. (If the council wants to keep a "second emphasis" slot for future use, the minimal
   correct move is still to cut it now and re-add it if/when a caller needs it, per this repo's
   own established practice of not leaving no-op/unused surface area — see the `T10`
   `simulate_deuteranopia` precedent in the Round 2 ruling: "either implement for real or delete,
   don't leave a no-op that looks functional.")
2. **For `ACCENT`, don't drop it (it's load-bearing default for two live functions) — either
   verify it or replace it, and document whichever is chosen.** Two options, roughly equal
   engineering cost:
   - (a) Get a real CVD-simulation/citation check on `#E8664A` and add the same style of inline
     comment the positive/negative pair has ("verified via colorspacious/coblis, safe as a
     standalone accent against gray").
   - (b) Replace it with an already-verified Okabe-Ito hue not otherwise used as a semantic
     signal in this file — `#E69F00` (orange) is a reasonable candidate since it's distinct from
     both `ACCENT_POSITIVE` (`#0072B2` blue) and `ACCENT_NEGATIVE` (`#D55E00` vermillion), so it
     can't be mistaken for either directional signal if a chart happens to combine "the one
     accent" with a positive/negative pair.
   I'd lean toward (b) since it's mechanically verifiable right now (the palette is already
   vetted elsewhere in this same skill) versus (a)'s open-ended verification work, but this is
   fundamentally a color-science call — **flagging for the color lens to make the final pick**,
   my job here is confirming the constant is genuinely unverified and identifying that a
   same-skill verified substitute already exists.

**Confidence: high** on the `ACCENT_BLUE` dead-code diagnosis (mechanically grepped, cross-
referenced against the T1 fix that orphaned it — this is a stronger/more specific finding than
the topic's framing of "two blues with different hex values," since one of the two isn't in play
at all). **Medium** on the `ACCENT` fix direction (real vs. substitute) — technical facts are
solid, the choice between (a)/(b) is a judgment call for the color lens.

---

## T22 — `color-palettes.md`'s CVD-subtype prevalence figures likely conflate deuteranopia with deuteranomaly

**Verdict: color-science topic, no code implications found — deferring to the color lens per the
task framing, with one narrow code-adjacent observation.**

I did not find any code in `assets/color_palettes.py` or `assets/swd_style.py` that consumes or
depends on the specific prevalence percentages in `references/color-palettes.md`'s "Types of
Color Vision Deficiency" section (lines 202–205) — they're presentational/citation text only, not
wired into any function logic, threshold, or conditional. So there's no code-correctness angle
in the sense of "code does the wrong thing because of this number."

One adjacent observation worth flagging to the color lens: `assets/color_palettes.py`'s
`simulate_cvd()` docstring (the T10 replacement function, lines 212–221 in
`references/color-palettes.md`'s copy) correctly uses the more precise "-anomaly" terminology
("`deuteranomaly` (green-weak, most common), `protanomaly` (red-weak), or `tritanomaly`
(blue-weak, rare)") right below the disputed "-opia" prevalence list in the same file — i.e. this
file's own code example is internally *more* correct on the anomaly/dichromacy distinction than
its own prose table three sections earlier. That's supporting evidence for the topic's premise
(the file's code is careful about this distinction; its prevalence table apparently isn't) but I
have not independently verified the "~5%/~1%" vs. "~5%/~2%" figures against a primary source —
that verification is the color lens's job per the task's lens assignment.

**Confidence: low** (deferring — this is out of my lens by design, flagging only what's
adjacent).

---

## T23 — `causal-inference-charts.md`'s presentation sequence promises an "IV first-stage" chart with no matching section

**Verdict: CONFIRMED. Structurally identical gap-pattern to T16 (`SKILL.md` promising a
paper/journal path with no landing section, resolved in Round 3 by adding the missing section).**

Confirmed by reading the file in full: it has exactly five `##`-level chart sections — `## 1.
Coefficient Plot`, `## 2. Parallel Trends Check`, `## 3. DiD Event Study`, `## 4. RDD Binned
Scatter`, `## 5. Propensity Score Overlap` — and the "Presentation Order for Causal Results"
section's step 3 (lines 168–172) names four identification-strategy → assumption-chart mappings:

```
DiD  → parallel trends chart (pre-treatment window)      -> matches ## 2
RDD  → binned scatter continuity + density test          -> matches ## 4
PSM  → propensity overlap chart                           -> matches ## 5
IV   → first-stage F-statistic + relevance test           -> no matching ## section
```

No section, subsection, or even a passing mention of "first-stage," "instrument," "IV," or
"F-statistic" exists anywhere else in the file (confirmed via full read, not just heading scan —
the "Common Causal Inference Chart Mistakes" table at the end also has no IV row, reinforcing
that IV genuinely has zero coverage, not just a missing heading for content that exists
elsewhere). This isn't a code-correctness bug in the T19 sense (no function signature/body to
check — this file is pure markdown prose, no `assets/*.py` backs it), but it is the same class of
"instructions/promises the content doesn't back up" issue T19 and T16 are, which is why I'm
flagging it as CONFIRMED rather than deferring it entirely.

**Proposed fix:** add a `## 6. IV First-Stage Diagnostic` section following the exact template
the other five sections use (Use when / Audience / Required inputs / Key design decisions),
covering the weak-instrument problem and a conventional F-statistic threshold callout (e.g. the
Staiger-Stock rule-of-thumb F > 10, or a pointer to Stock-Yogo critical values for more rigor) —
mirroring how each existing section pairs a diagnostic chart with the specific failure mode it
guards against (parallel trends → pre-trend divergence; RDD → manipulation at the cutoff;
overlap → extrapolation). I don't have a strong opinion on the exact visual encoding (bar vs.
table vs. annotated scalar) since that's a domain/statistics content design call outside my
code-correctness lens — flagging the content-design specifics for the standards lens, but the
gap itself and the fix location (`## 6`, before "Presentation Order" or after `## 5`) are
unambiguous.

**Confidence: high** that the gap exists exactly as described (mechanically verified via full-file
read and heading grep). **Low/deferred** on the specific chart-pattern content that should fill
it — that's a statistics-domain judgment for the standards lens, not a code-correctness one.

---

## Summary table

| Topic | Confirmed? | Code bug? | Fix confidence | Flag for other lens |
|---|---|---|---|---|
| T19 | Yes, both functions | Yes — docstring/body mismatch | High | — |
| T20 | Yes, stale 3/6 subset | No (prose only) | High (bug) / Medium (fix direction) | standards (doc structure) |
| T21 | Yes, refined root cause | Yes — dead code (`ACCENT_BLUE`) + unverified live default (`ACCENT`) | High (`ACCENT_BLUE`) / Medium (`ACCENT` fix) | color (verify/replace `#E8664A`) |
| T22 | N/A to this lens | No | — | color (prevalence figures) |
| T23 | Yes | No (prose only) | High (gap) / Low (content design) | standards (IV chart content) |
