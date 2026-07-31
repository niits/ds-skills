# Visualization Skill Review Council — Debate Log

## Council Charter

- **Date:** 2026-07-30
- **Skill under review:** `skills/visualization/` (SKILL.md + `references/*.md` + `assets/*.mplstyle`, `assets/*.py`)
- **Process:** Fresh subagent-based debate (the prior `agent_council/review_council.py` script used for `skills/metrics-evaluation/` has been deleted from disk and is not used here). Chairman selects debate topics; independent council members investigate all topics from their own angle in Round 1; council members cross-critique each other's findings in Round 2; Chairman issues final rulings and directs fixes.
- **Scope note:** `skills/banking-visualization/` and `skills/plotnine-visualization/` no longer exist on disk (deleted in the working tree per `git status`) — findings that reference them are about **dangling references from `skills/visualization/`**, not about reviewing their (absent) content.

---

## Debate Topics

### T1 — Dangling reference to the deleted `banking-visualization` skill, and orphaned banking-specific helpers in `swd_style.py`
**Files:** `SKILL.md` (Library Decision Tree, line ~43), `assets/swd_style.py` (`risk_colormap`, `psi_status`, `fmt_bps`, `waterfall_colors`)
**Why in question:** `SKILL.md`'s decision tree still routes "Banking domain chart (KS, PSI, vintage, fraud monitoring)" to "see `banking-visualization` skill," but `skills/banking-visualization/` has been deleted from the repository (confirmed: directory does not exist on disk). Meanwhile `assets/swd_style.py` — part of the general-purpose `visualization` skill — still carries banking/credit-risk-specific domain helpers (`risk_colormap`, `psi_status` with hardcoded PSI thresholds, `fmt_bps`, `waterfall_colors`). Debate whether the dangling reference should be removed/redirected and whether the domain-specific helpers belong in a general visualization skill at all now that the banking skill is gone.

### T2 — Colorblind-safe palette claims that don't hold up: Wong vs. Okabe-Ito duplication, and self-contradictory "safe" diverging maps
**Files:** `references/color-palettes.md` (Okabe-Ito vs. Wong sections), `assets/style_presets.py` (`WONG_COLORS`), `assets/color_palettes.py` (`WONG`, `DIVERGING_COLORMAPS_SAFE`)
**Why in question:** The "Wong Palette (Alternative for Categories)" is presented as a distinct choice from Okabe-Ito, but the eight hex values are identical to Okabe-Ito (only reordered) — Wong's 2011 Nature Methods column popularized Okabe & Ito's own 2008 palette, so offering it as an "alternative" is misleading/redundant, not a second option. Separately, `color_palettes.py` lists `PRGn` and `PiYG` inside `DIVERGING_COLORMAPS_SAFE` while annotating them "(use with caution)" in the same line — a self-contradicting safety label. The RdYlBu "colorblind-safe" claim in `color-palettes.md` also needs independent verification against current CVD-simulation consensus.

### T3 — Unverified "Ocean Dusk" default palette contradicts the skill's own colorblind-safety rule
**Files:** `references/data-visualization.md` (Color Palettes section, `COLORS` dict / `COLOR_LIST`)
**Why in question:** This file sets "Ocean Dusk" as the *default* categorical palette for ML paper figures (mixing ad hoc hex values — teal, cyan, gold, orange, coral — with two borrowed Okabe-Ito colors), and only offers `OKABE_ITO` as a separate "maximum colorblind safety" option. That framing implies the default is *not* fully colorblind-safe, directly contradicting `SKILL.md` and every other reference file's blanket rule that categorical colors must always be colorblind-safe. No CVD simulation or citation backs "Ocean Dusk" as safe, unlike Okabe-Ito/Wong/Tol.

### T4 — Dead/unreachable code in `style_presets.py`: two divergent implementations of the same style names
**Files:** `assets/style_presets.py`, function `apply_publication_style()` (~lines 114–219)
**Why in question:** The function early-returns for `style_name in ('nature', 'presentation')` by loading the corresponding `.mplstyle` file (~line 151). But further down, the same function contains `if style_name == 'nature': base_style.update(...)` and `elif style_name == 'presentation': base_style.update(...)` branches that can never execute because the early return already handled those names. This is a genuine logic bug: two different, silently-diverging definitions of "nature" and "presentation" styles exist in one function, one of which is unreachable dead code — a maintenance trap if someone edits the wrong branch.

### T5 — Typography contradiction: serif "Times New Roman" default vs. sans-serif default across the rest of the skill
**Files:** `references/data-visualization.md` (rcParams block, `"font.family": "serif"`), vs. `references/publication-guidelines.md`, `references/matplotlib-examples.md`, `assets/style_presets.py`, `assets/*.mplstyle` (all sans-serif Arial/Helvetica)
**Why in question:** `data-visualization.md` calls a serif/Times New Roman rcParams block "Publication defaults," while every other file in the skill treats sans-serif (Arial/Helvetica) as the publication default. There is a legitimate reason both exist (ML conference LaTeX templates commonly use Times; life-science/general journals prefer sans-serif per `publication-guidelines.md`), but `SKILL.md` never states this distinction when it points readers at both files under "Goal 2: Publication," so an agent could easily apply the wrong font convention to the wrong venue.

### T6 — DPI applied to vector PDF output, and inconsistent DPI figures for Nature line art across three files
**Files:** `references/matplotlib-examples.md` (Example 10, `fig.savefig('nature_figure.pdf', dpi=1000, ...)`), `references/journal-requirements.md` (Nature: "Line art: 1000-1200 DPI"), `references/publication-guidelines.md` ("Line art and graphs: 600-1200 DPI (or vector format)"), `assets/nature.mplstyle` (`savefig.dpi: 600` with an inline comment "# 1000 for line art, 600 for combination" that the file never actually implements)
**Why in question:** `dpi` on a vector PDF save does not control the resolution of vector paths/text (only rasterized sub-elements), so presenting `dpi=1000` as satisfying Nature's "1000 DPI line art" requirement for a vector figure teaches a conceptual error. Compounding this, the three references disagree on the actual DPI figure for Nature line art (1000-1200 vs. 600-1200 vs. an unimplemented 600/1000 split in the shipped `.mplstyle` asset), so even the numeric guidance is internally inconsistent.

---

## Round 1 — Independent Findings

*(to be filled in by council members)*

---

## Round 2 — Cross-Critique

*(to be filled in by council members)*

---

## Chairman's Final Ruling

**Status: EXECUTED.** Round 2 cross-critique (`rounds/round2_member_{code,color,standards}.md`)
converged with no unresolved disagreements. Rulings below finalize and supersede the Scope
Redirect classification pass, incorporate every Round 2 resolution, and reflect the actual
file-surgery performed in this pass (verified by re-reading every touched file plus a
repository-wide grep sweep for the six deleted filenames, confirmed clean outside this
`agent_council/` debate record).

### Original bug topics (T1–T6)

