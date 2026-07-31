# Round 1 — member_standards (Domain Best-Practice / Publication Standards / Cross-File Consistency)

Reviewed: `SKILL.md`, all files in `references/`, all files in `assets/` (including `.mplstyle`
files and the three `.py` helper modules). Web-verified claims against current Nature,
NeurIPS/ICML, ColorBrewer, and matplotlib documentation where noted.

---

## T1 — Dangling reference to deleted `banking-visualization` skill

**Verdict: Confirmed, and worse than the debate log states.**

**Evidence:**
- `SKILL.md` line 43 routes "Banking domain chart (KS, PSI, vintage, fraud monitoring)" to
  "see `banking-visualization` skill." Confirmed via `find`: `skills/banking-visualization/`
  does not exist on disk. `skills/banking-hypothesis-generation/` exists but is about
  hypothesis generation, not charting — it is not a valid redirect target.
- The skill does have partial banking/credit coverage that could absorb this content, but
  it is scattered and incomplete:
  - `references/model-evaluation-viz.md`'s "Audience Guide for Model Charts" table (line 177)
    lists a row **"KS Curve | — | common in credit | policy-specific | domain-specific"** —
    but the file has zero `## KS Curve` section. Sections 1–7 cover ROC, PR, Calibration,
    Confusion Matrix, Feature Importance, SHAP Waterfall, Lift/Gain only. The table promises
    content that was never written.
  - `references/audience-adaptation.md` repeatedly uses "KS curve," "PSI," and "PSI bar" as
    if they are defined chart types elsewhere in the skill (lines 22, 27, 28, 46-52) — they
    are not defined anywhere except as color-mapping/threshold helpers in `swd_style.py`
    (`psi_status`), which returns a status label/color, not a chart-building recipe.
  - No file in the skill ever shows how to actually plot a KS curve, a PSI bar/trend chart,
    or a vintage curve — the exact three chart types `SKILL.md` promises the (now-deleted)
    banking skill would cover.
- `assets/swd_style.py` still ships four banking-domain helpers (`risk_colormap`, `psi_status`,
  `fmt_bps`, `waterfall_colors`) inside what SKILL.md describes as the general-purpose SWD
  helper module (line 77: "operationalizes steps 3–6"). These are true domain-specific
  business-logic helpers (hardcoded PSI thresholds 0.10/0.25, basis-point formatting),
  not generic charting utilities — they don't belong beside `declutter()`/`annotate_insight()`
  in a domain-agnostic file, and their docstring (lines 8, 12) is the *only* place in the
  repo that still calls them "Domain helpers" without saying which domain, since the domain
  skill they served is gone.

**Proposed fix:**
1. Remove the "Banking domain chart → see `banking-visualization` skill" line from the
   decision tree entirely, or replace it with a real, actionable pointer: route KS/PSI/vintage
   to `references/model-evaluation-viz.md` **and actually write the missing KS Curve section
   there**, plus add a PSI trend/bar chart pattern (the SWD framework + `psi_status()` already
   exist; only the chart-construction code is missing).
2. Either (a) delete `risk_colormap`, `psi_status`, `fmt_bps`, `waterfall_colors` from
   `swd_style.py` since their target skill is gone and nothing in `visualization` currently
   documents how to use them, or (b) keep them but move them to a clearly-labeled section and
   add the missing "how to plot a KS/PSI/vintage chart with these helpers" example so they are
   reachable and not orphaned dead code. Do not leave them as documented-but-unused surface area.
3. Fix the `model-evaluation-viz.md` audience table to either add the missing KS Curve section
   or remove the table row that promises it.

---

## T2 — Wong vs. Okabe-Ito duplication; self-contradictory "safe" diverging list

**Verdict: Confirmed (duplication claim), partially valid (diverging-safety claim).**

