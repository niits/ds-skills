# Round 2 — member_code (Code & Technical Correctness lens)

Reviewed `agent_council/debate_log.md` in full, including the "## Scope Redirect —
Message-Delivery Focus" section and the chairman's flagged `swd_style.py` disagreement, against
my own Round-1 findings (T1–T7) and a fresh read of the actual files on disk (not taking the
chairman's classification on faith).

---

## 1. `assets/swd_style.py` — PRUNE vs DELETE, and the T7 fix

**Verdict: agree with PRUNE, not DELETE — with two corrections to the chairman's plan.**

I read all six functions the chairman proposes to keep line-by-line:

- `declutter` — pure spine/gridline/facecolor toggling on an `Axes`. No banking logic, no bugs.
- `apply_swd_palette` — builds a `[base]*n` or accent/base list from `highlight_indices`,
  validates indices are in range and raises `IndexError` on bad input. Generic, correct.
- `annotate_insight` — thin wrapper around `ax.annotate` with sane defaults. Generic, correct.
- `insight_title` — thin wrapper around `ax.set_title(loc='left', fontweight='bold')`. Generic.
- `label_bars` — direct-value-labeling for both `ax.bar`/`ax.barh` output. Uses
  `getattr(bars, 'orientation', None)` to auto-detect orientation — this is legitimate:
  `matplotlib.container.BarContainer` has carried an `orientation` attribute (set to
  `'vertical'`/`'horizontal'` by `ax.bar`/`ax.barh`) since mpl 3.7ish, so this isn't a guess, it's
  the documented mechanism. Falls back to a clear `ValueError` if unavailable/ambiguous. Correct.
- `highlight_region` — `axvspan` + optional label text. Generic, correct.

None of these six touch banking/credit concepts — confirms the chairman's characterization.
**I agree PRUNE is correct**: they are the only working code for "highlight-one/gray-out-rest,"
annotation, decluttering, and insight-titling, all explicitly in-scope per the redirect. Deleting
the whole file (as the coordinator's example list implied by lumping it with `style_presets.py`)
would delete the skill's only implementation of those kept concepts.

**Correction #1 — a 7th function is unaccounted for.** The chairman's keep-6/cut-4 split misses
`fmt_pct` (`fmt_pct(0.1234) → '12.3%'`, line 306-308). It is generic percentage formatting with
no banking dependency, yet the file's own module docstring (line 12) mislabels it as a "Domain
helper" alongside `risk_colormap`/`psi_status`/`fmt_bps`/`waterfall_colors`. It belongs in the
keep set on the same generic/reusable grounds as the other six — flag this for the chairman so it
isn't silently deleted by following the docstring's (wrong) categorization instead of the actual
code.

**Correction #2 — the module docstring itself needs editing, not just the function bodies.**
Lines 1-13 are a module docstring with a `from swd_style import ... risk_colormap, psi_status,
fmt_pct, fmt_bps` usage example and a "Domain helpers: risk_colormap, psi_status, fmt_pct,
fmt_bps, waterfall_colors" line. If the prune only deletes the four function bodies and leaves
this docstring untouched, the file's own top-of-file usage example imports names that no longer
exist — an orphan-breakage bug introduced by the prune itself. The docstring must be rewritten in
the same pass.

**T7 (red=negative/green=positive) — confirmed it lives inside kept code and must be fixed.**
`SWD.ACCENT_GREEN`/`SWD.ACCENT_RED` (lines 28-29) are part of the `SWD` class, which the
chairman's plan explicitly keeps ("the class stays too, since `apply_swd_palette`/`label_bars`/
etc. depend on it"). Their inline comments — `# green — positive outcome / goal achieved` and
`# red — negative / loss / critical` — are the exact prescriptive positive=green/negative=red
rule T7 flags as contradicting `pre-attentive-attributes.md`'s (kept) guidance and
`color-palettes.md`'s red/green-avoidance rule. I traced actual usage: `ACCENT_GREEN` is
referenced once, inside `psi_status` (line 299) — a function being **cut**. `ACCENT_RED` is
defined but never referenced anywhere in the file at all (dead even today, independent of the
prune). So cutting the four domain helpers removes the only *consumer* of `ACCENT_GREEN`, but the
misleading constant + comment pair itself survives on the class every downstream user can still
import (`from swd_style import SWD; SWD.ACCENT_GREEN`). **This confirms the chairman's mandatory-fix
note is correct and non-optional**: the comments must be corrected (or the constants
repurposed/removed) in the same pass as `pre-attentive-attributes.md`'s T7 fix, or the two
surviving files contradict each other immediately post-prune.

---

## 2. `style_presets.py` deletion — T4 moot, confirmed

`assets/style_presets.py` still exists on disk (13,581 bytes) with the same unreachable-branch
structure I documented in Round 1 (`apply_publication_style()` early-`return`s for
`style_name in ('nature', 'presentation')` before reaching the later dead
`if/elif style_name == 'nature'/'presentation'` dict-literal branches). Since the debate log's
Scope Redirect table classifies this entire file **DELETE** (explicitly named in the redirect as
"style-application plumbing," and the file's own KEEP/PRUNE entry says "Bugs mooted: T4 ...
moot, whole file deleted"), there is no surviving code path for T4 to apply to. **Confirmed
moot/resolved-by-deletion** — no fix needed, just delete the file as planned. (Side note: this
also removes `configure_for_journal`'s silently-generic plos/acs/ieee handling, member_standards'
T8, for the same reason — consistent with the debate log.)

---

## 3. Orphan-breakage introduced by the `data-visualization.md` / `matplotlib-examples.md` PRUNE plans

This is the one place I disagree with how far the chairman's plan goes unqualified — from a pure
code-correctness angle, **both PRUNE plans as currently scoped will leave the *kept* code examples
broken (NameError on copy-paste)**, not just trimmed of decoration. This needs to be called out
as required rewrite work, not implied by "replace any surviving example's color needs with a
pointer to `color-palettes.md`."

**`references/data-visualization.md`:** grep confirms `COLOR_LIST`/`COLORS[...]` (defined in the
cut "Ocean Dusk" section) and `FIG_ICML_SINGLE`/`FIG_ICML_FULL`/`FIG_NEURIPS_*` (defined in the
cut "Figure Sizes by Venue" table) are referenced throughout the kept chart-type functions:
- `plot_training_curves` (log-log/training-curve logic, keep-worthy): `FIG_ICML_SINGLE`, `COLOR_LIST[i]`
- "Shaded Variability" snippet (the uncertainty-band-with-caveat the chairman explicitly wants kept): `COLOR_LIST[0]` (×2)
- `plot_ablation`: `FIG_ICML_FULL`, `COLOR_LIST[i]`
- `plot_scatter` + "Scatter with regression line": `FIG_ICML_SINGLE`, `COLOR_LIST[0]`, `COLOR_LIST[1]`
- `plot_leaderboard` (the "sorted-and-highlighted leaderboard bars" chairman names explicitly): `FIG_ICML_SINGLE`, `COLORS["gray"]`, `COLORS["coral"]`
- `plot_distributions`: `FIG_ICML_SINGLE`, `COLOR_LIST[i]`
- `plot_stacked_bar` (the "stacked-horizontal-bar-over-pie rationale" chairman names explicitly): `FIG_ICML_FULL`, `COLOR_LIST`
- `plot_scaling` (the "log-log scaling-law framing" chairman names explicitly): `FIG_ICML_SINGLE`, `COLOR_LIST[0]`, `COLOR_LIST[1]`

That's every single one of the chairman's three explicitly-named "keep this" examples, broken.
Only `plot_heatmap`/"Diverging Heatmap", `plot_multi_panel`/"Subplot label convention" are clean
(inline figsize, no `COLOR_LIST`/`FIG_*` dependency) and survive the prune as-is. Fix: each kept
function needs its `FIG_ICML_*`/`FIG_NEURIPS_*` swapped for a literal figsize tuple or removed
entirely (let the caller pass `figsize`), and its `COLOR_LIST`/`COLORS[...]` swapped for a literal
Okabe-Ito reference (e.g. `from color_palettes import OKABE_ITO_LIST` or inline hex) — this is
edit work on every surviving function body, not just deletion of the two defining sections.

**`references/matplotlib-examples.md`:** grep confirms all four examples on the chairman's keep
list — Example 1 (line 110), Example 4 (line 257), Example 7 (line 387), Example 9 (line 493) —
call `save_publication_figure(fig, '...')`, which is defined only in the "Helper Function for
Saving" subsection the chairman's cut list explicitly names ("the entire 'Setup and Configuration'
rcParams block; `save_publication_figure` helper"). If that helper is deleted without touching the
four call sites, all four kept examples reference an undefined function. Fix: replace each
`save_publication_figure(fig, 'name')` call with the two-line `fig.savefig('name.pdf', ...)` /
`fig.savefig('name.png', dpi=300, ...)` pattern inline (same pattern the file already uses
correctly in Example 10, which is being cut wholesale anyway) — again, edit work on every kept
example, not just deletion of the helper's definition.

Net: the chairman's classification (what to keep/cut) is right; the mechanical claim that cutting
`COLOR_LIST`/`FIG_*`/`save_publication_figure` is a clean subtraction is not — it will break every
named "keep" example unless each is patched to be self-contained. Flagging as required work for
whoever executes the prune, not a reason to change the keep/cut classification itself.

---

## 4. `assets/color_palettes.py` — T2 fixes still needed post-prune

Re-read the file in full. It is unchanged from Round 1 and is classified **KEEP (minor prune)** —
neither bug is touched by any pruning:
- `WONG = ['#000000', '#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00',
  '#CC79A7']` (lines 32-33) is still a byte-identical reorder of `OKABE_ITO_LIST` (lines 28-29),
  exposed as a distinct option via `apply_palette('wong')`/`get_palette('wong')` — still
  misleading (picking "wong" changes nothing perceptually vs. "okabe_ito").
- `DIVERGING_COLORMAPS_SAFE` (lines 62-69) still contains `'PRGn', # (use with caution)` and
  `'PiYG', # (use with caution)` inside a list named `_SAFE` — still self-contradicting. (Per my
  Round-1 ColorBrewer verification, both are genuinely colorblind-safe per ColorBrewer's own
  classification, so the fix should be dropping the "(use with caution)" comment, not moving them
  to a different list — but that verification question is orthogonal to whether the fix is still
  needed, which it is.)

**Confirmed: T2 fixes are still required.** This file's KEEP status (it's the actual code for the
redirect's "choosing a safe categorical set" + sequential/diverging choice logic) makes fixing
these two issues more important post-redirect, not less — this is now one of a small number of
files an agent will actually import/run, so a duplicated-palette-under-a-false-name and a
self-contradicting safety label are live correctness bugs in surviving message-delivery code, not
dead weight that pruning removes.

---

## Summary

| # | Question | Answer |
|---|---|---|
| 1 | swd_style.py PRUNE vs DELETE | Agree PRUNE. Add `fmt_pct` to the keep set (mislabeled as domain helper). Module docstring's usage example/helper list must be edited alongside the function cuts. T7 (`ACCENT_GREEN`/`ACCENT_RED` positive/negative comments) is confirmed inside kept code (`SWD` class survives) and is a mandatory fix, not optional. |
| 2 | style_presets.py T4 | Confirmed moot — file still exists today with the same dead-branch bug, but is slated for full DELETE, which removes T4 (and member_standards T8) with no fix needed. |
| 3 | data-visualization.md / matplotlib-examples.md PRUNE orphan check | Real breakage found: every chairman-named "keep" example in both files references a name (`COLOR_LIST`/`COLORS`/`FIG_ICML_*`/`FIG_NEURIPS_*` in data-visualization.md; `save_publication_figure` in matplotlib-examples.md) defined only in a section slated for deletion. Requires per-example edits, not just deleting the defining sections. |
| 4 | color_palettes.py T2 | Confirmed still needed — file unchanged, KEEP status, both the Wong/Okabe-Ito duplication and the PRGn/PiYG "safe...use with caution" contradiction are live in surviving code. |
