# Round 4.2 — member_code Consolidated Findings (cross-critique of T19–T23 + NEW)

Read in full: `round4_1_member_code.md` (own prior pass), `round4_1_member_color.md`,
`round4_1_member_standards.md`, and skimmed `debate_log.md` for T1–T18 context. Ran fresh
verification (not re-derivation from memory) for the two open numeric questions the chairman
flagged: WCAG contrast ratios for `SWD.ACCENT` candidates, computed directly in Python using the
same relative-luminance formula member_color used (reproduced member_color's four reported
ratios exactly as a sanity check before trusting my own new numbers — see below).

---

## Tension 1 — T21: delete `ACCENT_BLUE` or keep-and-document it?

**Verdict: DELETE. Definitive.**

member_standards' "undocumented distinct-purpose pair" reading is well-argued on its own terms —
`pre-attentive-attributes.md`'s Gray Palette Strategy table does have a genuine "Accent 2: a
second color — only for a direct comparison point" row that `ACCENT_BLUE`'s inline comment
("second emphasis, use sparingly") plausibly operationalizes. But the chairman's wrinkle is the
deciding fact, not a side note: "Accent 2 ... for a direct comparison point" is definitionally
the two-hue-simultaneous-display scenario. Per member_color's own (sound) color-science
reasoning — CVD is a hue-*discrimination* deficit, irrelevant to a single hue shown against
neutral gray, but very relevant the instant two data-carrying hues must be told apart on the same
chart — keeping `ACCENT_BLUE` "for real" would obligate the exact verification work `ACCENT_POSITIVE`/`ACCENT_NEGATIVE` got under T7: a CVD-simulator check of the `ACCENT`/`ACCENT_BLUE` pair specifically, plus a citation-style inline comment. Nobody on the council has done that
check, and re-purposing "keep it, just add a docstring" as the fix would ship a constant whose
entire documented reason for existing (direct comparison against `ACCENT`) has never been
verified safe — worse than the current state, which is at least honestly inert.

Weighing the concrete facts against each other:
- Zero call sites, skill-wide (confirmed independently by member_code and member_color via
  separate greps — this isn't a single grep's blind spot).
- Its one historical caller (`waterfall_colors`) was already deleted under T1; nothing in the
  current file exercises the "Accent 2 direct comparison" pattern it would document.
- This repo has an explicit, already-applied precedent for exactly this situation: the T10
  ruling on `simulate_deuteranopia` — "either implement for real or delete, don't leave a no-op
  that looks functional." A constant with a plausible-sounding doc-comment but no caller and no
  safety verification is the color-constant equivalent of that no-op function.
- "Keep and document" doesn't actually close the gap the topic raises — it would require *also*
  doing the CVD-pair verification to be a complete fix, which is strictly more work than deleting
  and is speculative work for a currently-nonexistent use case (no chart in this skill currently
  needs a second accent for direct comparison; if one arises, add the constant back then, sized
  to that real use case, verified against the real second hue it's actually compared to).

**Final fix:** delete `SWD.ACCENT_BLUE = '#1A77B5'   # blue — second emphasis (use sparingly)`
(line 26 of `assets/swd_style.py`) outright. Do not add a "keep for future Accent-2 use"
placeholder — per the T10 precedent, re-add it when a real caller and a real verified pairing
exist, not before.

**Confidence: high.**

---

## Tension 2 — T21: what should `SWD.ACCENT` become?

**Verdict: neither of the two Round-1 proposals survives contact with a direct calculation.
Reconciled final fix: darken `ACCENT` within its existing hue/saturation family; do not swap to
`#E69F00`.**

First, reproduced member_color's four reported ratios independently (WCAG relative-luminance
formula, sRGB linearization) to confirm the method before trusting new numbers:

| Color | vs. white | vs. `GRAY_LIGHT` #CCCCCC |
|---|---|---|
| `ACCENT` `#E8664A` | 3.27:1 | 2.03:1 |
| `ACCENT_BLUE` `#1A77B5` | 4.83:1 | 3.01:1 |
| `ACCENT_POSITIVE` `#0072B2` | 5.19:1 | 3.23:1 |
| `ACCENT_NEGATIVE` `#D55E00` | 3.87:1 | 2.41:1 |