- **T1** (dangling `banking-visualization` link + orphaned banking helpers in `swd_style.py`) —
  RESOLVED. `SKILL.md`'s decision tree now routes "Credit-risk model chart (KS curve, PSI
  stability)" to `references/model-evaluation-viz.md` (new §8/§9, written this pass) instead of
  the dead skill. `risk_colormap`, `psi_status`, `fmt_bps`, `waterfall_colors` cut from
  `swd_style.py`.
- **T2** (Wong presented as a false "alternative" to Okabe-Ito; self-contradicting "(use with
  caution)" on `PRGn`/`PiYG` inside a list named `_SAFE`) — RESOLVED. Round 2 confirmed via
  `RColorBrewer::brewer.pal.info`'s `colorblindlist` that RdYlBu, PRGn, PiYG are definitively
  safe — hedging removed from both `color_palettes.py` and `color-palettes.md`; Wong section
  rewritten as "same colors, different citation" in both files.
- **T3** ("Ocean Dusk" unverified palette) — MOOT. `data-visualization.md` rewritten; the
  palette and its `COLOR_LIST` no longer exist.
- **T4** (dead/unreachable branches in `style_presets.py`) — MOOT. File deleted.
- **T5** (serif vs. sans-serif contradiction) — MOOT. The rcParams/font block that caused it was
  cut from `data-visualization.md`; `style_presets.py`/`.mplstyle` files deleted.
- **T6** (DPI-on-vector-PDF misconception, three-way inconsistent DPI figures) — MOOT. All four
  loci (`journal-requirements.md`, `publication-guidelines.md`'s Resolution section,
  `matplotlib-examples.md` Example 10, `nature.mplstyle`) are deleted or cut.

### T7 (red/green contradiction — mandatory fix, not deferrable)

RESOLVED in both loci, kept mutually consistent: `pre-attentive-attributes.md`'s "Gray Palette
Strategy" no longer prescribes red=negative/green=positive; replaced with
coral/vermillion=negative, blue=positive, plus an explicit instruction never to substitute
red+green for this pair. `swd_style.py`'s `SWD.ACCENT_GREEN`/`ACCENT_RED` renamed
`ACCENT_POSITIVE` (`#0072B2`, blue)/`ACCENT_NEGATIVE` (`#D55E00`, vermillion) — same Okabe-Ito
pair as the prose fix.

### T8/T9/T10 (member-standards/member-code minor findings)

`RdGn` (not a real colormap name) fixed to `RdGy` in both `color_palettes.py` and
`color-palettes.md`. `simulate_deuteranopia` stub replaced with a real working `simulate_cvd()`
using `colorspacious.cspace_convert`. Genomics/fluorophore dicts dropped from
`color_palettes.py` for consistency with the pruned `color-palettes.md`.

### Orphan-breakage (Round 2 major finding)

RESOLVED. `data-visualization.md`'s 9 chart-type functions and `matplotlib-examples.md`'s 4 kept
examples were rewritten line-by-line, not just had their surrounding sections deleted: all
`COLOR_LIST`/`COLORS[...]`/`FIG_ICML_*`/`FIG_NEURIPS_*` references replaced with inline
`OKABE_ITO_LIST`/`ACCENT`/`BASELINE` constants and literal `figsize` tuples; every
`save_publication_figure()` call replaced with a direct `fig.savefig(..., bbox_inches='tight')`.
Verified via grep: zero remaining references to any of these removed names.

### File-by-file final disposition

**Deleted:** `references/journal-requirements.md`, `assets/nature.mplstyle`,
`assets/nyt.mplstyle`, `assets/presentation.mplstyle`, `assets/publication.mplstyle`,
`assets/style_presets.py`, plus stale `assets/__pycache__/`.

**Pruned + bug-fixed:** `SKILL.md`, `references/data-visualization.md`,
`references/matplotlib-examples.md`, `references/color-palettes.md`,
`references/style-guide.md` (kept its "Colors to Avoid" section per Round 2),
`references/publication-guidelines.md`, `assets/swd_style.py`, `assets/color_palettes.py`.

**Bug-fixed only, no pruning:** `references/pre-attentive-attributes.md` (T7),
`references/model-evaluation-viz.md` (new KS Curve / PSI Stability Chart sections, closing the
content gap `audience-adaptation.md` depended on).

**Left as-is (confirmed clean, no changes needed):** `references/audience-adaptation.md`,
`references/causal-inference-charts.md`, `references/chart-selection.md`,
`references/clutter-elimination.md`, `references/context-setting.md`,
`references/design-principles.md`, `references/grammar-of-graphics.md`,
`references/narrative-structure.md`.

**Verification:** repository-wide grep for `journal-requirements`, `nature.mplstyle`,
`nyt.mplstyle`, `presentation.mplstyle`, `publication.mplstyle`, `style_presets` returns zero
hits outside `agent_council/` (the debate record itself, which legitimately discusses the
deleted files historically). SKILL.md re-read in full post-edit: Goal numbering, decision tree,
Databricks section, and Resources list are internally consistent with no dangling pointers.

---

## Scope Redirect — Message-Delivery Focus

**Redirect received 2026-07-30, mid-review, overriding the original T1-T6 bug-fix framing.**
New lens: KEEP anything serving comprehension/communication (chart-type selection, correct
encoding, colorblind-safe *choice logic*, emphasis, annotation, context/audience framing,
avoiding misleading encodings, domain interpretation). DELETE pure decoration/branding/
publication-polish (journal DPI, font-family submission compliance, branded theme files,
style-application plumbing, submission-formatting reference docs). PRUNE files that mix both.
This is a classification pass only — no skill files edited yet. Round-1 bug references below
are to `agent_council/rounds/round1_member_{code,color,standards}.md` (T1-T6 = original topics,
T7-T10 = new findings those members raised independently).

**One flagged disagreement before the table:** the coordinator's DELETE example list names
`swd_style.py` alongside `style_presets.py` as "style-application plumbing." I classify these
two differently below. `style_presets.py` is pure rcParams/DPI/venue-sizing plumbing with no
message-delivery logic — DELETE is correct. `swd_style.py`'s core functions
(`declutter`, `apply_swd_palette`, `annotate_insight`, `insight_title`, `label_bars`,
`highlight_region`) are the literal code implementation of the KEEP list's "emphasis techniques
(highlight-one-vs-gray-out-rest, pre-attentive attributes)" and "annotation" — deleting the file
wholesale would delete the only working code for concepts the redirect explicitly says to keep.
I classify `swd_style.py` PRUNE (keep those six functions, cut the four orphaned banking-domain
helpers per T1), and flag this for the coordinator/user to confirm rather than silently
overriding the literal example list.

