# Round 3, Phase 1 — member_color (Color Science & Accessibility lens)

Independent investigation of T11–T16. Files read in current on-disk state:
`references/color-palettes.md`, `assets/color_palettes.py`, `references/style-guide.md`,
`references/data-visualization.md`, `references/matplotlib-examples.md`,
`references/pre-attentive-attributes.md`, `references/chart-selection.md`,
`references/publication-guidelines.md`, `SKILL.md`.

---

## T11 — Diverging "safe" list drift (doc vs. code) — CONFIRMED, and it is a repeat of my own Round 2 fix

Verified exact current state:

- `assets/color_palettes.py` `DIVERGING_COLORMAPS_SAFE` (lines 68–75): **six** maps —
  `RdYlBu`, `RdBu`, `PuOr`, `BrBG`, `PRGn`, `PiYG` — with a comment citing
  `RColorBrewer::brewer.pal.info`'s `colorblindlist` as the verification source (this is the
  Round 2 fix I did).
- `references/color-palettes.md` "Colorblind-Safe Diverging Maps" (lines 136–153): only **three**
  subsections — RdYlBu, PuOr, BrBG. `RdBu`, `PRGn`, `PiYG` are absent from the prose entirely
  (not even mentioned in the "Avoid" list — they're just missing).

This is a real regression of the exact class of bug T2 fixed, and it happened for a boring
reason: the doc's "Safe" section is written as three hand-authored subsections with prose blurbs
("Excellent for colorblind viewers," "Good colorblind accessibility"), so extending the code list
to six required someone to also hand-write three new blurbs in the doc — and that step was
skipped when the code list was extended. The two lists have no mechanical link; nothing enforces
they agree.

**Proposed fix (this round should implement, not just re-sync the numbers):** the three-way
duplication (hex/name list in `color-palettes.md`, `OKABE_ITO`/`WONG` dicts in
`color-palettes.md`, `DIVERGING_COLORMAPS_SAFE`/`AVOID` in `color_palettes.py`) has no single
source of truth. Two options that actually prevent recurrence, not just fix the count:
1. **Make the code the source of truth and the doc a generated/mechanical mirror.** Replace the
   doc's three hand-written subsections with a table generated from (or asserted equal to)
   `DIVERGING_COLORMAPS_SAFE`/`AVOID`, and add one line to the doc instructing future editors:
   "this table must list exactly the names in `color_palettes.py`'s `DIVERGING_COLORMAPS_SAFE`;
   do not add prose blurbs per-map, add a plain table row." A table is far cheaper to keep in
   sync than paragraph blurbs, which is what invited the drift.
2. **Add a CI-independent sanity check**: since this skill has no test runner, the practical
   version of "prevent this class of drift" is a standing instruction at the top of both files —
   "SAFE/AVOID names in this file MUST match `assets/color_palettes.py`'s
   `DIVERGING_COLORMAPS_SAFE`/`DIVERGING_COLORMAPS_AVOID` exactly — if you edit one, edit both in
   the same change" — plus converting the doc list to the flat table form in (1) so verifying
   equality is a 5-second visual diff, not a paragraph-by-paragraph read.
I recommend (1): flatten the doc to a table keyed 1:1 to the code list. Prose blurbs are exactly
what made this expensive to maintain and easy to silently omit from.

**Verdict: CONFIRMED bug, T2-class regression. Fix by flattening the doc list to a table mirroring the code list, plus an explicit sync instruction — not just adding the three missing rows.**

---

## T12 — `coolwarm` for correlation matrices — CONFIRMED inconsistency; coolwarm itself is defensible but unverified by this skill's own standard

**Cross-file check confirmed:** `style-guide.md` line 39 recommends `cmap="coolwarm"` for
"Correlation matrix." `data-visualization.md` line 30 and line 137, and
`matplotlib-examples.md` lines 63–64, all use `RdBu_r` for correlation heatmaps with explicit
"centered at 0" reasoning. Three-out-of-four loci agree on `RdBu_r`; one disagrees.

**Is coolwarm actually colorblind-safe?** Yes, per its original design source, with a caveat:

- Kenneth Moreland's 2009 paper "Diverging Color Maps for Scientific Visualization" (the map's
  origin, and matplotlib's own attribution for `coolwarm`) states the design explicitly targets
  colorblind viewers: it "behaves well for observers with color-deficient vision" — this is a
  legitimate, citable, non-fabricated primary source, not marketing copy.
- However, `coolwarm` is a matplotlib-native map, not a ColorBrewer scheme, so it was never
  run through *this skill's own established verification methodology* — Round 2 explicitly
  verified `RdYlBu`/`RdBu`/`PuOr`/`BrBG`/`PRGn`/`PiYG` against
  `RColorBrewer::brewer.pal.info`'s `colorblindlist`. `coolwarm` has no entry there because it
  isn't a ColorBrewer palette, so it fails the skill's own bar even though it isn't actually
  unsafe.
- Separate, real weakness: matplotlib's own "Choosing Colormaps" documentation notes `coolwarm`
  "has little range of gray scale and would print to a more uniform plot, losing a lot of
  detail" — i.e., it's weak on the *grayscale-compatibility* axis, which is a rule
  `color-palettes.md` itself states elsewhere ("All figures should remain interpretable in
  grayscale"). `RdBu` (ColorBrewer) is explicitly tested and flagged print/photocopy-friendly on
  colorbrewer2.org, which `coolwarm` has never been checked against.

**Ruling:** `coolwarm` is not a fabricated or reckless recommendation — it has a real,
CVD-focused design pedigree — but it (a) is inconsistent with the rest of the skill's own
practice, (b) was never verified against this skill's chosen verification source
(ColorBrewer's colorblindlist), and (c) has a documented grayscale weakness the skill's own rules
care about. **Standardize on `RdBu_r` in `style-guide.md`'s Gradient Schemes table** to match the
other three loci and to stay inside the skill's one consistent verification methodology, rather
than trying to separately verify and carry a second, weaker-on-grayscale diverging map for the
same use case. If `coolwarm` is kept anywhere (e.g., because a reader specifically wants
matplotlib's default diverging map), it should cite Moreland (2009) by name next to it, not be
presented as interchangeable with `RdBu_r` on no citation at all, as it currently is.

Sources: Moreland, K. (2009), "Diverging Color Maps for Scientific Visualization,"
https://www.kennethmoreland.com/color-maps/ColorMaps.pdf ; matplotlib "Choosing Colormaps in
Matplotlib" user guide (grayscale-range note on coolwarm),
https://matplotlib.org/stable/users/explain/colors/colormaps.html

**Verdict: CONFIRMED inconsistency. Fix: change `style-guide.md`'s Gradient Schemes row to `RdBu_r` to match the rest of the skill. coolwarm is legitimate but redundant and weaker-on-grayscale; don't keep it as a second unverified-by-this-skill's-method option for the identical use case.**

---

## T13 — Bubble chart: endorsed vs. banned — CONFIRMED contradiction; both files are locally correct, the resolution is scoping, not picking a winner

Verified text:
- `pre-attentive-attributes.md` "Size" section: "Bubble charts, dot plots where a third dimension
  is encoded in size" listed as the **use case** for the Size attribute, immediately followed by
  its own caveat: "Size is hard to decode precisely. Use it for categorical importance, not for
  exact values."
- `chart-selection.md` "What to NEVER Use" table: "Bubble chart (3 vars) | Size is hard to decode
  | Scatter + color."

Notice both files use the **identical phrase** "size is hard to decode" — they agree on the
underlying perceptual fact (this is well-established: Cleveland & McGill 1984 rank area/size
low on the perceptual-accuracy hierarchy, well below position and length) — they disagree on the
**prescription** that follows from it. `pre-attentive-attributes.md` says: use size, but only for
coarse/categorical signal, not precise values. `chart-selection.md` says: never use it, full
stop, replace with color encoding instead.

**My perceptual-accuracy ruling:** `chart-selection.md`'s blanket "NEVER" is the overcorrection
here, not `pre-attentive-attributes.md`'s more qualified guidance. Size/area encoding for a third
variable is standard, well-studied practice (bubble charts are a named, legitimate chart type in
Cleveland's own work and in Few/Knaflic's storytelling-with-data literature) — the actual
perceptual finding is not "never use size," it's "size supports ranking/rough-magnitude judgments
but not precise value reading," which is exactly what `pre-attentive-attributes.md` already says.
Banning bubble charts outright and replacing them with "scatter + color" is not even a like-for-
like substitute: color encodes a *categorical or a second continuous* variable differently than
size encodes *magnitude* — swapping size for color changes what perceptual question the chart can
answer (color doesn't intuitively map to "how big," size does), so the prescribed replacement
doesn't preserve the original chart's message-delivery purpose.

**Resolution:** don't delete either position; make `chart-selection.md`'s entry match
`pre-attentive-attributes.md`'s actual rule instead of blanket-banning. Recommended fix: change
the "NEVER Use" table row to something like "Bubble chart for exact-value comparison | Size is
hard to decode precisely for exact values | Scatter + color, or add direct value labels on the
bubbles" — i.e., scope the ban to precise-value tasks, not to the chart type itself, matching
`pre-attentive-attributes.md`'s framing verbatim. This is the general fix pattern for T13: it's
not "which file is wrong," it's "chart-selection.md's table format (blanket type → blanket ban)
can't represent a conditional rule that pre-attentive-attributes.md already states correctly,"
so the table entry needs to gain the same condition, not flip to agree with one side wholesale.

**Verdict: CONFIRMED contradiction. `pre-attentive-attributes.md`'s qualified guidance (size for coarse/ranking signal, not exact values) is the perceptually correct position. `chart-selection.md`'s unqualified "NEVER" is the overcorrection and should be narrowed to match, not the other way around.**

---

## T14 — Wet-lab/genomics leftovers — brief, low priority from my lens

Confirmed present: `matplotlib-examples.md` uses "Fluorescence intensity (a.u.)," `gene_names`,
"Concentration (μM)," "WT / Mutant A / Mutant B," "Activity (% of WT control)" throughout its 4
surviving examples; `publication-guidelines.md` line 49 lists "expression patterns" as a heatmap
use case. From a color/accessibility lens specifically this has no functional bug — none of these
labels affect palette choice or CVD-safety — it's purely a domain-genericism/consistency issue
(same category as the Round 2 genomics-dict pruning in `color_palettes.py`/`color-palettes.md`,
just missed in the sibling file). I'd defer to member_standards/chairman on whether to
re-genericize the example data; low priority, no accessibility stake.

---

## T15 — Unguarded `OKABE_ITO_LIST[i]` indexing — not my primary lens, but flagging the accessibility angle

This is fundamentally a code-correctness bug (member_code's territory), but it has one
accessibility-adjacent wrinkle worth noting: the fix must not silently wrap past 8 series with
`% len(OKABE_ITO_LIST)`, because the whole point of Okabe-Ito is that all 8 colors are mutually
distinguishable under CVD — reusing colors 0 and 8 for two different series on the *same chart*
via modulo wrap reintroduces an ambiguous-categories problem (two different series rendered in
the identical color), which is arguably worse than crashing. If the fix is a `% len(...)` wrap
(matching the existing `markers[i % len(markers)]` pattern one line above in
`plot_training_curves`), the doc/docstring should say plainly "supports up to 8 distinguishable
series; beyond that, colors repeat and additional encoding (marker shape, direct labeling) is
required to keep series distinguishable" — don't let the wrap read as "handles any number of
series safely."

**Verdict: defer primary fix to member_code; my addition — if the fix is a modulo wrap, it must come with an explicit "colors repeat past N=8, add markers/direct labels" caveat, not a silent wrap that reintroduces color-only ambiguity.**

---

## T16 — Missing "paper/journal" Goal section — no color/accessibility stake, no objection

Confirmed: decision tree line 42 names "Static figure for a paper / journal → matplotlib /
seaborn" with no matching `## Goal` section (only Goal 1: EDA, Goal 2: Business Presentation
exist; the paper/journal path lands only via the "Color and Statistical-Honesty Reference"
pointer at line 154). This is a structural/navigability issue, not a color-science issue. No
objection to whatever fix the group lands on (e.g., a short "Goal 2.5" or renumbered "Goal 3:
Paper/Journal Figure" pointer section) — just note that if such a section is added, it should
point to `color-palettes.md` for palette choice and NOT reintroduce a competing color
recommendation inline (i.e., don't let a new Goal section accidentally create a fourth place that
could drift out of sync the way T11/T12 already did).

---

## New topics found

None beyond T11–T16 from this lens — no new color/accessibility-specific issues surfaced during
this pass that aren't already captured above. One reinforcement worth flagging to the chairman:
T11 and T12 are the same underlying failure mode (a prose/table doc file drifting out of sync
with a sibling source of truth, be it code or another doc) appearing twice in one round. If only
one of the two gets a structural fix (table-ification / explicit sync instruction) and the other
just gets its numbers patched, expect a T11/T12-shaped bug to resurface in Round 4.
