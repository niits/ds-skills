# Round 3, Phase 2 — member_standards Cross-Critique Response

Responding to member_code (round3_1_member_code.md) and member_color (round3_1_member_color.md)
against my own round3_1 findings. No files edited.

---

## Point 1 — member_code's 4th OKABE_ITO_LIST instance (`plot_stacked_bar`) + new T18

**Scope change: yes, fold the 4th instance into T15's fix. Priority change: no.**

member_code traced `plot_stacked_bar` (`data-visualization.md` line 266:
`colors = colors or OKABE_ITO_LIST`, line 281: `color=colors[i]`) and found the identical unguarded-
index defect I named in T15 for the other three functions. This isn't a new bug class requiring
separate adjudication — it's the same root cause (unbounded loop index into a fixed-length list),
same fix (`colors[i % len(colors)]`), same file, same pass. I originally scoped T15 to three call
sites because I was working from the prior round's summary rather than a fresh full read of
`data-visualization.md`; member_code's independent full read caught what mine missed. I'm folding
it in: T15's fix set becomes four call sites, not three. This doesn't change T15's priority — it
was already "confirmed, real, fix in the same pass" — it just makes the fix complete instead of
3/4 complete. Applying three of four and leaving `plot_stacked_bar` to crash on a 9th segment
would be a strange place to stop given the other three are being fixed for literally the same
line of reasoning.

**T18 (label_bars docstring falsely implies orientation auto-detection): defer, don't fold in.**
I agree with member_code's own severity read — this fails loudly (`ValueError`) rather than
silently mislabeling a chart, so it doesn't carry the "reader gets a wrong-looking figure and
doesn't know it" risk that has driven this council's highest-priority fixes (T2, T7, T11, T15).
It's real (I don't dispute `BarContainer` lacking a public `.orientation` attribute — that matches
my own read of matplotlib's public API) but it's a docstring-accuracy nit on a helper function, not
a cross-file consistency problem, and it sits outside both my T11-T16 scope and this round's
already-larger-than-planned fix list (T11, T12, T13, T15+4th instance, T16, my A, my B). Recommend
the chairman log it as a fast follow-up (one-line docstring edit or drop the dead `getattr`
fallback) rather than absorbing it into this round's execution — it doesn't share a file, a
root cause, or a review pass with anything already being touched, so bundling it buys no
efficiency, only scope creep.

---

## Point 2 — Goal 2: Paper/Journal Figure sketch

Sketched separately below (not restating to the chairman, per instructions) — kept to 4-6 lines,
pointer-only, no re-added venue-formatting/decoration content, consistent with the Round 2
message-delivery prune.

**Draft block** (to insert between current Goal 1 and Goal 2, renumbering the latter to Goal 3):

```
## Goal 2: Paper / Journal Figure

Primary tool: matplotlib/seaborn (same as EDA — publication figures rarely need a new library,
just tighter execution). Use plotnine instead only if the figure is inherently a faceted/layered
grammar-of-graphics composition (see the Grammar of Graphics Reference below) — not by default.

For chart-type selection, color/palette choice, and honest-uncertainty display, see:
`references/data-visualization.md` (chart patterns), `references/matplotlib-examples.md` (worked
uncertainty examples), `references/color-palettes.md` (colorblind-safe palettes),
`references/style-guide.md` (sizing/typography defaults). For venue-specific mechanics (DPI,
figure dimensions, font embedding), check your target venue's author guidelines directly — see
`references/publication-guidelines.md` for what to look for, not a substitute for the venue's own
spec.
```

That's it — no code sample (unlike Goal 1/Goal 2, which each carry one). Rationale: Goal 1 and
Goal 2's code samples earn their place because they show a *decision* (which library, which call)
that isn't otherwise obvious from the decision tree. A paper-figure code sample would just be
"import matplotlib, call the chart-type function from data-visualization.md" — redundant with
the pointer immediately below it, and the risk flagged in T14 (this file's own examples still
carrying wet-lab flavor) makes me reluctant to add *another* code snippet under this goal until
that's cleaned up separately. Five sentences, five pointers, zero new decoration/formatting
guidance — matches the Round 2 pivot's own stated boundary (chart-type/encoding logic in scope,
venue-formatting mechanics out of scope).

---

## Point 3 — Finding A: `model-evaluation-viz.md` decision-tree label too narrow

Confirmed exact location again this pass: `SKILL.md` line 47, currently:

```
└─ Credit-risk model chart (KS curve, PSI stability) → `references/model-evaluation-viz.md`
```

**Exact fix** — replace with:

```
└─ Binary classifier evaluation chart (ROC, PR, calibration, confusion matrix, KS, PSI) → `references/model-evaluation-viz.md`
```