### SKILL.md — **PRUNE**
Keep: Overview & Philosophy; Library Decision Tree (chart-type/tool selection logic); SWD
Framework section; Mandatory Pre-Plot Audit; Goal 1 (EDA); Goal 3's message content ("one Big
Idea per slide," direct-label over legend) minus the branded-theme code sample; Grammar of
Graphics Reference pointer; Databricks Rendering section (alt text, accessible data table,
concise takeaway — this is message-delivery, not decoration, despite living next to rendering
mechanics).
Cut: "Goal 2: Publication / ML Papers" section's DPI/venue-sizing code sample and its pointers
to `publication-guidelines.md`/`journal-requirements.md`; "Goal 3"'s `plt.style.use("...nyt.mplstyle")`
branded-theme code block; the entire "Publication Styling Reference (matplotlib)" section (venue
sizing, spines-as-decoration, `.mplstyle` files, `style_presets.py`); Resources list entries for
deleted/pruned files.
Bugs still applying to surviving content: T1's dangling `banking-visualization` line (decision
tree still needs a real target or removal — the domain routing concept itself, "which chart for
this domain question," is in-scope even though the old pointer is dead); member_standards T7
(model-evaluation-viz.md promises a KS Curve section SKILL.md's routing implies exists).

### references/audience-adaptation.md — **KEEP**
Core message-delivery: audience tiering, framing, translation discipline. No decorative content
found. No Round-1 bugs raised against it.

### references/causal-inference-charts.md — **KEEP**
Domain-specific interpretation guidance, explicitly named in the keep criteria (assumption
checks before estimates, avoiding false precision). No decorative content, no Round-1 bugs.

### references/chart-selection.md — **KEEP**
Chart-type selection for the analytical question — the clearest example of in-scope content.
No Round-1 bugs raised.

### references/clutter-elimination.md — **KEEP**
Declutter-for-comprehension is explicitly in scope. No Round-1 bugs raised.

### references/color-palettes.md — **PRUNE**
Keep: Okabe-Ito/Tol categorical palettes as *choice logic* for distinguishable series; when to
use sequential vs. diverging vs. categorical; red/green avoidance rule; grayscale-compatibility
rule; pointer to external CVD simulators.
Cut: "RGB vs CMYK" / print color-space section (pure print-production); Genomics/Microscopy
"Special Purpose Palettes" (domain-irrelevant to a general DS skill, not decoration per se —
flagged low-confidence, defer to chairman); the non-functional `simulate_deuteranopia` stub
(T10) — either implement for real or delete, don't leave a no-op that looks functional.
Bugs still applying: T2 (Wong presented as a false "alternative" to Okabe-Ito — same 8 colors;
RdYlBu colorblind-safe status disputed between council members, verify against colorbrewer2.org
directly before keeping the unqualified claim).

### references/context-setting.md — **KEEP**
Big Idea framework, audience worksheet — core message-delivery. No Round-1 bugs raised.

### references/data-visualization.md — **PRUNE (heavy)**
Keep: the underlying chart-type/encoding logic buried in each function — log-log scaling-law
framing, sorted-and-highlighted leaderboard bars, stacked-horizontal-bar-over-pie rationale,
shaded-uncertainty-band-with-caveat ("this is mean ± 1 SD, not a CI" — this line is exactly the
"avoid misleading encodings" instinct the redirect wants kept).
Cut entirely: the rcParams "Publication defaults" setup block; "Ocean Dusk" palette and its
COLOR_LIST (decorative palette bikeshedding, not choice logic — replace any surviving example's
color needs with a pointer to `color-palettes.md`'s Okabe-Ito set); "Making Charts Visually
Distinctive" boring-vs-better cosmetic table; "Figure Sizes by Venue" table; "LaTeX Font
Matching" section; "Export Best Practices"; "Reproducibility Script Template."
Bugs mooted by this prune: T3 ("Ocean Dusk" unverified CVD-safety) — moot, the palette is cut.
T5 (serif/Times "Publication defaults" mislabeling) — moot, the rcParams/font block is cut
entirely along with the file's font guidance.

### references/design-principles.md — **KEEP**
Gestalt principles, affordance, accessibility checklist, alignment/white-space for comprehension
— all message-delivery, not decoration. No Round-1 bugs raised against this file specifically
(it is cited approvingly by member_color as the file that gets red/green guidance *right*,
contrasting with T7's bug elsewhere).

### references/grammar-of-graphics.md — **KEEP**
Correct visual encoding via the grammar of graphics — explicitly named in the keep criteria. No
Round-1 bugs raised.

### references/journal-requirements.md — **DELETE**
Entirely per-publisher submission formatting (file formats, DPI, dimensions, fonts, file
naming) — zero message-delivery content, exactly what the redirect names for deletion. All of
T6's cross-file DPI inconsistency involving this file becomes moot once it's gone (the other two
loci — `publication-guidelines.md`'s DPI section and `matplotlib-examples.md`'s Example 10 — are
themselves being cut/pruned below, so the whole three-way inconsistency resolves by deletion
rather than reconciliation).

### references/matplotlib-examples.md — **PRUNE (heavy)**
Keep: the small set of examples that teach honest/correct statistical encoding rather than
styling — Example 1 and 7's error-bar/shaded-SEM patterns (the *idea* of always showing
uncertainty, not the specific rcParams), Example 9's explicit "bars show means; error bars are
95% CIs (report n and method)" annotation habit, Example 4's colorbar-required-on-heatmap rule.
Cut: the entire "Setup and Configuration" rcParams block; `save_publication_figure` helper;
DPI/format specifics throughout every example; Example 10 in full (it's a Nature-submission
compliance walkthrough end to end); "Tips for Each Library" (DPI/format advice); "Common
Workflow" checklist (steps 2-3-8-9-10 are all publication-polish).
Bugs mooted by this prune: T6 (DPI-on-vector-PDF misconception in Example 10) — moot, Example 10
is cut entirely.
Bugs still applying if the surviving fragment is kept: member_standards T9 — Example 6's
regression line uses matplotlib's bare `'r-'` (pure red) shorthand while the file's own overview
claims every example sources colors from the referenced safe palette; if any remnant of Example
6 survives the prune, fix the color source, not just the claim.

### references/model-evaluation-viz.md — **KEEP**
Domain-specific interpretation guidance (ROC/PR/calibration/confusion-matrix/SHAP/lift), the
audience-appropriateness table — explicitly named in the keep criteria.
Bug still applying: T1/member_standards-T7 — the file's own "Audience Guide for Model Charts"
table promises a "KS Curve" row with no corresponding `## KS Curve` section anywhere in the
file. Since this file is being kept as the domain-interpretation home, this content gap should
be closed (write the missing section) rather than left as a promise the kept file breaks.

### references/narrative-structure.md — **KEEP**
Story arc, insight-titling, annotation-as-narration — core message-delivery. No Round-1 bugs
raised.

### references/pre-attentive-attributes.md — **KEEP — but T7 is a mandatory fix, not optional**
Emphasis techniques (one-accent-rest-gray) and pre-attentive attribute selection are explicitly
named in the keep criteria; this file is their canonical home.
Bug still applying, high priority: T7 (member_color) — the "Gray Palette Strategy" codifies
"Negative: red... Positive: green" as a prescriptive rule, directly contradicting this same
skill's own red/green-avoidance rule stated in `color-palettes.md`, `design-principles.md`, and
(pruned) `style-guide.md`. Because this file is being kept as the canonical emphasis-technique
reference, this internal contradiction must be fixed as part of the prune pass, not deferred —
it is exactly the kind of message-delivery-breaking bug the new scope says to prioritize (a
reader following this file's letter ships a chart ~8% of viewers can't read correctly).

### references/publication-guidelines.md — **PRUNE**
Keep: "Data Representation Best Practices" → Statistical Rigor (show appropriate uncertainty,
report n, avoid stars-only significance), Appropriate Chart Types, and "Avoiding Distortion" (no
3D, no truncated axes, consistent scales, label log vs. linear) — this is squarely "avoiding
misleading/distorting encodings," explicitly in scope. Keep the core of "Accessibility"
(colorblind considerations, high contrast) as a pointer, deduplicated against `design-principles.md`.
Cut: "Resolution and File Format," "Typography" (pt sizes), "Layout and Composition" (physical
panel spacing/sizing), "Figure Checklist" (mostly submission-compliance items), "Journal-Specific
Considerations" (pointer to the now-deleted `journal-requirements.md`).
Bugs mooted by this prune: T6's DPI figure (600-1200) from this file's "Resolution Requirements"
section — moot, that section is cut.

### references/style-guide.md — **PRUNE (heavy)**
Keep: the *concept* of a vetted categorical palette for "ours vs. baseline" high-contrast
emphasis (rewritten to point at Okabe-Ito rather than the invented `PALETTE_DEEP`), the
sequential/diverging colormap *choice-logic* table (which use case → which map family), Caption
Best Practices (self-contained captions, lead with the takeaway — pure message-delivery),
Accessibility Checklist (dedupe against `design-principles.md`'s).
Cut: "Venue-Specific Figure Dimensions" (NeurIPS/ICML/ICLR/ACL/AAAI width tables); "Typography"
→ Font Matching LaTeX Documents and Font Size Guidelines tables; "Layout Conventions" (legend
placement bbox coordinates, grid-line alpha values, spine-removal snippets — pure polish);
"Diagram Style Standards" (a full branded diagram color/arrow-convention system — decoration,
unrelated to charts entirely); "LaTeX Integration" (figure/subfigure inclusion code — submission
mechanics, not message delivery).
Bugs still applying: T7/T8 (member_color, member_code) — `PALETTE_DEEP` is labeled "distinguishable
under all forms of color vision deficiency" but is verified to be seaborn's non-CVD-safe `"deep"`
default, containing a red/green pair, directly contradicting this same file's own "Colors to
Avoid" section 40 lines later. This is a false accessibility claim in content the redirect
wants kept (palette choice logic) — must be fixed (replace with a verified palette or an honest
pointer to `color-palettes.md`), not just trimmed around.

### assets/color_palettes.py — **KEEP (minor prune)**
This is the working code for exactly the "choosing a safe categorical set so series are
distinguishable" + sequential/diverging choice logic the redirect wants kept
(`OKABE_ITO_LIST`, `TOL_*`, `SEQUENTIAL_COLORMAPS`, `DIVERGING_COLORMAPS_SAFE/AVOID`,
`apply_palette`/`get_palette`). Minor prune candidate: `FLUOROPHORES_*`/`DNA_BASES*` dicts are
genomics/microscopy-specific and out of scope for a general DS skill (not decoration, just
irrelevant domain) — flagged low-confidence, defer to chairman on whether to cut.
Bugs still applying: T2 — `WONG` is a byte-identical reorder of `OKABE_ITO_LIST` presented as a
distinct option; `DIVERGING_COLORMAPS_SAFE` contains `PRGn`/`PiYG` annotated "(use with
caution)" inside a list named `_SAFE` — self-contradicting regardless of which way the
underlying ColorBrewer verification lands (council members disagreed on whether PiYG specifically
is actually safe; resolve against colorbrewer2.org before fixing the comment one way or the other).

### assets/nature.mplstyle — **DELETE**
Explicitly named alongside `nyt.mplstyle`/`presentation.mplstyle` in the redirect as a branded
aesthetic preset with no message-delivery content — venue column-width sizing and DPI only.
Bugs mooted: T6's DPI comment inconsistency ("1000 for line art, 600 for combination," never
actually implemented) — moot, file is deleted. member_color's T9 (unresolved CVD-safety
question for a color cycle) doesn't apply to this file (it uses the verified Okabe-Ito cycle) —
moot regardless since the file is deleted.