**Evidence — Wong/Okabe-Ito:**
- `references/color-palettes.md` presents "Okabe-Ito Palette (Recommended for Categories)"
  (line 9) and "Wong Palette (Alternative for Categories)" (line 55) as two options. The hex
  values are identical (`#E69F00, #56B4E9, #009E73, #F0E442, #0072B2, #D55E00, #CC79A7`) plus
  black, just reordered with black moved from last to first.
- Web-verified: Wong's 2011 *Nature Methods* "Points of View: Color Blindness" column
  republished a 7-color subset of the Okabe & Ito Color Universal Design palette (omitting
  black), popularizing it for a broader audience — it is not an independently designed
  alternative. Presenting it as a second choice ("Alternative for Categories") implies a
  meaningfully different option when it is the same 7-8 colors under a different name/citation.
- This duplication is repeated in `assets/color_palettes.py` (`OKABE_ITO_LIST` vs. `WONG`,
  identical colors, black moved to front) and `assets/style_presets.py` (`OKABE_ITO_COLORS`
  vs. `WONG_COLORS`, same pattern), and both expose `palette_name='wong'` as if it were a
  distinct 8th choice in `set_color_palette()`/`apply_palette()`.

**Evidence — diverging "safe" list self-contradiction:**
- `assets/color_palettes.py` line 62-69: `DIVERGING_COLORMAPS_SAFE` includes `PRGn` and
  `PiYG` with inline comments `# use with caution` inside a list literally named `_SAFE`.
  This is a genuine self-contradiction regardless of whether the underlying safety claim
  is correct — a variable named "safe" should not contain caveated entries silently.
- Web-verified against ColorBrewer's colorblind-safe designations (independently corroborated
  by two search passes): **BrBG, PiYG, PRGn, PuOr, RdBu** are ColorBrewer-certified
  colorblind-safe diverging schemes; **RdGy, RdYlGn, Spectral** are not. So PRGn/PiYG's
  underlying inclusion in the safe list is *actually correct per ColorBrewer* — the "use with
  caution" annotation appears to be an unjustified, overly conservative gloss (likely
  pattern-matching on "contains green"), not a documented finding. This makes the file
  internally contradictory without evidence backing the caution.
- **RdYlBu** status: web searches returned conflicting secondary-source summaries (one calling
  it ColorBrewer-safe, another calling it one of the "not safe" three). I could not get a
  clean authoritative read from colorbrewer2.org itself (JS-rendered, filter state not
  visible via fetch). Flag as **unresolved — verify directly against colorbrewer2.org's
  "colorblind safe" filter** before asserting either way; do not let the skill state it as
  fact without that check. `color-palettes.md` line 135-138 currently asserts it works with
  no caveat at all, which is the risky direction if the true answer is "not safe."

**Proposed fix:**
1. Merge the Wong section into Okabe-Ito as "also cited as the Wong palette (Nature Methods,
   2011) — same 7 colors, black added by Okabe & Ito's original 2008 set." Stop presenting
   `wong` as an independent selectable option with a different set of colors; if kept as a
   named option for citation-matching convenience, document explicitly that it is identical.
2. Remove the "(use with caution)" qualifier from `PRGn`/`PiYG` in `DIVERGING_COLORMAPS_SAFE`
   (they are ColorBrewer-certified) or move them to a separate list with the actual reasoning
   documented — don't leave a self-labeled "safe" list with unexplained caution flags.
3. Verify RdYlBu's actual ColorBrewer colorblind-safe status directly and correct
   `color-palettes.md` accordingly; until verified, add a hedge or swap the example for an
   uncontested one (RdBu, PuOr, BrBG).

---

## T3 — "Ocean Dusk" default palette vs. the skill's colorblind-safety rule

**Verdict: Confirmed.**

**Evidence:**
- `references/data-visualization.md` lines 49-68: "Ocean Dusk" is explicitly labeled
  "(default — professional, distinctive)" and mixes five ad hoc hex values (`teal`, `cyan`,
  `gold`, `orange`, `coral`) with two colors borrowed from Okabe-Ito (`blue`, `sky`) and one
  gray. Only two of eight "Ocean Dusk" colors are from a validated CVD-safe palette; the rest
  (especially `gold #E9C46A` vs `orange #F4A261` vs `coral #E76F51`) are close in hue/luminance
  and have no CVD-simulation backing in the file or elsewhere in the skill.