This is a straight line-47 swap, no restructuring of the surrounding tree needed. It brings the
decision-tree label into agreement with `SKILL.md`'s own Resources-section description of the same
file (line 208: "ROC, PR, calibration, confusion-matrix, KS, PSI charts" — already generic, no
"credit-risk" qualifier there), so the fix is really a sync-to-match-the-file's-own-other-mention,
the same pattern as T11/T12. No content inside `model-evaluation-viz.md` itself needs to change —
each section already states its own domain convention (KS/PSI as "standard in credit/collections")
internally, so genericizing the entry-point label doesn't lose that nuance, it just stops hiding
7 of 9 sections behind a domain-specific tree label a fraud/churn-model reader would skip past.

---

## Point 4 — Finding B: `chart-selection.md` decision tree missing Slope Chart leaf

Confirmed exact location: `references/chart-selection.md`, the "Change over time?" branch, lines
6-9 of the file:

```
├── Change over time?
│   ├── Few time points (< 6) → Bar chart (vertical)
│   ├── Many time points      → Line chart
│   └── Cumulative change     → Area chart (filled)
```

**Exact fix** — add a fourth leaf under this branch (before the closing `└──` reformats to a
mid-branch `├──`, matching the ASCII tree's own connector convention):

```
├── Change over time?
│   ├── Few time points (< 6) → Bar chart (vertical)
│   ├── Many time points      → Line chart
│   ├── Exactly two points    → Slope chart
│   └── Cumulative change     → Area chart (filled)
```

One line added, one connector character changed (the old `Cumulative change` leaf's `└──` becomes
`├──` since it's no longer the last item in the branch). This routes to the file's own existing
`### Slope Chart — Change Between Two Points` section (confirmed present at line 105 in my round3_1
pass), closing the same "tree doesn't route to content the file commits to" gap pattern as T16,
just contained to one file.

---

## Point 5 — Round 4 gut-check

**My honest read: this is a reasonable stopping point, with one soft caveat, not a hard call for
Round 4.**

Reasoning:
- Every confirmed fix this round is small and mechanical: one-line-to-few-line edits (T11 doc
  additions, T12 one-cell swap, T13 two qualifying edits, T15's four `% len()` wraps, T16's new
  Goal section, my A's one-line label swap, my B's one-line tree addition). None of them touch
  code logic in a way that could introduce a *new* bug — they're either string edits, list
  additions, or index-guard patterns already proven correct elsewhere in the same file. The
  "did we just create a new inconsistency while fixing this one" risk is low across the board.
- The one place I'd flag as worth a light re-check rather than a full Round 4: member_color's
  closing note that T11 and T12 are "the same underlying failure mode... appearing twice in one
  round," and that if only one gets a structural fix (table-ify + explicit sync instruction) while
  the other just gets numbers patched, the pattern will resurface. I agree with that read. If the
  chairman applies member_color's T11 table-ification but treats T12 as "just swap coolwarm for
  RdBu_r" (which is also my own recommendation, and correct as far as it goes), that's fine *for
  this round* since T12 doesn't have T11's multi-entry-list structure to begin with — but it's
  worth a one-line standing note somewhere central (SKILL.md or a CONTRIBUTING-style comment) that
  color/palette claims in prose docs must match their backing code/other-doc source, the same
  spirit as member_color's proposed sync instruction. That's a cheap addition-to-the-fix, not a
  reason to hold the round open.
- Nothing surfaced this round is close to T13's severity (a direct, first-encounter-breaking
  prescriptive contradiction) or T15's (a reproducible crash) that's still *unresolved* going into
  execution — every item on the table now has an agreed, scoped, small fix with no open
  disagreement between the three of us. That's a meaningfully different state than after Round 2,
  where T11-T19-shaped gaps were still being discovered fresh.
- Caveat on confidence: three passes deep, each of us has now read every file in the skill at
  least once specifically hunting for cross-file drift, and the finding rate per pass is dropping
  (Round 3 phase 1 surfaced 2 new items from me, 2 from member_code, 0 new from member_color;
  phase 2 cross-critique surfaced 1 more from member_code's own re-read). That trend line — fewer
  new findings each pass, and the new ones getting smaller (T18/T19-scale, not T13/T15-scale) — is
  itself the strongest signal that we're near the noise floor for this method, not that a Round 4
  would find another T13.

**Bottom line for the chairman:** apply this round's fixes (including the folded-in 4th T15
instance and my A/B), log T18 as a deferred fast-follow, add the one-line "palette claims must
match their backing source" standing note as a cheap insurance policy against a T11/T12 repeat,
and call it. I would not personally spend a Round 4 on this file set — but the decision is the
chairman's, and if they want one more pass, I'd scope it narrowly to "re-verify T11/T12/T16's
fixes landed correctly" rather than another open-ended full-file sweep, since the open-ended
sweeps are the ones showing diminishing returns.
