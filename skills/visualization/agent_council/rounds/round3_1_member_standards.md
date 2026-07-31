# Round 3 — member_standards (STANDARDS & CROSS-FILE CONSISTENCY)

Independent investigation of T11–T16, plus a fresh consistency sweep across every file
currently on disk in `skills/visualization/`. Investigation only — no files edited.

---

## T13 — Bubble charts: endorsed vs. banned (my domain — deep dive)

**Confirmed real.** Exact passages:

- `references/pre-attentive-attributes.md:44`, under "Size":
  `**Use cases:** Bubble charts, dot plots where a third dimension is encoded in size.`
  — immediately followed by its own caveat, line 46: `**Rule:** Size is hard to decode
  precisely. Use it for categorical importance, not for exact values.`
- `references/chart-selection.md:130`, "What to NEVER Use" table:
  `| Bubble chart (3 vars) | Size is hard to decode | Scatter + color |`

Both files are on the KEEP list from the Round-2 execution pass and both were marked "clean,
no changes needed" — but that pass only checked for dangling references to deleted files, not
substantive cross-file agreement, so this slipped through.

**Is the contradiction actually load-bearing, or do the two files just use different words for
the same idea?** I checked the reasoning, not just the verdict, in both files. They actually
*agree* on the underlying fact — "size is hard to decode precisely" appears almost verbatim in
both (`pre-attentive-attributes.md` line 46; `chart-selection.md` line 130's "Why" column). They
disagree only on the conclusion drawn from that shared fact: one treats it as "so use size only
for coarse/categorical importance," the other treats it as "so never use it, full stop, use
scatter+color instead." That's a real, first-encounter-breaking contradiction (an agent or human
reading one file has no reason to open the other), but it's a *policy* disagreement built on
*agreed* evidence, not two files that got the underlying fact wrong.

**Recommendation: reconcile, don't delete either side.** Scatter+color is a real replacement
only when the third variable is categorical (color can carry it) or when precision matters. It
is not a general replacement when the third variable is continuous and only coarse/relative
magnitude needs to register (the classic Gapminder wealth-bubble case) — color can't carry a
third continuous channel if color is already carrying a category, and turning it into a 4th
"color = magnitude tier" dimension reintroduces the same imprecision bubble size has, just in a
different channel. So:
- Keep `pre-attentive-attributes.md`'s Size entry, but tighten it to point at the caution
  explicitly: append a cross-reference sentence like "For a full chart (not just an isolated
  size cue), see chart-selection.md's caution against bubble charts as a default — prefer this
  only when the third variable is coarse/ordinal and the audience doesn't need precise reads."
- Soften `chart-selection.md`'s "NEVER Use" row from a blanket ban to a qualified one, e.g.
  `Bubble chart (3 vars) as a precise encoding | Size is hard to decode precisely | Scatter +
  color for categorical 3rd var; bubble only for coarse/ordinal magnitude with direct value
  labels`. This keeps the table's "avoid by default" posture (which is the right default —
  bubble charts are genuinely overused and abused) while not flatly contradicting the file two
  clicks away that documents the one legitimate use case.
This is a two-line edit in each file, not a chapter rewrite, and it resolves the contradiction by
narrowing scope rather than picking a winner — both files' underlying claims are correct, only
their stated conclusions clashed.

---

## T14 — Wet-lab/genomics leftover example data

**Confirmed, and precisely located.** In `references/matplotlib-examples.md`, every one of the
4 kept examples carries molecular-biology flavor in variable names/units, not just incidentally
but as the example's entire framing:
- Example 1, line 37: `ax.set_ylabel('Fluorescence intensity (a.u.)')`
- Example 2, line 69: `gene_names = [f'Gene{i+1}' for i in range(n)]` used as tick labels on a
  generic random-correlation heatmap that has nothing to do with genes (the data is
  `np.random.randn` — the gene framing is pure decoration on top of arbitrary numbers)
- Example 3, line 103: `ax.set_ylabel('Concentration (μM)')`
- Example 4, lines 123, 139: `categories = ['WT', 'Mutant A', 'Mutant B']`,
  `ax.set_ylabel('Activity (% of WT control)')` — a knockout/mutant assay framing