- This directly contradicts the skill's own stated universal rule. `SKILL.md` line 112
  ("colorblind-safe categorical colors" — stated as a requirement even for lightweight EDA),
  `references/style-guide.md` line 9 ("Colorblind-safe palettes — Never rely on color alone"),
  `references/publication-guidelines.md` line 62 ("Colorblind-friendly" as principle #1 of
  color selection), and `references/color-palettes.md` throughout all treat colorblind-safety
  as non-negotiable for any categorical palette, with no carve-out for "distinctive/professional
  aesthetic first, safety second."
  - Nature/Science/Cell/PLOS/IEEE all explicitly require sans-serif but none endorse
    "aesthetically distinctive but unvalidated" categorical palettes as an acceptable default —
    accessibility is treated as a submission requirement, not a nice-to-have, in real journal
    guidelines (confirmed via `journal-requirements.md`'s own compiled table).
- The file's own framing undercuts itself: it separately offers `OKABE_ITO` as "(maximum
  colorblind safety)" (line 70), which by contrast implies Ocean Dusk is *not* maximally safe
  — an explicit admission buried in a comment, not surfaced as a warning to the reader before
  the default is used.

**Proposed fix:** Either (a) demote "Ocean Dusk" from "default" to "optional accent variant,
verify with a CVD simulator before use," with Okabe-Ito as the actual default in this file
(matching every other reference file), or (b) replace the two visually-similar warm hues
(gold/orange/coral) with values validated against a simulator and cite the source. Do not
ship an unvalidated palette labeled "default" in a skill whose universal rule is
colorblind-safety-always.

---

## T4 — Dead code in `style_presets.py::apply_publication_style()`

**Verdict: Confirmed, and the dead branches are not merely redundant — they silently diverge.**

**Evidence:**
- Lines 151-156: early return for `style_name in ('nature', 'presentation')` loads the
  `.mplstyle` file and returns.
- Lines 161-170 (`nature`) and 200-212 (`presentation`) are unreachable for those two names
  because of the early return, confirmed by direct trace.
- Diffing the unreachable "nature" branch against the file it can never reach because of the
  early return (`assets/nature.mplstyle`):
  - `nature.mplstyle` sets `figure.figsize: 3.5, 2.625` (Nature's 89mm single-column sizing);
    the dead `get_base_style()`-based branch never sets `figure.figsize` at all, so if this
    branch were ever reached (e.g., after someone "fixes" the bug by deleting the early
    return) it would silently produce a *default* (6.4×4.8in) figure — not Nature's required
    column width. This is not just redundant code, it's a real behavior regression waiting to
    happen for the next person who "cleans up" the early return.
  - `axes.prop_cycle` also differs: dead branch inherits `OKABE_ITO_COLORS` (8 colors including
    black) from `get_base_style()`; `nature.mplstyle`'s cycler explicitly excludes black
    (7 colors, line: `cycler('color', ['E69F00', ... 'CC79A7'])`, no `'000000'`).
  - Tick sizes differ too: `xtick.major.size` 3/2 (dead branch, via `get_base_style()`) vs.
    2.5/1.5 (`nature.mplstyle`).
- Same pattern for `presentation`: `presentation.mplstyle` figure size (13.333×7.5) is a bundled
  fact; the dead branch under `elif style_name == 'presentation':` (line 200) *does* set
  `figure.figsize` matching it, so that one branch happens to reconverge on figsize but still
  diverges elsewhere (tick widths, marker sizes are consistent by luck here, worth re-checking
  if either file changes independently in the future since nothing enforces they stay in sync).

**Proposed fix:** Delete the dead `if style_name == 'nature': ...` / `elif style_name ==
'presentation': ...` blocks entirely (lines ~161-170 and ~200-212) since they can never
execute. If a non-.mplstyle-file code path is still wanted for these styles, it must be
reconciled field-by-field with the shipped `.mplstyle` file or it should just call
`plt.style.use()` on the same file, single source of truth.

---

## T5 — Serif "Times New Roman" vs. sans-serif default (typography)

**Verdict: Partially valid — the underlying dual convention is real and correctly captured in
one file, but `SKILL.md` never surfaces the distinction, so an agent following the decision
tree has no way to pick correctly.**

**Evidence:**
- Web-verified: NeurIPS's official LaTeX template specifies Times as the body font, and
  community tooling (e.g. `tueplots.fonts.neurips2021()`) matches figures to
  `font.family: serif`, `font.serif: ['Times New Roman']` for exactly this reason — figures
  should match the surrounding LaTeX body text. ICML/ICLR/ACL/AAAI templates are also
  Times-based. So `data-visualization.md`'s serif rcParams block (lines 15-44) is *not* wrong
  in isolation — it is correct for ML-conference camera-ready figures, and this is exactly
  what `references/style-guide.md` documents explicitly and correctly (lines 114-120: a table
  mapping NeurIPS/ICML/ICLR/ACL/AAAI to "Times" body font → serif figure font).
- Web-verified: Nature's author guidelines explicitly require sans-serif (Arial/Helvetica
  preferred, Helvetica preferred over Arial) — confirmed directly from Nature's own author
  guidance. `journal-requirements.md`, `publication-guidelines.md`, `matplotlib-examples.md`,
  and all four `.mplstyle` assets correctly encode this as sans-serif for the
  Nature/Science/Cell/PLOS/journal-submission use case.
