# Round 3, Phase 2 — member_code Cross-Critique

Reviewed `round3_1_member_color.md` and `round3_1_member_standards.md` against my own
`round3_1_member_code.md`. Five points resolved below; all claims re-checked directly against
current on-disk files/code, not taken on the other members' word.

---

## 1. T11 structural fix — flatten color-palettes.md's safe section to a table keyed to `color_palettes.py`

**Workable, agree.** Confirmed the root cause member_color diagnosed: `color-palettes.md`'s
"Colorblind-Safe Diverging Maps" (lines 136–153) is three hand-written `###` subsections with
prose blurbs, while `color_palettes.py`'s `DIVERGING_COLORMAPS_SAFE` (lines 68–75) is a flat
6-item list. Prose-vs-list is exactly the shape mismatch that makes silent drift cheap: extending
the code list is a one-line diff, extending the doc requires someone to notice and author a new
paragraph, and nothing forces that second step. A table with one row per colormap (name / one-line
note / code snippet) collapses the doc to the same shape as the list it mirrors, so "does the doc
match the code" becomes a row-count-and-name check instead of a full read.

From the code lens specifically, two refinements to make it stick, since this repo has zero test
infra (no `tests/`, no CI workflow, no assertion scripts anywhere — I checked) so nothing can
mechanically enforce equality:

- **Bidirectional pointer comments**, not just the table. Add a one-line comment directly above
  `DIVERGING_COLORMAPS_SAFE` in `color_palettes.py`: `# Mirrored in
  references/color-palettes.md's "Colorblind-Safe Diverging Maps" table — keep both in sync.` And
  a matching line at the top of the doc's table: `<!-- Source of truth: assets/color_palettes.py,
  DIVERGING_COLORMAPS_SAFE -->`. This is cheap (two lines, zero maintenance cost) and means an
  editor who opens *either* file via grep for the colormap name lands on a note telling them the
  other file exists, which a bare table alone doesn't guarantee — the drift here happened because
  nobody re-opened the doc when the code list grew, not because the doc's format was hard to edit.
- Since there's no CI to enforce this, don't oversell it as "prevented" — it's now *cheap to
  check* and *discoverable*, not automatically synced. I'd stop short of proposing a standalone
  sync-check script; this skill has no Python test runner anywhere, and a one-off script nobody
  runs is worse than no script (false confidence). The table + pointer comments is the right-sized
  fix for a docs-only repo with no build step.

No better mechanical safeguard than what member_color already proposed, from my lens — I'd just
add the pointer comments as a supplement, not a replacement.

---

## 2. T13 reconciliation wording (narrow the ban to "not for precise value reading," cross-reference both files)

**Agree with the direction.** No code stake either way — this is prose-only in
`pre-attentive-attributes.md` and `chart-selection.md`, neither of which contains executable code,
so I have no correctness objection. I'll note two things from a consistency-with-my-own-T13-fix
angle:

- My own round-1 proposed fix only edited `pre-attentive-attributes.md` (softening line 44 to
  point at `chart-selection.md`). member_color's and member_standards's converged proposal edits
  **both** files (narrows `chart-selection.md`'s table row *and* adds the cross-reference sentence
  in `pre-attentive-attributes.md`). Theirs is the more complete fix — a one-directional pointer
  still leaves a reader who opens `chart-selection.md` first hitting a blanket "NEVER" with no
  signal that a qualified exception exists elsewhere. I'm dropping my narrower version in favor of
  their two-file edit.
- Both members independently landed on near-identical replacement text for the `chart-selection.md`
  row (scope the ban to "as a precise encoding" / "exact-value comparison," keep "scatter + color"
  as the fallback for the categorical case, add "direct value labels" as the fallback for the
  coarse/ordinal case). I have no objection to that exact wording — it preserves the table's
  existing columns/format, which matters here since `chart-selection.md`'s whole value is being a
  fast-scan reference table; a longer caveat paragraph would break that.

Agree, no changes requested.

---

## 3. T16 — add a "Goal: Paper/Journal Figure" section rather than removing the decision-tree path

**Agree, and I'm adopting member_standards's specific placement over my own round-1 proposal.**
Re-checked `SKILL.md` directly this pass: decision tree (lines 38–47) lists the paths in this
order — EDA, **paper/journal**, slide/presentation, credit-risk routing — but the `## Goal`
headers only exist for `## Goal 1: EDA & Exploration` (line 98) and `## Goal 2: Business
Presentation` (line 120), in that order, with nothing for paper/journal in between. My own round-1
fix proposed renaming the existing "Color and Statistical-Honesty Reference" section (line 154) to
"Goal 3" — that resolves the missing-landing-page problem but leaves the Goal numbering (1, 2, 3 =
EDA, Business Presentation, paper/journal-via-color-ref) out of step with the decision tree's own
listed order (EDA, paper/journal, slide/presentation). member_standards's fix — insert a new
`## Goal 2: Paper / Journal Figure` between the current Goal 1 and Goal 2, renumbering the
existing Goal 2 (Business Presentation) to Goal 3 — fixes both problems in one edit and costs
nothing extra. I'm switching to their placement.