In `references/publication-guidelines.md`, line 49: `**Heatmaps**: Matrix data, correlations,
**expression patterns**` — "expression patterns" is gene-expression-heatmap-specific language
inside an otherwise domain-neutral bullet list (bar/line/scatter/box/violin entries are all
generic).

**Is this actually a problem for a general DS skill, or harmless flavor?** I lean toward "worth
fixing, low urgency" rather than "must fix," and here's the reasoning: the *code* in every one of
these examples is fully domain-neutral and reusable as-is (error bars, SEM, colorbar-on-heatmap,
grouped-bar-with-CI — none of that logic is genomics-specific). Only the string literals
(axis labels, category names) carry the domain. Round 2 already established the precedent that
this project draws the line at *domain-irrelevant content*, not *domain-flavored variable names*
— it cut the `FLUOROPHORES_*`/`DNA_BASES*` dicts and the "Special Purpose Palettes" section
because those were substantively about microscopy/genomics (real palette-selection logic tied to
a domain this skill doesn't serve), not because a chart example happened to say "gene" in a tick
label. That said, the file's own header claims "ML/DS-generic" framing implicitly (it's the
skill-wide default matplotlib reference, cited from `SKILL.md`'s "Color and Statistical-Honesty
Reference" for *ML-paper* figures), and four-for-four wet-lab-flavored examples reads as more
than coincidence — it suggests the file was drafted from (or copy-adapted from) a biology-skill
source and never re-themed. My recommendation: low-cost regenericize (swap `gene_names` →
`feature_names`, `Fluorescence intensity (a.u.)` → `Signal (a.u.)` or a metric a DS reader
recognizes, `WT/Mutant A/Mutant B` → `Baseline/Variant A/Variant B`, `Concentration (μM)` →
`Metric value`, and `expression patterns` → `feature correlations` or drop the phrase) — this is
a find-and-replace on string literals, zero risk to the code logic, and removes a distraction
that costs nothing to fix. Not a blocking issue if the chairman prefers to leave it (the code
itself teaches the right lesson regardless of what the y-axis says), but I'd rate it above "pure
bikeshedding" because the redirect's own message-delivery lens is about *examples reading as
directly applicable to the reader's job* — a DS reader hesitates for a beat on "why is this
skill's matplotlib reference showing me knockout-mutant assay data," which is exactly the kind of
friction the skill's own Design principles / Affordance section (`design-principles.md` line 78:
"if a viewer needs to study... for more than 5 seconds... affordance has failed") would flag if
applied reflexively to itself.

---

## T16 — SKILL.md's dangling "paper/journal" decision-tree path

**Confirmed via a full re-read of the current `SKILL.md`.** The structure is:
- Library Decision Tree (lines 38–48) names 4 destinations: EDA, "Static figure for a paper /
  journal," "Slide / presentation for stakeholders," and credit-risk domain routing.
- `## Goal 1: EDA & Exploration` (line 98) — full worked section: primary tool, code sample,
  fallback chain, in-scope caveat.
- `## Goal 2: Business Presentation` (line 120) — same treatment for the slide/stakeholder path.
- No `## Goal` section exists for the paper/journal path. The only landing spot is `## Color and
  Statistical-Honesty Reference (matplotlib figures)` (line 154), which is framed purely as a
  color/encoding pointer ("Colorblind-safe palette choice... showing uncertainty honestly...") —
  it never states "matplotlib/seaborn primary, here's a starting code sample," the way Goal 1 and
  Goal 2 do for their respective paths.

**Recommendation: add a short Goal section, don't remove the decision-tree path.** Two reasons
this is the smaller, more consistent fix rather than deleting the path:
1. The content this path would point to already exists and is already scoped correctly post-prune
   — `data-visualization.md`, `matplotlib-examples.md`, `color-palettes.md`,
   `publication-guidelines.md`, and `style-guide.md` are all still on disk specifically because
   Round 2's redirect judged their *chart-type/encoding choice logic* (not their
   venue-formatting mechanics) to be in-scope message-delivery content for exactly this use case
   — a static figure destined for a paper. Removing the decision-tree path would leave five kept
   reference files with no entry point from the goal-based navigation structure at all, which is
   a worse structural gap than the one T16 identifies.
