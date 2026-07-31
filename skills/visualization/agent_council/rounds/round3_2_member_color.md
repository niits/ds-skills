# Round 3, Phase 2 — member_color (cross-critique response)

Read `round3_1_member_color.md` (own), `round3_1_member_code.md`, `round3_1_member_standards.md`.
Responding to the four resolution points from the chairman.

---

## 1. `plot_stacked_bar`'s 4th `OKABE_ITO_LIST[i]` instance — is silent color-repeat past 8 an accessibility issue worth flagging in-code?

**Yes — same recommendation I made for the original three instances now explicitly extends to
this fourth one, and I want to sharpen it rather than soften it now that it's confirmed skill-wide.**

member_code's trace (`data-visualization.md` line 266: `colors = colors or OKABE_ITO_LIST`, line
281: `colors[i]`) shows this call site defaults to the *same* 8-entry Okabe-Ito list as the other
three. My round-3.1 caveat therefore applies without modification: `% len(colors)` is the right
crash-avoidance fix, but a silent wrap is not accessibility-neutral — it re-introduces the exact
failure Okabe-Ito exists to prevent (two visually identical colors standing for two different
data series on the same chart), which is arguably worse for a colorblind reader than an
`IndexError`, because a crash is loud and a color collision is silent and misleading.

On "is 8 categorical series already beyond reasonable chart practice, making this a non-issue" —
**no, I don't think that escape hatch holds for this specific call site**, and I want to flag why
it's actually weaker here than for the line/bar/violin call sites:

- For `plot_training_curves`/`plot_ablation`/`plot_distributions`, 8 lines/bars/violins on one
  axis is already visually crowded, so "you're past reasonable chart practice" is a fair reason
  to treat wraparound as an edge case nobody should hit in practice.
- For `plot_stacked_bar`, the loop variable `i` indexes **segments within a single bar**, not
  top-level series. Stacked bars routinely carry more segments than a line chart carries lines
  (e.g., a churn-reason breakdown, a funnel-stage breakdown, a multi-category budget bar) — 8+
  segments in one stacked bar is a real, not hypothetical, use case, and segment adjacency makes
  color confusion *more* likely, not less, because segments are drawn touching each other with no
  intervening whitespace the way separate lines/violins have.

**Recommendation:** add a one-line comment/docstring caveat at all four sites (not just the three
originally named), worded uniformly: `"colors repeat past N=8 (or len(colors) if a custom list is
passed); for more categories, aggregate an 'Other' bucket or add direct segment labels/hatching to
keep segments distinguishable."` For `plot_stacked_bar` specifically I'd make this caveat slightly
more prominent than a trailing comment — e.g. in the function's docstring, since segment-count
overflow is the more plausible real-world trigger of the four call sites — but the fix pattern
(modulo wrap + explicit caveat, never a silent "handles any N" implication) should be identical
across all four for consistency.

---

## 2. T11 structural fix — code-generated doc vs. manually-synced table

**Confirming manually-synced flat table, not code-generated doc — this is the simpler option and
it is robust enough given this skill's actual constraints. I'm not asking for
`color_palettes.py`'s dict to carry canonical prose descriptions.**

Reasoning: "generate the doc from the dict" implies either (a) a build/lint step that runs
generation and fails CI on drift, or (b) an agent manually re-deriving the doc from the dict every
time either changes. This skill has no test runner and no CI (confirmed by all three of us across
rounds — the "practical version of a check" has consistently been "an explicit sync instruction,"
never an actual script). Given that reality, (a) is aspirational — there's no mechanism that would
ever execute the generation step, so specifying it doesn't prevent drift, it just adds a comment
claiming a workflow nobody runs. That's worse than doing nothing, because it's a false promise of
enforcement.

The flat table + explicit "these two lists must match, edit both together" instruction (my
round-3.1 option 1, which member_code and member_standards both independently converged on too)
is simpler to write, simpler to verify (a human or agent can eyeball-diff a 6-row table against a
6-item Python list in under 5 seconds — this was the whole point of flattening away the prose
blurbs), and doesn't require inventing tooling this skill doesn't have anywhere else. It's the
right amount of robustness for a markdown+python reference skill, not a software package.

**Final position: table in `color-palettes.md`, one row per `DIVERGING_COLORMAPS_SAFE` entry,
plus a one-line sync instruction in both files. No dict-level description strings in
`color_palettes.py`.**