- The actual bug is navigational, not factual: `SKILL.md`'s "Goal 2: Publication / ML Papers"
  section (lines 116-137) is a single undifferentiated goal covering both journal submissions
  and ML conference papers, and its "Get the details right" pointer (line 136) sends the
  reader to `publication-guidelines.md`, `journal-requirements.md`, `matplotlib-examples.md`
  only — all three of which are sans-serif. `data-visualization.md` (serif/Times, ML-conference
  convention) and `style-guide.md` (which correctly documents *when* serif is right) are never
  mentioned in that Goal 2 pointer at all; they only appear in the undifferentiated "Resources"
  list at the bottom of the file (lines 219-222) with no venue-type label. An agent asked to
  make a Nature figure or a NeurIPS figure gets routed to the same paragraph and the same code
  sample (`apply_publication_style` + `okabe_ito` + `configure_for_journal("nature", ...)`),
  none of which even branches on "is this a life-science journal or an ML conference?"
- `data-visualization.md` itself calls its serif block "Publication defaults" (line 14 comment)
  with no venue qualifier — read in isolation (which is how an agent following SKILL.md's
  Resources list would encounter it) it reads as a universal default, not an ML-conference-only
  one, which is where the contradiction with the rest of the skill actually originates.

**Proposed fix:**
1. Split `SKILL.md`'s "Goal 2: Publication / ML Papers" into two explicit sub-paths — "Life
   science / general journal (Nature, Science, Cell, PLOS, IEEE)" → sans-serif →
   `publication-guidelines.md` + `journal-requirements.md` + `matplotlib-examples.md`, vs.
   "ML conference paper (NeurIPS/ICML/ICLR/ACL/AAAI)" → serif/Times matching the LaTeX
   template → `data-visualization.md` + `style-guide.md`.
2. Retitle `data-visualization.md`'s rcParams comment from "Publication defaults" to
   "ML-conference publication defaults (Times-matching)" to prevent it from being read as a
   universal default.

---

## T6 — DPI on vector PDF savefig; inconsistent Nature line-art DPI figures

**Verdict: Confirmed on both counts.**

**Evidence — conceptual DPI/vector error:**
- Web-verified against matplotlib's own documented behavior: `dpi` in `savefig()` for a vector
  format (PDF/EPS/SVG) only controls the resolution of any *rasterized* sub-elements embedded
  in the file (e.g., an `imshow` raster layer); it has no effect on vector paths or text, which
  remain infinitely scalable regardless of the dpi value.