Agree, 5 reference files (`data-visualization.md`, `matplotlib-examples.md`, `color-palettes.md`,
`publication-guidelines.md`, `style-guide.md`) are still on disk and already scoped for this path,
so removing the decision-tree leaf would be the worse structural gap, not the fix.

---

## 4. Validating member_standards's two new findings

**Finding A — `model-evaluation-viz.md` decision-tree label too narrow. CONFIRMED, exactly as described.**

Ran `grep -n "^##" references/model-evaluation-viz.md` directly:

```
8:   ## 1. ROC Curve
32:  ## 2. Precision-Recall Curve
54:  ## 3. Calibration Plot — Reliability Diagram
78:  ## 4. Confusion Matrix
98:  ## 5. Feature Importance — Global
119: ## 6. SHAP Waterfall — Individual Prediction Explanation
144: ## 7. Lift / Gain Chart
166: ## 8. KS Curve
198: ## 9. PSI Stability Chart
231: ## Audience Guide for Model Charts
```

9 numbered sections; only #8 (KS Curve) and #9 (PSI Stability) are credit/collections-specific by
convention — the other 7 (ROC, PR, Calibration, Confusion Matrix, Feature Importance, SHAP
Waterfall, Lift/Gain) are generic binary-classifier evaluation with no credit-risk dependency.
`SKILL.md` line 47's decision-tree leaf reads `└─ Credit-risk model chart (KS curve, PSI
stability) → references/model-evaluation-viz.md` — narrower than the file it routes to. Confirmed
the 7-of-9 count precisely; also confirmed `SKILL.md` line 208's Resources-list description
(`model-evaluation-viz.md — ROC, PR, calibration, confusion-matrix, KS, PSI charts`) is already
generic and accurate, so the fix is isolated to the one decision-tree line, matching member_standards's
proposed fix.

**Finding B — `chart-selection.md`'s own decision tree missing a Slope Chart leaf. CONFIRMED.**

`chart-selection.md`'s top-of-file decision tree (lines 5–34, read directly):

```
├── Change over time?
│   ├── Few time points (< 6) → Bar chart (vertical)
│   ├── Many time points      → Line chart
│   └── Cumulative change     → Area chart (filled)
```

Three leaves under "Change over time?" — none for exactly two points. `grep -n "Slope Chart"
references/chart-selection.md` confirms a full dedicated section exists at line 105 (`### Slope
Chart — Change Between Two Points`) with its own required-inputs/rules content. Same defect
pattern as T16 (decision tree not routing to content the file commits to), contained to one file.
Confirmed exactly as described; agree it's a one-line fix and low priority relative to T16/T13.

---

## 5. My own T18 — RETRACTED. `label_bars`'s orientation auto-detection actually works; my round-1 claim was wrong.

I re-verified this empirically this round rather than re-asserting the round-1 claim, and my
original finding does **not** hold up.

Round-1 T18 claimed `getattr(bars, 'orientation', None)` always falls through to `None` because
"matplotlib's `BarContainer` does not... have a public `.orientation` attribute at all." I did not
actually run this against a live matplotlib in round 1 — I reasoned from general knowledge, which
was wrong. This round I ran it directly:

```
$ python3 -c "
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
b = ax.bar([1,2],[1,2])
print('bar orientation:', repr(b.orientation))
bh = ax.barh([1,2],[1,2])
print('barh orientation:', repr(bh.orientation))
"
bar orientation: 'vertical'
barh orientation: 'horizontal'
```

Confirmed via `matplotlib.container.BarContainer.__init__` source (installed version 3.10.8):
`orientation` is a real constructor parameter/attribute, and `Axes.bar`/`Axes.barh` populate it
correctly (`'vertical'` / `'horizontal'` respectively) — this has been true since the attribute was
added to `BarContainer` (matplotlib 3.7, Feb 2023), well before any version a project starting
today would install. I also grepped this repo for a pinned matplotlib version
(`requirements*.txt`, `pyproject.toml`, `*.cfg`, `*.yml`) and found none — nothing in the skill
constrains it to a pre-3.7 matplotlib where the old behavior might apply.

**Conclusion: `label_bars`'s docstring claim ("Works for both vertical (`ax.bar`) and horizontal
(`ax.barh`) BarContainers") is accurate, and `orientation = orientation or getattr(bars,
'orientation', None)` (line 210) does correctly auto-detect in practice** — a caller who omits
`orientation=` and passes the container straight from `ax.bar()`/`ax.barh()` gets the right branch
without hitting the `ValueError` on line 212. That `ValueError` only fires for genuinely malformed
input (e.g., a caller passing something that isn't a `BarContainer` at all, or an
`orientation=` string that isn't one of the two valid values) — which is correct, intended guard
behavior, not a docstring/code mismatch.

**No fix needed. T18 should be dropped from the findings list, not carried forward with a fix
recommendation.** This is a case where the right outcome of cross-checking is retracting my own
finding rather than picking one of the two fix directions I originally offered (fix code vs. fix
docstring) — both would have been solving a problem that doesn't exist. Flagging this prominently
for the chairman since T18 was in my own round-1 writeup and I want the retraction on record before
any fix gets applied against a correct docstring.

(T19, also mine, remains as filed in round 1 — verified clean, no defect, no action — unaffected
by this correction.)