Exact match to member_color's table — method confirmed sound.

Then computed the chairman's specific ask, member_code's own `#E69F00` (Okabe-Ito orange)
proposal, against the same two backgrounds:

| Color | vs. white | vs. `GRAY_LIGHT` #CCCCCC |
|---|---|---|
| `#E69F00` (candidate) | **2.25:1** | **1.40:1** |

**This is worse than the current `ACCENT` on both axes**, not better — it fails the chairman's
"does one fix solve both problems" test decisively. My Round-1 proposal (b) is retracted: I
proposed `#E69F00` purely on CVD-vetted-hue grounds (it's an unused Okabe-Ito color) without
checking its luminance against white/gray, and it turns out to be one of the lightest hues in
that palette — exactly wrong for a color that needs to read against light backgrounds. This is
the kind of thing that's obvious once measured and easy to miss by reasoning about hue safety
alone; good catch by the chairman forcing the check.

I also swept the remaining unused Okabe-Ito hues for completeness, in case one of them threaded
the needle:

| Color | vs. white | vs. `GRAY_LIGHT` |
|---|---|---|
| sky blue `#56B4E9` | 2.31:1 | 1.44:1 |
| bluish green `#009E73` | 3.42:1 | 2.13:1 |
| yellow `#F0E442` | 1.32:1 | 1.21:1 |
| reddish purple `#CC79A7` | 3.06:1 | 1.91:1 |

None clears 3:1 against `GRAY_LIGHT` either (bluish green comes closest at 2.13:1, still short).
The Okabe-Ito palette as a whole is optimized for CVD-discriminability between saturated hues at
roughly matched mid-lightness, not for high-contrast-against-light-gray — swapping within it
doesn't solve a contrast problem, confirming member_color's read that this needs a luminance fix,
not a hue-identity fix.

**Given `ACCENT_BLUE` is deleted (Tension 1), `ACCENT` is used only alone against neutral
background** (`apply_swd_palette` vs. `GRAY_LIGHT`, `highlight_region` vs. background) — so per
member_color's reasoning, which I adopt as correct, CVD-pair verification is not needed for
`ACCENT` at all going forward. The only real, actionable accessibility defect is the thin
contrast member_color found. The cleanest fix is therefore to keep `ACCENT`'s hue family (so it
still reads as "coral," visually distinct from `ACCENT_NEGATIVE`'s vermillion, preserving
member_standards' point that the two shouldn't become easy to confuse) and darken it until it
clears WCAG's 3:1 minimum for non-text graphical objects against **both** white and its own
paired `GRAY_LIGHT` — 2.03:1 against `GRAY_LIGHT` is the binding constraint, not the 3.27:1
against white.

Computed a same-hue/same-saturation lightness sweep (H=10.6°, S=0.77 held constant, only L
varied) to find the minimal darkening that clears both thresholds with a safety margin rather
than just barely (a "just clears 3.03:1" fix is fragile to any future anti-aliasing/opacity
tweak):

| L | Hex | vs. white | vs. `GRAY_LIGHT` |
|---|---|---|---|
| 0.46 | `#D03B1A` | 4.86:1 | 3.03:1 (barely clears) |
| **0.44** | **`#C73819`** | **5.24:1** | **3.26:1** |
| 0.40 | `#B53317` | 6.09:1 | 3.79:1 |

**Final recommendation: `SWD.ACCENT = '#C73819'`** (down from `#E8664A`, same hue/saturation
family, L 0.60 → 0.44). This:
- Clears WCAG 3:1 against both white (5.24:1) and `GRAY_LIGHT` (3.26:1) with real margin, not a
  hairline pass.
- Stays in the same hue (10.6°) as the original — still reads as "coral/red-orange," not a hue
  swap, so it doesn't inherit member_standards' "which is the accent" confusability risk with
  `ACCENT_NEGATIVE` (`#D55E00`, hue 26.5°) — the ~16° hue gap between the two is unchanged from
  the current file, i.e. darkening doesn't erode the distinction that already existed.