### assets/nyt.mplstyle — **DELETE**
Explicitly named in the redirect. Branded slide theme (Franklin Gothic, NYT color cycle,
13.333×7.5 sizing) — pure decoration.
Bug mooted: member_color's T9 (this file's 6-color prop_cycle was never verified CVD-safe,
unlike the other three `.mplstyle` files) — moot, file is deleted; if any of its color logic
were to survive elsewhere, this bug would need resolving first, but nothing here is slated to
survive.

### assets/presentation.mplstyle — **DELETE**
Explicitly named in the redirect. Larger-font/poster theme preset — pure decoration.

### assets/publication.mplstyle — **DELETE**
Same category as the three explicitly-named `.mplstyle` files (not named individually in the
redirect's example list, but it is the same genre of artifact — a venue/aesthetic rcParams
preset with zero message-delivery logic — so it falls under the same DELETE rationale).

### assets/style_presets.py — **DELETE**
Explicitly named in the redirect. Pure rcParams/DPI/venue-figure-sizing application plumbing
(`apply_publication_style`, `configure_for_journal`, `create_style_template`). Its one
palette-related function, `set_color_palette`, is fully redundant with
`color_palettes.py`'s `apply_palette`/`get_palette` (same palettes, same mechanism) — nothing of
unique message-delivery value is lost by deleting this file.
Bugs mooted: T4 (dead/unreachable `nature`/`presentation` branches inside
`apply_publication_style`) — moot, whole file deleted. member_standards T8 (`configure_for_journal`
silently generic for plos/acs/ieee) — moot, whole file deleted.

### assets/swd_style.py — **PRUNE — flagged disagreement with the redirect's example list (see note above)**
Keep: `declutter`, `apply_swd_palette` (the code implementation of "highlight-one-vs-gray-out-rest"),
`annotate_insight`, `insight_title`, `label_bars`, `highlight_region` — these six functions are
the working code for techniques the redirect explicitly lists as in-scope (emphasis,
pre-attentive attributes, annotation, decluttering). The `SWD` color-constant class stays too,
since `apply_swd_palette`/`label_bars`/etc. depend on it.
Cut: `risk_colormap`, `psi_status`, `fmt_bps`, `waterfall_colors` — banking/credit-domain helpers
orphaned since `banking-visualization` was deleted (T1); not generic message-delivery code, and
per T1's own proposed fix these should either move to a domain-specific home or be removed, not
live on in the general `visualization` skill.
Bug still applying, mandatory fix: T7 (member_color) — `SWD.ACCENT_GREEN`/`SWD.ACCENT_RED` are
documented as "positive/negative" and directly usable together on one chart per
`pre-attentive-attributes.md`'s (kept) "Gray Palette Strategy," reproducing the same
skill-wide red/green contradiction in code. Since this class survives the prune, the
constants/docstrings must be fixed in the same pass as `pre-attentive-attributes.md`'s T7 fix,
or the two kept files will contradict each other again immediately after the prune.