- `references/matplotlib-examples.md` Example 10 (lines 564-565):
  `fig.savefig('nature_figure.pdf', dpi=1000, ...)` is presented as satisfying Nature's "Line
  art: 1000-1200 DPI" requirement (as compiled in `journal-requirements.md` line 16). For a
  figure made entirely of vector line/scatter/bar elements (which Example 10 is — no `imshow`
  raster panel is actually rasterized-and-saved at this dpi in a way that matters), setting
  `dpi=1000` on the PDF save is functionally a no-op for satisfying that requirement; the
  actual resolution of vector line art in a PDF is unbounded/dpi-independent. This teaches a
  conceptual misunderstanding that will not actually break anything in practice (the PDF will
  still look sharp) but misinforms the reader about *why* it looks sharp and would fail them
  the moment they need to explain/troubleshoot a mixed vector+raster panel (e.g. Example 10's
  own Panel c heatmap via `imshow`, which the same dpi=1000 call rasterizes, though 1000 there
  is arguably reasonable for a raster panel).
- Note Example 10 also independently violates Nature's file-format guidance: `png` is not
  disallowed by Nature the way JPEG is, but the file also saves a `.png` at `dpi=300` (line
  566-567) as a second output with no clear purpose stated (Nature wants PDF/EPS/AI, not PNG,
  for graphs) — this is a smaller inconsistency worth flagging alongside the dpi issue.

**Evidence — numeric inconsistency across three files:**
| File | Nature line-art DPI figure |
|---|---|
| `journal-requirements.md` line 16 | 1000-1200 DPI |
| `publication-guidelines.md` line 16 | 600-1200 DPI ("Line art and graphs," not Nature-specific, but presented as the general publication rule an agent would apply) |
| `assets/nature.mplstyle` line ~46 | `savefig.dpi: 600` with inline comment `# 1000 for line art, 600 for combination` — the comment documents the correct Nature-specific split but the actual `savefig.dpi` value shipped is unconditionally 600, i.e., the file's own comment describes behavior it does not implement. Since matplotlib's `.mplstyle` format has no way to conditionally set dpi by content type, this is an inherent limitation of shipping a single flat dpi in an `.mplstyle` file for a journal with panel-type-dependent dpi requirements — but the comment should say so, not imply the split is handled.

**Proposed fix:**
1. In `matplotlib-examples.md` Example 10, replace the misleading framing: state that PDF/vector
   output is resolution-independent for line art regardless of the `dpi` argument, and that
   `dpi` there only matters for any rasterized panel (call out Panel c's `imshow` specifically
   as the thing dpi actually affects). Keep `dpi=1000` only if a raster panel is present and
   needs it; document that this is not "satisfying the 1000 DPI line art rule" so much as
   controlling raster panel quality.
2. Reconcile the three DPI figures: cite Nature's actual current author-guidelines number in
   `journal-requirements.md` and make `publication-guidelines.md`'s generic figure explicitly
   say "varies by journal, see `journal-requirements.md` for exact figures" instead of giving a
   second, different number.
3. Fix `nature.mplstyle`'s comment to read "savefig.dpi is a flat 600 here because .mplstyle
   cannot conditionally set dpi per panel type; for line-art-only figures increase to 1000-1200
   at save time" instead of implying the split is already implemented.

---

## Additional gaps found (not in original T1-T6 list)

### T7 (new) — Skill promises KS/PSI/vintage banking chart guidance in three separate places, delivers none

Already substantially covered under T1's evidence, but worth calling out as its own item
because it spans more than the dangling-link issue: this is a **content gap**, not just a
broken pointer.

- `SKILL.md` line 43 promises banking chart coverage (now nowhere).
- `references/model-evaluation-viz.md` line 177 promises a KS Curve chart type in its own
  table (not delivered in the same file).