- Needs no CVD-pair verification, because (per the resolved Tension 1) `ACCENT` will only ever be
  shown alone against neutral gray/white going forward — this is purely a contrast fix, correctly
  targeting the actual defect member_color identified, not a defect that doesn't exist (CVD-pair
  safety for a constant no longer paired with anything).

Add an inline comment matching the file's existing citation style for the positive/negative pair,
e.g. `# coral — the ONE thing that matters (WCAG 3:1+ verified vs. white and GRAY_LIGHT)`.

**Confidence: high** on the contrast numbers (mechanically computed, method cross-checked against
member_color's independently-computed values, exact match). **High** on the fix direction
(darken-in-place beats both Round-1 proposals on the chairman's own test). **Medium** on the
exact final hex (`#C73819` is my pick for a comfortable margin; `#D03B1A` is an equally valid,
less-drastic alternative if the council prefers a smaller visual change from the original coral —
this is a stylistic tiebreak, not a correctness question, since both clear 3:1).

---

## Tension 3 — T19: confirm final fix code

**Verdict: (a) is final — both member_code and member_standards converge here, and (b) doesn't
survive scrutiny.**

member_standards deferred the (a)/(b) choice explicitly ("no code-lens preference"). Resolving
it: (b) — softening the docstrings to stop promising interval support — would satisfy the letter
of "docstring matches body" but actively regresses the skill's own stated mission. `SKILL.md`
sends readers to `data-visualization.md` by name for "showing uncertainty honestly," and
`publication-guidelines.md`'s Statistical Rigor section states uncertainty display is a
requirement, not an option, for model-comparison charts — the exact chart type these two
functions are. Softening the docstring would make the file *consistent* while making it *worse*
at the one job it's pointed to for. (a) is the only fix that keeps both the docstring's promise
and the skill's cross-file mission intact. Final call: **(a), unconditionally.**

**Final parameter names and docstring wording** (confirmed against matplotlib 3.10.8's installed
`Axes.bar`/`Axes.barh` signatures, verified in Round 1):

`plot_ablation` — new third positional-or-keyword param, `errors_data=None`, dict keyed identically
to `methods_data` (`{method_name: list_of_errors}`), each entry either a length-`n_categories`
list (symmetric ± half-width) or a `(2, n_categories)` array (asymmetric CI). Passed through as
`yerr=errors_data.get(method) if errors_data else None`, with `capsize=3` always passed explicitly
(matplotlib's default `capsize` is `0`, i.e. invisible caps — must be set explicitly or the error
bars render as bare lines with no visual stop, which would be a silent half-fix).

Docstring addition:
```
errors_data: optional dict of {method_name: list_of_errors}, same keys/shape as methods_data.
             Each entry is the +/- interval half-width per category (or a (2, n_categories)
             array for asymmetric CIs). Populate this whenever reporting a model comparison —
             pass replicate-level results or estimates plus intervals — and report n in the
             caption or axis label.
```

`plot_leaderboard` — new param `errors=None`, list/array length `len(scores)` (or `(2, len(scores))`
for asymmetric), passed as `xerr=errors, capsize=3` in the `ax.barh(...)` call (not `yerr` —
`barh`'s value axis is x, confirmed in Round 1 against the installed matplotlib docstring).

Docstring addition:
```
errors: optional interval half-widths (or (2, n) array for asymmetric CIs), same length as
        scores. Use estimates with intervals — pass via `errors` — and highlight only by a
        prespecified criterion.
```

Both signatures keep all existing params in their current order with the new param inserted
right after the primary data param (`methods_data`, `scores`) and before the cosmetic params —
matches this skill's existing convention elsewhere (data params first, cosmetic/figsize params
last) and keeps the change backward-compatible for any positional caller that doesn't pass the
new optional argument.

Non-blocking secondary note from Round 1 (member_code, uncontested): `plot_leaderboard`'s value
label at `bar.get_width() + 0.3` may visually collide with a rendered error cap for wide
intervals. Not required for T19's resolution; worth a one-line mention or a
`+ (errors[i] if errors is not None else 0) + 0.3` adjustment if whoever implements this wants to
polish it in the same pass.

**Confidence: high.**

---

## Full per-topic final verdicts

### T19 — docstring/implementation mismatch in `plot_ablation` / `plot_leaderboard`
**Verdict:** Confirmed real bug, both functions. **Fix:** as specified under Tension 3 above —
add `errors_data=None` / `errors=None`, wire to `yerr`/`xerr` with explicit `capsize=3`, update
docstrings to the exact wording above. **Confidence: high.**

### T20 — `publication-guidelines.md` stale 3/6 diverging-colormap subset
**Verdict:** Confirmed, third recurrence of the T11 drift pattern. All three Round-1
investigations independently converge on the same fix (member_code flagged it as a judgment call
for the standards/color lens; both of those lenses came back with the identical pointer-based
fix, and member_standards additionally swept the entire skill and found no other undiscovered
drift sites). **Fix:** replace `references/publication-guidelines.md` line 26 (`**Diverging
(negative to positive)**: RdBu, PuOr, BrBG (colorblind-safe)`) with a pointer matching the file's
own existing convention one line above (line 24's categorical pointer to `color-palettes.md`),
e.g.: `**Diverging (negative to positive)**: colorblind-safe maps only — see color-palettes.md's
Colorblind-Safe Diverging Maps table (e.g. RdBu, PuOr, BrBG).` A pointer, not a third enumerated
copy, permanently closes the drift risk rather than relocating it. **Confidence: high** (unanimous
across all three lenses, sweep-verified no other sites exist).

### T21 — `swd_style.py` accent-color constants
**Verdict:** Resolved per Tensions 1 and 2 above. **Fix (two parts, both final):**
1. Delete `SWD.ACCENT_BLUE` (line 26) — dead code, zero call sites, its only historical caller
   already removed under T1; re-add only if/when a real "Accent 2 direct comparison" caller and a
   verified `ACCENT`/second-hue CVD check both exist.
2. Change `SWD.ACCENT` from `#E8664A` to `#C73819` (same hue/saturation, darkened for WCAG 3:1+
   contrast against both white and `GRAY_LIGHT`) with an inline comment noting the contrast
   verification. No CVD-simulator work needed, since post-deletion `ACCENT` is only ever shown
   against neutral gray.

**Confidence: high** on both parts — this is the one topic where Round-1's three lenses actively
disagreed on direction, and the disagreement is now fully resolved with mechanical verification
(grep for call sites, computed contrast ratios) rather than a judgment call left open.

### T22 — CVD subtype prevalence figures (deuteranopia/protanopia mislabeled)
**Verdict:** Not a code-correctness topic (confirmed independently in Round 1 — no
`assets/*.py` file consumes these numbers; they're presentational prose only). Deferring fully to
member_color's finding, which is well-sourced (four independent citations, internally consistent
with the skill's own "~8%" aggregate figure used elsewhere) and unopposed by any other lens.
**Fix:** adopt member_color's proposed replacement text verbatim — relabel the four-row breakdown
as Deuteranomaly (~5%), Protanomaly (~1%), Deuteranopia (~1%), Protanopia (~1%), plus a combined
Tritanopia/Tritanomaly (~0.01%) row, with the "cannot distinguish" language restricted to the two
true-dichromacy rows and a closing sentence tying the four back to the skill-wide "~8%" figure.
**Confidence: high** (adopting member_color's high-confidence, well-sourced finding; no
code-lens objection).

### T23 — `causal-inference-charts.md` missing IV first-stage section
**Verdict:** Confirmed by two independent full-file reads (member_code, member_standards) —
total gap, zero mentions of IV/instrument/first-stage/F-statistic anywhere outside the one
Presentation Order table line. **Fix:** write the missing `## 6. IV First-Stage Diagnostic`
section, not soften the promise. Both lenses that examined this converged on "write it" (not
"remove the promise") independently, and member_standards' reasoning is sound and directly
on-point: this file's own Core Principle ("a chart that presents a result without its assumption
check is incomplete regardless of correctness") applies to IV exactly as it does to DiD/RDD/PSM,
and the T16/T17 precedent in this same council is to fill promised-content gaps in files kept as
canonical homes for that content class (this file was explicitly KEPT in the Scope Redirect
pass). Adopt member_standards' proposed section shape (Use when / Required inputs / Key design
decisions, matching the other five sections' template; Staiger-Stock F > 10 rule-of-thumb with a
"state your policy threshold" caveat matching this skill's existing PSI-threshold pattern).
**Confidence: high** (unanimous across the two lenses that examined it; gap mechanically verified
via grep + full read by both).

### NEW — `SKILL.md` promises "uplift" charts in `causal-inference-charts.md`; none exist
**Verdict:** Confirmed (member_standards only — single-lens finding, but the absence is
mechanically unambiguous: one grep hit for "uplift" in the entire skill, the promise itself).
From the code-correctness angle there's nothing to verify beyond the grep (no code backs this
either way), so I'm affirming member_standards' verdict and reasoning rather than re-deriving it.
**Fix: remove "uplift" from `SKILL.md`'s Resources one-liner** (`causal-inference-charts.md —
uplift, DiD, event-study charts` → drop "uplift,"), rather than writing a new section — and I
agree this is correctly a *different* call from T23, not an inconsistency needing to be smoothed
over. The distinguishing test is scope-fit against the file's own Core Principle: IV first-stage
is an assumption-check chart for one of the same four identification strategies (DiD/RDD/PSM/IV)
this file already treats symmetrically, so writing it closes a gap within the file's existing
frame. Uplift modeling (ranking/targeting by estimated individual treatment effect) has no
assumption-check analog and belongs to a different chart family entirely — adding it would be
scope expansion, not gap-closing, and this council's own T20/T-series pattern (prefer pointers
and precise scoping over inline duplication/expansion when a topic risks drift or scope creep)
supports the lighter fix here. **Confidence: high** on the gap; **high** on the fix direction
(the asymmetry with T23 is principled, not arbitrary — both lenses' reasoning point the same way
once the scope-fit test is applied explicitly).

---

## Anything still unresolved after this pass

None. All three chairman-flagged tensions (T21 delete-vs-keep, T21 `ACCENT` hex value, T19 fix
confirmation) are resolved with concrete, execute-ready fixes above. T20/T22/T23/NEW had no
cross-lens disagreement in Round 1 requiring resolution — all lenses that examined each converged
independently; I'm recording final verdicts for completeness per the task instructions, not
because they were contested.

One flag for the chairman, not a disagreement: T21's final `ACCENT` hex (`#C73819`) is my pick
among several that clear the 3:1 threshold with margin (`#D03B1A` at L=0.46 is a smaller visual
change from the original and also clears both thresholds, 4.86:1/3.03:1). If the council wants
the least-perceptible change from the current coral, `#D03B1A` is an equally correct fallback —
noting this as a stylistic tiebreak, not a reopened question, since both values are computed and
verified above.

## Summary table

| Topic | Final verdict | Final fix | Confidence |
|---|---|---|---|
| T19 | Confirmed bug, both functions | Add `errors_data=None` (`plot_ablation`) / `errors=None` (`plot_leaderboard`), wire to `yerr`/`xerr`, `capsize=3` explicit, docstrings as specified | High |
| T20 | Confirmed, 3rd T11 recurrence | Replace inline 3-map list with pointer to `color-palettes.md`'s table (matches file's own existing pointer convention) | High |
| T21 | Resolved (both tensions) | Delete `ACCENT_BLUE`; change `ACCENT` `#E8664A` → `#C73819` (contrast fix, same hue family, no CVD work needed) | High |
| T22 | Confirmed, color-science fix | Adopt member_color's relabeled deuteranomaly/protanomaly/deuteranopia/protanopia breakdown verbatim | High |
| T23 | Confirmed, total gap | Write `## 6. IV First-Stage Diagnostic` section per member_standards' template | High |
| NEW (uplift) | Confirmed, total gap | Remove "uplift" from `SKILL.md`'s Resources line (lighter fix — different scope-fit judgment than T23, correctly so) | High |