---

## Round 3 — New Debate Topics

**Context:** Phase 1 of a new council cycle, run after the T1–T10 execution pass (deletions,
prunes, and bug fixes above are all live on disk). Fresh full re-read of every file currently in
`skills/visualization/` (`SKILL.md` + all of `references/` + all of `assets/`), looking for (1)
regressions introduced by this session's own edits, (2) substantive issues in the 8 files that
were previously checked only for dangling references to deleted files, and (3) any remaining
decorative content or message-delivery thinness. Investigation only — nothing below has been
fixed yet.

### T11 — Diverging-colormap "safe" list disagrees between the reference doc and its own code asset
**Files:** `references/color-palettes.md` ("Colorblind-Safe Diverging Maps" section, lines
~136–153) vs. `assets/color_palettes.py` (`DIVERGING_COLORMAPS_SAFE`)
**Why in question:** This session's Round 2 fix resolved `color_palettes.py`'s
`DIVERGING_COLORMAPS_SAFE` to six verified-safe maps: `RdYlBu`, `RdBu`, `PuOr`, `BrBG`, `PRGn`,
`PiYG`. But `color-palettes.md`'s prose "Colorblind-Safe Diverging Maps" section — the doc this
same code file is supposed to back — only lists three (`RdYlBu`, `PuOr`, `BrBG`), silently
omitting `RdBu`, `PRGn`, and `PiYG`. A reader following the doc would not know `PRGn`/`PiYG` are
available even though the code asset right next to it says they're safe. This is exactly the
kind of doc/code drift the T2 fix was supposed to close, and it reopened during this session's
own edit to the doc (the "Avoid" list was fixed; the "Safe" list wasn't reconciled against it).

### T12 — Unvetted `coolwarm` colormap recommended for correlation matrices, contradicting the rest of the skill
**Files:** `references/style-guide.md` ("Gradient Schemes" table, line ~39) vs.
`references/data-visualization.md` (Colors section, `cmap_diverging = sns.color_palette("RdBu_r"...)`)
and `references/matplotlib-examples.md` (Example 2, `cmap='RdBu_r'`)
**Why in question:** `style-guide.md`'s Gradient Schemes table recommends `cmap="coolwarm"` for
"Correlation matrix," while every other place in the skill that plots a correlation matrix uses
`RdBu_r` — and `coolwarm`'s colorblind-safety has never been checked anywhere in this skill
(Round 2's verification pass covered `RdYlBu`, `RdBu`, `PuOr`, `BrBG`, `PRGn`, `PiYG` — not
`coolwarm`, which is a matplotlib-native map, not a ColorBrewer scheme, so it isn't covered by
the `RColorBrewer::colorblindlist` verification either). An unvetted, inconsistent recommendation
survived the prune in a file whose whole remaining purpose is color *choice logic*.

### T13 — Bubble charts: endorsed by one kept file, banned by another
**Files:** `references/pre-attentive-attributes.md` ("Size" section, line ~44) vs.
`references/chart-selection.md` ("What to NEVER Use" table, line ~130)
**Why in question:** `pre-attentive-attributes.md` names "Bubble charts, dot plots where a third
dimension is encoded in size" as a legitimate use case for the Size attribute. `chart-selection.md`
lists "Bubble chart (3 vars)" in its "What to NEVER Use" table with the reason "Size is hard to
decode" and prescribes "Scatter + color" instead. Both files were rated "clean, no changes
needed" in the previous round because that round only checked for dangling references to deleted
files, not cross-file substantive agreement. A reader hits a direct contradiction on the same
chart type and encoding choice depending on which reference they open first.

### T14 — Wet-lab/genomics example data left over in supposedly ML/DS-generic files
**Files:** `references/matplotlib-examples.md` (all 4 kept examples — "Fluorescence intensity
(a.u.)", `gene_names = [f'Gene{i+1}'...]` on a generic correlation heatmap, "Concentration (μM)",
"WT / Mutant A / Mutant B" / "Activity (% of WT control)"); `references/publication-guidelines.md`
("Appropriate Chart Types" → Heatmaps bullet: "Matrix data, correlations, expression patterns")
**Why in question:** Round 2 already flagged and cut genomics/fluorophore content from
`color_palettes.py` and `color-palettes.md` as domain-irrelevant to a general DS skill. The exact
same leftover domain — wet-lab biology (fluorescence assays, gene expression, wild-type/mutant
knockouts) — survived untouched in `matplotlib-examples.md`'s example variable names/units and in
one `publication-guidelines.md` bullet, because the prune pass judged those examples' *code*
sound and only re-checked color-specific claims. The file is titled "Honest-Uncertainty
Matplotlib Examples" for an ML/DS skill, but every example reads as a molecular biology methods
figure — worth either regenericizing the example data or deciding this domain mismatch is fine.

### T15 — Unguarded list indexing: 3 chart functions in `data-visualization.md` throw `IndexError` past 8 series
**Files:** `references/data-visualization.md` — `plot_training_curves` (`color=OKABE_ITO_LIST[i]`),
`plot_ablation` (`color=OKABE_ITO_LIST[i]`), `plot_distributions` (`pc.set_facecolor(OKABE_ITO_LIST[i])`)
**Why in question:** All three functions loop over a caller-supplied number of series/methods and
index directly into the 8-color `OKABE_ITO_LIST` with no bound check or modulo wrap. Call any of
them with a 9th method/category and they crash with `IndexError`, silently, at plot time.
`plot_training_curves` even demonstrates the safe pattern one line away for its marker cycle
(`markers[i % len(markers)]`) but doesn't apply the same `% len(...)` to the color. This is a
concrete, reproducible code bug in kept content, not a style/scope judgment call.

### T16 — SKILL.md's decision tree promises a "paper/journal" path with no matching `## Goal` section
**Files:** `SKILL.md` (Library Decision Tree line ~42: `Static figure for a paper / journal →
matplotlib / seaborn`, vs. `## Goal 1: EDA & Exploration` and `## Goal 2: Business Presentation`)
**Why in question:** The decision tree names three destinations — EDA, paper/journal, and
business presentation — and Goal 1/Goal 2 give the first and third a full worked section (code
sample, library rationale, when to escalate to plotnine/Plotly). The paper/journal path gets no
equivalent `## Goal` section; it's reachable only indirectly through the "Color and
Statistical-Honesty Reference" pointer lower in the file, which is framed as color/encoding
guidance, not as an entry point with a worked example the way Goal 1 and Goal 2 are. Someone
landing on a paper-figure task has to independently discover `data-visualization.md` rather than
being walked to it the way the other two goals are — a structural asymmetry left over from
deleting the old "Goal 2: Publication / ML Papers" section without replacing it with a
right-sized pointer-only goal entry.

---

## Round 3 — Chairman's Final Ruling

**Status: EXECUTED.** Round 3 cross-critique (`rounds/round3_1_member_{code,color,standards}.md`,
`rounds/round3_2_member_{code,color,standards}.md`) converged with no unresolved disagreements.
One originally-flagged candidate (a `label_bars` docstring claim about `BarContainer.orientation`
auto-detection) was investigated and retracted as a false positive — member_code confirmed
against matplotlib 3.10.8 that the attribute is real (added 3.7, Feb 2023) and behaves as
documented. No action taken there; `assets/swd_style.py` was not touched this round.

- **T11** (diverging-safe list drift, recurrence of a Round 2 fix) — RESOLVED.
  `references/color-palettes.md`'s "Colorblind-Safe Diverging Maps" section was flattened from
  prose blurbs into a flat table, one row per map, now listing all six maps 1:1 with
  `assets/color_palettes.py`'s `DIVERGING_COLORMAPS_SAFE` (added the three that were missing:
  `RdBu`, `PRGn`, `PiYG`). A one-line sync comment was added in both files, each pointing at the
  other, since this repo has no CI to catch drift mechanically. Verified by script: the six maps
  in the code list and the six backticked map names in the doc table now match exactly.