- `references/audience-adaptation.md` repeatedly uses "KS curve" and "PSI bar" as named,
  presumed-known chart types across its worked example (lines 22, 27-28, 46-52) with no
  forward reference to where a reader would learn to build one.
- `assets/swd_style.py`'s `psi_status()` gives a status/color/label for a PSI value but is not
  a charting function — there is no `plot_psi_trend()` or equivalent anywhere in `assets/`.

**Proposed fix:** Add a "KS Curve" and "PSI Stability Chart" section to
`model-evaluation-viz.md` (parallel to its existing ROC/Calibration sections — required
inputs, key design decisions, audience) so that every chart type referenced by name elsewhere
in the skill actually has a home. This closes T1's redirect problem and T7's content gap in
one change.

### T8 (new) — `configure_for_journal()` in `style_presets.py` silently uses `apply_publication_style('default')`-equivalent styling for `plos`, `acs`, `ieee`

`assets/style_presets.py` lines 295-309: the `journal_configs` dict maps `'plos'`, `'acs'`,
and `'ieee'` all to `'style': 'default'` — i.e., calling `configure_for_journal('ieee', ...)`
applies the exact same rcParams as `configure_for_journal('plos', ...)` and the generic
default style, only varying figure width. But `journal-requirements.md` documents materially
different requirements for these three (e.g., IEEE: sans-serif preferred, 8-10pt min, 600 DPI
line art vs. PLOS: sans-serif preferred, 8-12pt, 600 DPI preferred but 300 minimum; ACS: no
font family stated but different DPI floor 300/600/1200 tiers, and ACS is the one journal here
where CMYK is explicitly conditional). None of these journal-specific distinctions are
represented in code — `configure_for_journal` implies per-journal correctness ("Configure
matplotlib for a specific journal") but three of its six supported journals get identical
non-journal-specific treatment. This isn't necessarily wrong (a shared sane default may be
fine), but the docstring/print message ("✓ Configured for {journal.upper()}") overstates what
actually happened. **Fix:** either implement journal-specific style dicts for plos/acs/ieee
matching `journal-requirements.md`, or soften the docstring/print statement to make clear that
only figure width is journal-specific for these three and rcParams remain generic.

### T9 (new) — `matplotlib-examples.md`'s own claim of colorblind-safe throughout is not fully true

The file's overview (line 5) claims "All examples ... use colorblind-friendly palettes from
`color-palettes.md`." Example 6 (Scientific Scatter with Regression, line 329) uses
`ax.plot(x_line, y_line, 'r-', ...)` — matplotlib's default `'r'` (pure red) for the regression
line against a `'#0072B2'` (Okabe-Ito blue) scatter. Pure red vs. blue is fine for most CVD
types, but the file's own "Common Mistakes" guidance elsewhere in the skill
(`color-palettes.md` line 216: "Don't: Use red/green combinations") and the broader rule of
sourcing every color from a named safe palette is broken here — `'r-'` is a matplotlib default
shorthand, not a value pulled from Okabe-Ito/Tol, contradicting the file's own overview claim
that *all* examples use the referenced palette.

---

## Summary Table

| Topic | Verdict | Severity |
|---|---|---|
| T1 | Confirmed, worse than stated (content gap, not just dead link) | High |
| T2 | Confirmed (Wong/Okabe-Ito duplication); partially valid (diverging list — PRGn/PiYG caution is unjustified per ColorBrewer; RdYlBu status unresolved) | Medium |
| T3 | Confirmed | Medium-High |
| T4 | Confirmed, with real regression risk if "fixed" naively | Medium |
| T5 | Partially valid — real convention exists but SKILL.md doesn't route to it | Medium |
| T6 | Confirmed on both DPI/vector conceptual error and cross-file numeric inconsistency | Medium |
| T7 (new) | Confirmed — content gap underlying T1 | High |
| T8 (new) | Confirmed — misleading function behavior/docstring | Low-Medium |
| T9 (new) | Confirmed — overview claim contradicted by own example | Low |