2. The fix is genuinely small: a paper/journal Goal doesn't need Goal 2's level of code (the
   redirect explicitly cut DPI/venue-sizing/font mechanics, and rightly so — "check your target
   venue's author guidelines directly" is already the file's own stated policy, see
   `publication-guidelines.md` line 3). It needs 4–6 lines: primary tool (matplotlib/seaborn,
   same as the decision tree already says), one line on when plotnine is acceptable (grammar fit,
   mirroring the decision tree's own sub-bullet), and a direct pointer to the "Color and
   Statistical-Honesty Reference" section for the actual chart-pattern/color/uncertainty content
   that already exists. This is proportionate to how thin Goal 1 and Goal 2 already are — neither
   is a tutorial, both are a paragraph plus a code snippet plus pointers.

Concretely: insert a `## Goal 2: Paper / Journal Figure` between the current Goal 1 and Goal 2,
renumbering the current Goal 2 (Business Presentation) to Goal 3. This also makes the Goal
numbering match the decision tree's own listed order (EDA → paper/journal → slide/presentation),
which it currently does not (decision tree lists paper/journal second, but there is no Goal 2 for
it — the existing Goal 2 is the *third* item in the decision tree). Renumbering closes that
secondary inconsistency for free.

---

## T11, T12, T15 — brief weigh-in

**T11 (diverging-safe list drift, doc vs. code)** — Confirmed, and it's squarely in my lane
(doc/code consistency, the same failure mode as the original T2). `references/color-palettes.md`
"Colorblind-Safe Diverging Maps" (lines 136–153) lists only RdYlBu, PuOr, BrBG. `assets/
color_palettes.py`'s `DIVERGING_COLORMAPS_SAFE` (lines 68–75) has six: RdYlBu, RdBu, PuOr, BrBG,
PRGn, PiYG — all verified per the code file's own comment (line 65-67, `RColorBrewer::
brewer.pal.info`'s `colorblindlist`). This is a straightforward reconciliation, not a
disagreement to adjudicate: the doc under-lists relative to its own backing code. Recommend
literally copying the code's 6-item list into the doc's "Colorblind-Safe Diverging Maps" section
(add RdBu, PRGn, PiYG entries in the same style as the existing three), since the code asset is
the one that carries the citation/verification trail.

**T12 (unvetted `coolwarm`)** — Confirmed via grep across the whole skill: `coolwarm` appears
in exactly one place, `references/style-guide.md:39`, nowhere else. Every other correlation-matrix
example in the skill (`data-visualization.md:30`, `data-visualization.md:137`,
`matplotlib-examples.md:64`) uses `RdBu_r`, which *is* on the verified-safe list (T11's own list).
`pre-attentive-attributes.md:37` also uses `RdBu` as its example diverging map. Recommend the
simplest possible fix: replace `coolwarm` → `RdBu_r` in `style-guide.md`'s Gradient Schemes table.
This is a one-cell table edit that simultaneously resolves the cross-file inconsistency (matches
what every other file already does) and the unvetted-colormap problem (RdBu_r is already
verified) — no need to go research `coolwarm`'s CVD status separately when the rest of the skill
already has a working, verified answer sitting right next to it.

**T15 (unguarded list indexing)** — Confirmed as a real, reproducible bug, though it's a code-
correctness issue more than a cross-file consistency one. `data-visualization.md`'s
`plot_training_curves` (line 50: `color=OKABE_ITO_LIST[i]`), `plot_ablation` (line 98:
`color=OKABE_ITO_LIST[i]`), and `plot_distributions` (line 243:
`pc.set_facecolor(OKABE_ITO_LIST[i])`) all index an 8-element list by an unbounded loop variable.
Worth noting for consistency purposes: `plot_training_curves` sits three lines above its own
correct pattern (`markers[i % len(markers)]`, line 52) — so the fix isn't inventing a new
convention, it's applying one this same function already uses one line away. Recommend
`OKABE_ITO_LIST[i % len(OKABE_ITO_LIST)]` in all three call sites.

---

## Fresh consistency sweep — additional findings

I read every remaining file not covered by T11–T16 in full (`audience-adaptation.md`,
`causal-inference-charts.md`, `clutter-elimination.md`, `context-setting.md`,
`design-principles.md`, `grammar-of-graphics.md`, `narrative-structure.md`,
`model-evaluation-viz.md`, `swd_style.py`) specifically hunting for T13-style contradictions.
Cross-checked color constants (`SWD.ACCENT_POSITIVE`/`ACCENT_NEGATIVE` in `swd_style.py` vs. the
"Negative: coral/vermillion / Positive: blue" prose in `pre-attentive-attributes.md`'s Gray
Palette Strategy, vs. `publication-guidelines.md`'s `OURS`/`BASELINE` two-color scheme) — all
consistent, no drift found there. Two new (smaller) findings:

### New finding A — `model-evaluation-viz.md`'s decision-tree label is narrower than its actual scope
`SKILL.md`'s decision tree (line 47) routes to this file only under **"Credit-risk model chart
(KS curve, PSI stability)."** But the file itself (`references/model-evaluation-viz.md`) covers 9
sections, 7 of which are generic binary-classifier evaluation with no credit-risk dependency at
all: ROC Curve, Precision-Recall, Calibration Plot, Confusion Matrix, Feature Importance (SHAP),
SHAP Waterfall, Lift/Gain Chart — only KS Curve and PSI Stability are credit/collections-specific
by convention. `SKILL.md`'s own Resources section (line 208) describes the same file accurately
and generically: `model-evaluation-viz.md — ROC, PR, calibration, confusion-matrix, KS, PSI
charts` — no "credit-risk" qualifier there. So the file is self-consistent, and the Resources
list is accurate, but the decision tree's *only* entry point to it is mislabeled narrowly. A
reader building an ROC curve or confusion matrix for a fraud or churn model (not credit) has no
decision-tree path to this file at all — they'd have to already know it exists and read the
Resources list at the bottom. Recommend widening the decision-tree line, e.g. `└─ Binary
classifier evaluation chart (ROC, PR, calibration, confusion matrix, KS, PSI) →
references/model-evaluation-viz.md`, dropping "Credit-risk" as the sole framing (KS/PSI's
credit-specific convention is already explained inside the file itself, in each section's "Use
when" / "Standard in..." language — the decision tree doesn't need to duplicate that nuance to
route correctly).

### New finding B — `chart-selection.md`'s own decision tree omits its own Slope Chart section
`chart-selection.md`'s top-of-file ASCII decision tree (lines 5–34) branches "Change over time?"
into three leaves (few time points → bar, many time points → line, cumulative → area) but has no
leaf for "change between exactly two time points," even though the file has a full dedicated
`### Slope Chart — Change Between Two Points` section (line 105) with required inputs and rules,
and it's cited approvingly elsewhere (`design-principles.md` line 53 references slope charts by
name). This is a smaller, single-file version of the same defect class as T16 (a decision tree
that doesn't route to content the file itself commits to) — worth a one-line addition to the
tree, e.g. a fourth leaf under "Change over time?": `└─ Exactly two points → Slope chart`. Lower
priority than T16 since it's contained within one file rather than spanning the skill, but it's
the same bug pattern and cheap to fix in the same pass if the chairman is already touching
`chart-selection.md` for T13.

No other T13-class contradictions (two files giving opposite prescriptive verdicts on the same
named chart/technique) turned up in this pass. The skill's color-constant story in particular
holds together end-to-end now (Okabe-Ito hex values, positive/negative pair, ours/baseline pair,
gray-scale hierarchy all match verbatim across `pre-attentive-attributes.md`,
`design-principles.md`, `swd_style.py`, `color-palettes.md`, `color_palettes.py`, and
`publication-guidelines.md`), which is worth noting as a place the T7 fix genuinely stuck.