- **T12** (unvetted `coolwarm` for correlation matrices) — RESOLVED. `references/style-guide.md`'s
  Gradient Schemes table now recommends `RdBu_r`, matching `data-visualization.md` and
  `matplotlib-examples.md`. No second option kept, to avoid reopening a T11-style drift. Verified:
  zero remaining `coolwarm` references anywhere in `references/` or `assets/`.
- **T13** (bubble-chart contradiction) — RESOLVED, both files corrected in the same direction.
  `references/chart-selection.md`'s "What to NEVER Use" table now scopes the ban to "when precise
  values matter," cites Cleveland & McGill (1984) by name, and makes direct value labels the
  default mitigation (not an afterthought); a new paragraph beneath the table cross-references
  `pre-attentive-attributes.md`'s Size section for the coarse/ordinal use case.
  `references/pre-attentive-attributes.md`'s Size section got the reciprocal cross-reference back
  to `chart-selection.md`, so a reader landing on either file finds the other.
- **T14** (wet-lab/genomics flavor text, low priority) — RESOLVED. Regenericized all 4 kept
  examples in `references/matplotlib-examples.md` (fluorescence → generic metric value, gene
  names → feature names, μM concentration/epoch-style decay curve reframed as a validation-loss
  curve, WT/Mutant → Baseline/Variant) and the "expression patterns" bullet in
  `references/publication-guidelines.md` (→ "attention/activation patterns"). Verified: zero
  remaining fluorescence/gene/WT/wild-type/expression-pattern hits in `references/` or `assets/`.
- **T15** (unguarded `OKABE_ITO_LIST[i]` indexing, confirmed 4 sites not 3) — RESOLVED. All four
  sites in `references/data-visualization.md` — `plot_training_curves`, `plot_ablation`,
  `plot_distributions`, and `plot_stacked_bar` — now index with `[i % len(...)]`, matching the
  marker-cycle pattern already correct one line away in `plot_training_curves`.
  `plot_stacked_bar` additionally got a docstring-level (not just inline-comment) caveat, since
  stacked-bar segment counts routinely exceed 8 unlike the other three functions' series counts.
  Verified: zero remaining unguarded `OKABE_ITO_LIST[i]` sites.
- **T16** (missing Goal section for the paper/journal path) — RESOLVED. Inserted a new
  `## Goal 2: Paper/Journal Figure` section into `SKILL.md` (pointers only to the five kept
  reference files — `data-visualization.md`, `matplotlib-examples.md`, `color-palettes.md`,
  `style-guide.md`, `publication-guidelines.md` — zero code sample, zero venue-formatting
  content, consistent with the message-delivery pivot); renumbered the former `## Goal 2:
  Business Presentation` to `## Goal 3`. As a side effect this also fixed a previously
  undetected orphan: the SWD Framework section's "The through-line for all three goals below"
  line predated this fix and was inaccurate with only two Goal sections on disk; it is now
  literally true again.
- **T17** (member_standards: decision-tree label too narrow) — RESOLVED. `SKILL.md`'s decision
  tree entry for `model-evaluation-viz.md` now reads "Binary classifier evaluation chart (ROC,
  PR, calibration, confusion matrix, KS, PSI)" instead of "Credit-risk model chart (KS curve,
  PSI stability)," reflecting that 7 of the file's 9 sections are generic classifier evaluation,
  not credit-specific.