---

## 3. T12 — coolwarm vs. RdBu_r, final call

**Final. Standardize on `RdBu_r` in `style-guide.md`'s Gradient Schemes table. No case for keeping
both as documented options for this skill.**

I considered the "coolwarm for continuous data, RdBu_r for something else" split before proposing
this in round 3.1, and it doesn't hold up: both maps are diverging colormaps designed for
data centered on a meaningful midpoint (correlation = 0, delta = 0) — that's the *only* use case
either one appears for anywhere in this skill (correlation matrices, in all four loci). There's no
second use case in any file where coolwarm's specific properties (matplotlib-native, decent hue
range, weak grayscale range) would be preferred over RdBu_r's (ColorBrewer-verified against
`RColorBrewer::brewer.pal.info`'s `colorblindlist`, explicitly flagged print/grayscale-friendly on
colorbrewer2.org). Keeping both "documented as options" for an identical use case just recreates
T11's exact failure mode — two lists that are supposed to be interchangeable but aren't
mechanically tied together, waiting to drift the next time someone edits one and not the other.

One coda, unchanged from round 3.1: if a reader specifically wants matplotlib's own default
diverging map for some reason outside this skill's scope, that's fine, but it shouldn't live in
this skill's tables presented as interchangeable with RdBu_r on zero citation. Cite Moreland
(2009) if it's kept anywhere at all. My recommendation remains: don't keep it anywhere in
`style-guide.md`; just replace the cell.

---

## 4. T13 final wording — reviewing member_standards' proposed table row

member_standards' proposed `chart-selection.md` row:
> `Bubble chart (3 vars) as a precise encoding | Size is hard to decode precisely | Scatter +
> color for categorical 3rd var; bubble only for coarse/ordinal magnitude with direct value
> labels`

**This is perceptually accurate and I'd ship it with one small addition, not a rewording.**

Checking it against the actual literature rather than just internal consistency: Cleveland &
McGill (1984)'s perceptual-accuracy ranking places position and length above angle/slope, which is
above area/volume, which is above color/density/saturation at the bottom. That ordering directly
supports both halves of the proposed sentence:
- "Scatter + color for categorical 3rd var" — correct pairing. Color is being asked to carry a
  *category*, not a magnitude, in this branch, which plays to color's actual perceptual strength
  (categorical discrimination) rather than its weakness (color is poor for ordered-magnitude
  judgments — a reader can't reliably rank five hues by "how much," which is exactly why nobody
  proposes color as a size replacement for a *continuous* third variable — matching
  member_standards' own T13 analysis in `round3_1_member_standards.md` about color not being a
  general substitute).
- "bubble only for coarse/ordinal magnitude" — correct scope-down. Area/size sits below position
  and length in Cleveland-McGill but is not at the bottom (color/hue is worse for ordered
  magnitude), so "usable for coarse/ordinal, not precise" is exactly where the literature places
  it — not "never," not "fully reliable," but "supports rank/rough-magnitude judgments." This
  matches my own round-3.1 ruling verbatim.
- "with direct value labels" — this is the one place I'd strengthen rather than reword: I'd make
  labeling **the compensating mechanism, not an optional add-on** — e.g. "bubble only for
  coarse/ordinal magnitude, and prefer direct value labels on the largest/smallest bubbles to
  cover the precision gap size can't close on its own." As written it reads as one item in a list
  of acceptable choices; the perceptual science says size *alone* is genuinely weak for exact
  values (Cleveland-McGill puts it well below position/length), so a reader following this rule
  should treat "add labels" as the default mitigation whenever precision matters at all, not a
  nice-to-have.

I'd also suggest citing Cleveland & McGill (1984) by name in the row or its surrounding prose,
the same way T12's fix should cite Moreland (2009) — both files currently assert "size is hard to
decode" as received wisdom with no citation anywhere in the skill; since we're already touching
this exact sentence for T13, it's a cheap add that upgrades an assertion into a sourced claim,
consistent with how T11/T12 already got citations from this round.

**Final position: member_standards' wording is substantively correct and matches the perceptual
science. Recommend one tightening (make direct labels the stated default mitigation, not a
trailing option) and one citation add (Cleveland & McGill 1984), not a different resolution.**