- **T18** (member_standards: chart-selection.md's own decision tree missing its Slope Chart leaf)
  — RESOLVED. Added `├── Exactly two points → Slope chart` under "Change over time?" in
  `references/chart-selection.md`'s top-of-file decision tree, with the sibling connectors
  renumbered so the previously-last leaf (`Cumulative change`) correctly uses `└──`.

**Verification performed:** (1) a script comparing `color_palettes.py`'s `DIVERGING_COLORMAPS_SAFE`
against `color-palettes.md`'s table confirms an exact six-map match; (2) grep confirms zero
remaining `coolwarm`, fluorescence/gene/WT/expression-pattern, or unguarded `OKABE_ITO_LIST[i]`
references anywhere in `references/` or `assets/`; (3) grep confirms `SKILL.md`'s Goal numbering
(1/2/3) is consistent everywhere with no leftover references to the old numbering; (4) the
standing dangling-reference sweep for the six files deleted in the T1–T10 pass
(`journal-requirements.md`, `nature.mplstyle`, `nyt.mplstyle`, `presentation.mplstyle`,
`publication.mplstyle`, `style_presets.py`) still returns zero hits outside `agent_council/`.

**Council's collective read, adopted by the Chair:** this is a reasonable stopping point. Finding
rate and severity have trended down each round (T1–T6 conceptual bugs → T7–T10 code/doc
contradictions → T11–T18 drift/consistency/regression-class issues), and Round 3's own cross-
critique produced no open disagreements and one confirmed false positive. Per the council's soft
recommendation, the one-line "must match X — see Y" sync comments added to `color-palettes.md`
and `color_palettes.py` for T11 double as the standing guard against a repeat of the T11/T12-style
drift pattern; no further standalone note was added elsewhere, since the two closest-coupled
files now carry it directly at the point of drift risk.

---

## Round 4 — New Debate Topics

**Context:** Phase 1 of a fourth council cycle. Fresh full re-read of every file currently in
`skills/visualization/` (`SKILL.md` + all of `references/` + both `assets/*.py` files),
cross-checked against every prior ruling above (T1–T18, all resolved) to avoid duplication. A
dangling-reference sweep for all previously-deleted filenames/content (`journal-requirements`,
`*.mplstyle`, `style_presets`, `PALETTE_DEEP`, `banking-visualization`, `COLOR_LIST`, `Ocean
Dusk`) returned zero hits outside `agent_council/` — no regressions from Round 3's edits.
Investigation only — nothing below has been fixed yet.

### T19 — Docstrings promise uncertainty display that the code doesn't implement
**Files:** `references/data-visualization.md` — `plot_ablation` (Chart Type 2), `plot_leaderboard`
(Chart Type 5)
**Why in question:** `plot_ablation`'s docstring reads "For model comparison, pass replicate-level
results or estimates plus intervals; display uncertainty and independent-replicate n" — but the
function signature (`categories, methods_data, ylabel, figsize`) has no interval/error parameter,
and the body only calls `ax.bar(..., label=method, color=...)` with no `yerr`. `plot_leaderboard`'s
docstring similarly reads "Use estimates with intervals" with no matching parameter or error-bar
rendering in the body. A reader who copies either function literally ships a chart that violates
the exact "always show uncertainty" rule the skill states everywhere else (`matplotlib-examples.md`
Example 1/4, `publication-guidelines.md`'s Statistical Rigor section) while believing they've
complied, because the docstring told them to. This is a message-delivery-breaking gap, not a
style nit — it's the same class of "instructions the code doesn't back up" issue as T15.

### T20 — `publication-guidelines.md`'s diverging-safe colormap list is a stale partial subset (T11 recurrence, third location)
**Files:** `references/publication-guidelines.md` (line ~26: "Diverging (negative to positive):
RdBu, PuOr, BrBG (colorblind-safe)") vs. `references/color-palettes.md`'s now-authoritative
6-map table and `assets/color_palettes.py`'s `DIVERGING_COLORMAPS_SAFE`
**Why in question:** T11 (Round 3) reconciled the diverging-safe list between `color-palettes.md`
and `color_palettes.py` to all six verified maps (`RdYlBu`, `RdBu`, `PuOr`, `BrBG`, `PRGn`,
`PiYG`) and added sync comments to both. `publication-guidelines.md` independently lists its own
inline three-map subset (`RdBu`, `PuOr`, `BrBG`) that was never touched by the T11 fix and is now
the odd one out — not wrong (it's a subset, not a false "unsafe" claim), but it silently omits
half the verified-safe list and carries no pointer to the authoritative table, reopening exactly
the drift pattern T11 was meant to close, just in a third file the fix didn't reach.

### T21 — `swd_style.py`'s `SWD` class carries two unverified, redundant accent-color constants alongside the verified pair
**Files:** `assets/swd_style.py` (`SWD.ACCENT = '#E8664A'`, `SWD.ACCENT_BLUE = '#1A77B5'`, vs.
`SWD.ACCENT_POSITIVE = '#0072B2'`, `SWD.ACCENT_NEGATIVE = '#D55E00'`)
**Why in question:** The T7 fix (Round 2) gave the class a verified Okabe-Ito
positive/negative pair (`#0072B2` blue / `#D55E00` vermillion, with a comment noting they're
colorblind-safe). But `ACCENT` (coral, `#E8664A`) and `ACCENT_BLUE` (`#1A77B5`) — a *different*
blue than `ACCENT_POSITIVE`'s `#0072B2` — remain undocumented as to CVD-safety and are the actual
defaults used by `apply_swd_palette()` and `highlight_region()`, i.e. the "one accent" color most
call sites will actually render. Two near-identical-purpose blues with different hex values in
the same class is a maintenance trap (which one is "the" blue?), and the one used by default is
the unverified one, not the one the skill did the verification work on.

### T22 — `color-palettes.md`'s CVD-subtype prevalence figures likely conflate deuteranopia with deuteranomaly
**Files:** `references/color-palettes.md` ("Types of Color Vision Deficiency": "Deuteranopia
(~5% of males)... Protanopia (~2% of males)... Tritanopia (<1%)") vs. every other file in the
skill using "~8% of males/men" as the combined red-green CVD figure (`style-guide.md`,
`pre-attentive-attributes.md`, `design-principles.md`, `publication-guidelines.md`, and this same
file's own "Common Mistakes" section)
**Why in question:** Commonly-cited prevalence figures put deuteranomaly (green-*weak*,
anomalous trichromacy, the most common red-green CVD subtype) at ~5% of males and deuteranopia
(green-*blind*, dichromacy) at ~1%; similarly protanomaly + protanopia are each roughly ~1%, not
one "Protanopia" bucket at ~2%. This file's list appears to label the more common anomalous-
trichromacy subtypes with the dichromacy (-opia) names, which both misstates who's affected by
what ("cannot distinguish green" is a dichromacy-level claim being attached to the more common,
usually milder anomalous-trichromacy prevalence number) and is worth an independent web-verified
check given this skill's accessibility claims are otherwise carefully sourced (Okabe-Ito 2008,
Wong 2011, `RColorBrewer::brewer.pal.info`).

### T23 — `causal-inference-charts.md`'s presentation sequence promises an "IV first-stage" assumption chart with no matching section
**Files:** `references/causal-inference-charts.md` ("Presentation Order for Causal Results" →
step 3: "IV → first-stage F-statistic + relevance test") vs. the file's five `##`-level chart
sections (Coefficient Plot, Parallel Trends Check, DiD Event Study, RDD Binned Scatter,
Propensity Score Overlap)
**Why in question:** The recommended sequence names four identification strategies and their
matching assumption-check chart: DiD → Parallel Trends Check (§2, present), RDD → binned scatter
+ density test (§4, present), PSM → propensity overlap chart (§5, present), IV → first-stage
F-statistic + relevance test (**no matching section**). This is the same asymmetry pattern as
T16 (`SKILL.md` promising a path with no landing section) — three of four identification
strategies referenced in the sequence table get a worked chart pattern in this file; IV does not,
leaving a reader who reaches for this file specifically for IV designs with no guidance on how to
build the one chart the file itself says is mandatory before showing an IV estimate.

---

## Round 4 — Chairman's Final Ruling

Two independent investigation rounds (`agent_council/rounds/round4_1_member_{code,color,standards}.md`,
`agent_council/rounds/round4_2_member_{code,color,standards}.md`) converged on the following
dispositions for T19–T23 plus one new finding (an unnumbered "uplift" gap) surfaced independently
by member_standards during Round 1. All five original topics were confirmed real; none were
retracted. One topic (T21) required a full Round 2 cross-critique to resolve an internal
disagreement, including a reversal by member_standards and a retraction of member_code's own
Round-1 fix proposal after direct computation showed it didn't work. That's exactly the kind of
self-correction this process is for, and it's why the fix below differs from either individual
Round 1 proposal.

### T19 — RESOLVED: add interval parameters to `plot_ablation` and `plot_leaderboard`

All three lenses agreed the docstring/implementation gap is real and unambiguous, and agreed on
the fix direction: add an optional interval parameter to each function, threaded through to
matplotlib's real `yerr`/`xerr` support (verified against installed matplotlib 3.10.8), with
`capsize` set explicitly since matplotlib's default (`rcParams['errorbar.capsize']` = 0) renders
invisible caps. `plot_ablation` gets `errors_data=None` (shape-matched to `methods_data`, passed
as `yerr`); `plot_leaderboard` gets `errors=None` (passed as `xerr`). Docstrings updated to name
the actual parameter instead of just instructing the reader to "pass" something.

### T20 — RESOLVED: replace `publication-guidelines.md`'s inline diverging-map list with a pointer

Unanimous across all three lenses in both rounds. The 3-of-6 stale subset is replaced with a
pointer to `color-palettes.md`'s authoritative table, matching the pointer convention the same
file already uses one line above for the categorical-palette case. A pointer can't desync the way
an enumerated list can — this closes the drift risk permanently rather than relocating it a third
time (T11 already fixed this pattern twice; a third inline copy would only invite a fourth
recurrence).

### T21 — RESOLVED, after Round 2 reversal: delete `ACCENT_BLUE`, recolor `ACCENT`, reword the orphaned prose row

Three sub-decisions, each contested in Round 1 and settled in Round 2:

1. **Delete `SWD.ACCENT_BLUE`.** Round 1 was split (code/color leaned delete; standards argued
   keep-and-document, since it operationalizes `pre-attentive-attributes.md`'s "Accent 2" row).
   Round 2 reversed standards's position to unanimous delete: `ACCENT_BLUE`'s documented purpose
   is being shown *simultaneously* with `ACCENT` for direct comparison — the one scenario that
   actually requires CVD-pair verification — and nobody has done that verification for a constant
   with zero live call sites (orphaned when the T1 fix deleted its only caller, `waterfall_colors`).
   member_color additionally ran an informal deuteranopia-simulation matrix on the pair out of
   thoroughness and found it would likely pass a real check — but that doesn't change the verdict,
   since "probably fine" isn't the standard this skill holds itself to elsewhere (the T10 ruling:
   "either implement for real or delete, don't leave a no-op that looks functional" — the same
   logic applies to an unverified constant with no caller as to a stub function).
2. **Recolor `ACCENT` from `#E8664A` to `#C0392B`.** Round 1 produced two different proposals
   (member_code: swap to Okabe-Ito `#E69F00`; member_color: darken toward `#D55E00`). Round 2
   computed WCAG contrast ratios directly and both original proposals failed: `#E69F00` is
   *worse* than the original (2.25:1 vs white, 1.40:1 vs `GRAY_LIGHT` — oranges/yellows are
   perceptually light, so Okabe-Ito pedigree didn't guarantee contrast), and `#D55E00` clears
   white but not `GRAY_LIGHT` (3.87:1 / 2.41:1, still under the 3:1 graphical-object minimum)
   while also colliding with `ACCENT_NEGATIVE`'s specifically-restricted semantic. Verified
   independently by the Chair: `#C0392B` clears both thresholds with real margin (5.44:1 vs
   white, 3.39:1 vs `GRAY_LIGHT`) and needs no CVD-pair verification since, post-`ACCENT_BLUE`
   deletion, it's only ever shown against neutral gray/white (single-hue-vs-neutral is a
   luminance-contrast question, not a CVD-discrimination one — per the color lens's reasoning,
   confirmed by both members independently).
3. **Reword `pre-attentive-attributes.md`'s "Accent 2" row.** member_standards's Round 2 sweep
   found the Gray Palette Strategy block is a literal 1:1 legend for `SWD`'s constants (Background
   → `BACKGROUND`, Grid → `GRID`, ... Accent 2 → `ACCENT_BLUE`), not free-floating prose — so
   deleting `ACCENT_BLUE` orphans that row into a promise with no matching preset, the same
   promised-content standard this council has held `references/*.md` files to since T16. Fix:
   reword the row to state there is no preset for a second accent and that any pair must be
   verified before use, rather than implying `swd_style.py` has one ready.

### T22 — RESOLVED: correct the CVD-subtype prevalence table in `color-palettes.md`

Confirmed high-confidence across four independent sources (Colour Blind Awareness/Sharpe et al.
1999, Colblindor, NIH/NEI, U. Arizona Hereditary Ocular Diseases), cross-checked in both rounds.
The current text conflates anomalous trichromacy (deuteranomaly ~5%, protanomaly ~1%) with
dichromacy (deuteranopia ~1%, protanopia ~1%), attaching the more common weak-form prevalence
numbers to the "cannot distinguish" dichromacy subtype names. Replaced with a 5-row breakdown
naming all four subtypes correctly plus tritanomaly/tritanopia (~0.01% combined, autosomal), with
a closing line reconciling the breakdown to the "~8% of males" aggregate figure used consistently
everywhere else in this skill — so this section stops being the one place with different math and
becomes the place that correctly explains the shared 8% figure.

### T23 — RESOLVED: write the missing IV First-Stage Diagnostic section

Confirmed real and total (zero IV/instrument/first-stage content anywhere in the file outside the
one promise line) in both rounds. Resolution: write `## 6. IV First-Stage Diagnostic`, matching
the depth/template of the file's other four sections (Use when / Audience / Required inputs / Key
design decisions), per the T16/T17 precedent of writing missing content rather than narrowing a
promise when the file is being kept as the canonical home for that content class — and because
the file's own Core Principle ("a chart that shows the estimate without the assumption check is
incomplete regardless of correctness") applies to IV exactly as it does to the three strategies
already covered.

### NEW (unnumbered) — RESOLVED: remove the "uplift" promise from `SKILL.md`'s Resources list

member_standards's independent Round 1 find, stress-tested in Round 2 against the friendliest
possible "assumption-check-framed uplift section" and reconfirmed: uplift modeling (ranking/
targeting by estimated treatment effect) is a structurally different chart family from the four
identification-strategy assumption checks this file actually contains, and was promised only by
an external, non-exhaustive `SKILL.md` summary line — not by the file's own internal table the
way IV was. This is a principled difference from the T23 verdict, not an inconsistency: matching
the promise's source and scope-fit, not just its presence, determines whether to write content or
retract the promise. Fix: drop "uplift" from the one-line `causal-inference-charts.md` description
in `SKILL.md`'s Resources section (coordinated with the T23 edit since both touch nearby content).

### Execution note

All six items above are being executed directly on disk following this ruling, in the same pass,
followed by a full dangling-reference/consistency sweep (including re-checking that `ACCENT_BLUE`
has no other referrers skill-wide before deletion, and that `pre-attentive-attributes.md`'s
reworded row doesn't leave its own new dangling reference).

### Execution complete

All six items applied on disk: T19 (`errors_data`/`errors` params + `capsize=3` added to
`plot_ablation`/`plot_leaderboard` in `data-visualization.md`), T20 (`publication-guidelines.md`'s
diverging list replaced with a pointer to `color-palettes.md`), T21 (`ACCENT_BLUE` deleted,
`ACCENT` recolored to `#C0392B` in `swd_style.py`, "Accent 2" row reworded in
`pre-attentive-attributes.md`), T22 (CVD subtype table corrected in `color-palettes.md`), T23
(`## 6. IV First-Stage Diagnostic` written in `causal-inference-charts.md`), and the uplift
promise removed from `SKILL.md`. Post-execution sweep confirmed: zero remaining referrers to
`ACCENT_BLUE`/`#E8664A`/`#1A77B5`/"uplift" outside this archive directory; the new diverging-map
pointer resolves to a real table; the IV row in the Presentation Order table now matches a real
section; all edited Python blocks in `data-visualization.md` parse cleanly; `swd_style.py` parses
cleanly. Round 4 (T19-T23 + the uplift fix) is closed.

---
