# Round 4.1 — member_standards Independent Findings

**Lens:** standards / cross-file consistency — internal cross-referencing, promised-vs-actual
content, structural symmetry (decision trees, tables, "see X" pointers), and message-delivery
scope adherence. Investigation only; no skill files edited.

**Method:** Read `debate_log.md` in full (Round 1 → Round 3 rulings, Scope Redirect, Round 4
topic list). Read `SKILL.md` and all 13 `references/*.md` files plus both `assets/*.py` files in
full. Cross-checked every decision tree, table, and "see `references/X.md`" pointer against the
actual target content. Ran targeted greps to sweep for colormap-list drift across the whole
skill (not just the three previously-known loci).

---

## T19 — Docstring/implementation gap in `data-visualization.md` (code-correctness topic; structural angle)

**Confirmed, and scoped precisely.** `plot_ablation`'s docstring ("For model comparison, pass
replicate-level results or estimates plus intervals; display uncertainty and
independent-replicate n") and `plot_leaderboard`'s docstring ("Use estimates with intervals")
both promise interval/uncertainty handling that the function signatures and bodies do not
implement — no `yerr`/interval parameter, no error-bar rendering in either function.

**Does this pattern recur elsewhere in the file?** I checked all 9 chart-type functions
individually. It does **not** recur beyond these two. Every other function's docstring matches
its body:
- `plot_training_curves` — no uncertainty claim in its own docstring; the "Shaded
  Variability or Uncertainty" pattern is a separate code block immediately below it, correctly
  presented as an optional addition, not baked into the function's contract.
- `plot_heatmap`, `plot_scatter`, `plot_multi_panel`, `plot_distributions`, `plot_scaling` —
  docstrings describe only what the body actually does.
- `plot_stacked_bar` — its docstring's CAUTION note (about color wraparound past 8 segments,
  added in the T15 fix) accurately describes real behavior, not an aspirational one.

**Structural significance for my lens:** `SKILL.md`'s "Color and Statistical-Honesty Reference"
paragraph explicitly sends readers to `data-visualization.md` for "showing uncertainty
honestly" as one of five named responsibilities of that pointer. Two of the nine functions in
the file it's pointing to actively demonstrate the opposite (a docstring claiming compliance
while the code ships without it) — this directly undercuts that specific SKILL.md promise, not
just a generic code-quality nit. It's the same *class* of bug as T15 (promise not backed by
code), just doc-vs-code instead of tree-vs-code.

**My recommendation (secondary to member_code's call on the exact fix):** either (a) add an
optional `errors=None` / `ci_data=None` parameter to both functions with `yerr=` plumbed through
when provided, or (b) soften the docstrings to stop asserting interval support and instead point
to `matplotlib-examples.md`'s Example 4 pattern for how to add error bars when the caller has
replicate-level data. I have no code-lens preference between (a)/(b) — flagging for member_code.

**Confidence: high** (docstring text and function bodies directly compared, gap is unambiguous,
no third recurrence found).

---

## T20 — `publication-guidelines.md`'s diverging-safe colormap list is a stale subset (T11 recurrence, third location)

**Confirmed as described**, and I swept the entire skill (all of `SKILL.md`, all 13
`references/*.md`, both `assets/*.py`) via grep for every diverging-map name
(`RdBu`, `PuOr`, `BrBG`, `PRGn`, `PiYG`, `RdYlBu`, plus the avoid-list `RdYlGn`/`RdGy` and the
already-resolved `coolwarm`) to check for any other undiscovered drift site.

**Sweep result — only one other drift site found, and it is exactly T20 (no new sites):**
- `references/color-palettes.md` (lines 144–149) and `assets/color_palettes.py` (lines 71–76) —
  the authoritative 6-map pair from the T11 fix, still in sync (verified 1:1).
- `references/publication-guidelines.md` line 26 — `RdBu, PuOr, BrBG (colorblind-safe)`, a
  3-map subset with no pointer to the authoritative table. This is T20 itself.
- `references/style-guide.md` lines 37/39 — recommends `RdBu_r` as *the single choice* for
  "Diverging" and "Correlation matrix" rows in a Use-Case → Colormap table. This is **not** a
  drift site: it's a single recommended default (the T12 fix deliberately narrowed this file to
  one map, "no second option kept, to avoid reopening a T11-style drift" per the Round 3 ruling)
  rather than an enumeration of "the safe set." No action needed here.
- `references/pre-attentive-attributes.md` line 37 — "e.g. RdBu" is an illustrative example
  within a sentence about diverging colormaps generally, not an enumerated safe-list. Not a
  drift site.
- `references/matplotlib-examples.md` and `references/data-visualization.md` — both use
  `RdBu_r` as a single concrete example in code, consistent with everywhere else, not a list.

I also swept the **sequential** colormap set (`viridis`, `plasma`, `inferno`, `magma`,
`cividis`, `YlOrRd`, `YlGnBu`) for the same pattern, since `color_palettes.py`'s
`SEQUENTIAL_COLORMAPS` is a closed list like `DIVERGING_COLORMAPS_SAFE`. No file elsewhere in
the skill presents an enumerated "safe sequential set" that could drift — every other mention is
a single example usage, not a closed list. No sequential-list drift found.

**My recommendation:** `publication-guidelines.md` line 24 (one line above the offending line)
already uses the pointer pattern for the categorical case: *"Qualitative (categories):
ColorBrewer, Okabe-Ito palette — see `color-palettes.md`."* I recommend applying the identical
pointer pattern to line 26 — replace `RdBu, PuOr, BrBG (colorblind-safe)` with a pointer to
`color-palettes.md`'s "Colorblind-Safe Diverging Maps" table — rather than re-listing all six
names a third time. Re-listing all six would fix the immediate omission but reopens a third
copy of the same data for a future edit to silently desync (the exact failure mode T11 and now
T20 both demonstrate); a pointer has nothing left to desync. This keeps the fix inside this
file's own established convention rather than inventing a new pattern.

**Confidence: high** (subset vs. authoritative-list comparison is a direct read; the sweep for
additional sites was exhaustive via grep across every file in the skill).

---

## T21 — Redundant color constants in `assets/swd_style.py` (color topic; structural angle)

Confirmed the four constants exist as described: `SWD.ACCENT` (`#E8664A`, coral) and
`SWD.ACCENT_BLUE` (`#1A77B5`) are undocumented for CVD-safety and are the actual defaults used
by `apply_swd_palette()` (via `accent_color or SWD.ACCENT`) and `highlight_region()` (via
`color or SWD.ACCENT`), while `SWD.ACCENT_POSITIVE`/`ACCENT_NEGATIVE` carry the verified
Okabe-Ito pair from the T7 fix but are not wired as a default anywhere in this file.

**Structural read (my lens):** I don't think `ACCENT`/`ACCENT_BLUE` are simply redundant with
`ACCENT_POSITIVE`/`ACCENT_NEGATIVE` — they serve a different semantic role. `ACCENT` implements
`pre-attentive-attributes.md`'s "Accent 1: one bold color — THE focus, use once per chart" (a
general single-highlight color, not inherently positive/negative), and `ACCENT_BLUE` maps to
that same file's "Accent 2: a second color — only for a direct comparison point." The
`ACCENT_POSITIVE`/`ACCENT_NEGATIVE` pair implements a narrower, different row in the same Gray
Palette Strategy table: "Negative: coral/vermillion — financial loss, error states only" /
"Positive: blue — goal achieved, up vs target only." These are two distinct rows in the prose
spec (`pre-attentive-attributes.md`'s Gray Palette Strategy), correctly implemented as two
distinct constant pairs in code — the class isn't carrying dead/duplicate constants, it's
carrying an **undocumented mapping** between code constants and prose roles.

**The actual bug, structurally:** nothing in the class docstring or inline comments states this
mapping, so a reader can't tell that `ACCENT`/`ACCENT_BLUE` ≠ `ACCENT_POSITIVE`/`ACCENT_NEGATIVE`
on purpose. Compounding this, `ACCENT`'s hex (`#E8664A`) is close enough to `ACCENT_NEGATIVE`'s
hex (`#D55E00`, also a coral/vermillion) that a maintainer skimming the class could plausibly
"simplify" by deleting one, picking the wrong one to keep.

**My recommendation:** add a docstring block (or inline comments) on the `SWD` class explicit
about the mapping: `ACCENT`/`ACCENT_BLUE` = general "Accent 1"/"Accent 2" per
`pre-attentive-attributes.md`, used by `apply_swd_palette`/`highlight_region` for generic
one-thing-matters emphasis; `ACCENT_POSITIVE`/`ACCENT_NEGATIVE` = the narrower goal/loss-framing
pair, verified Okabe-Ito, for callers that specifically need that semantic (currently no
function in this file wires them as a default — worth noting in the docstring that callers pass
them explicitly via `accent_color=SWD.ACCENT_POSITIVE` when that's the intended meaning).

**Flag for color lens:** `ACCENT` (`#E8664A`) and `ACCENT_BLUE` (`#1A77B5`) are the two
highest-traffic default colors in this file (used by default, not opt-in) and have never been
run through the same verification pass `ACCENT_POSITIVE`/`ACCENT_NEGATIVE` got in the T7 fix.
Since they're visually close to Okabe-Ito's vermillion/blue but not byte-identical, they should
get an explicit CVD-safety check rather than inheriting "probably fine, they look similar."

**Confidence: medium** (the redundancy framing in T20's write-up is arguable — I read this as
"undocumented distinct-purpose pair," not "genuinely redundant pair" — but the missing
documentation and the unverified-defaults problem are both real and high-confidence).

---

## T22 — CVD prevalence statistics (color-science topic; skipped substantively, one structural note)

Not my primary lens; I did not attempt to verify the deuteranopia/deuteranomaly prevalence
figures against external sources. One structural observation: I checked whether the ~8%
combined figure used everywhere else in the skill (`design-principles.md`, `style-guide.md`,
`pre-attentive-attributes.md`, `publication-guidelines.md`, and `color-palettes.md`'s own
"Common Mistakes" section) is at least **internally consistent** with `color-palettes.md`'s
"Types of Color Vision Deficiency" breakdown (Deuteranopia ~5% + Protanopia ~2% + Tritanopia
<1% ≈ 8%). The arithmetic is self-consistent — the breakdown sums to the same aggregate figure
used skill-wide, so there is no cross-file *numeric* contradiction, only (per T22's framing) a
possible within-file subtype-labeling precision issue (dichromacy names attached to what may
actually be the more common anomalous-trichromacy prevalence numbers). That's a color-science
accuracy question, not a structural one — deferring to member_color.

**Confidence: n/a (deferred).**

---

## T23 — `causal-inference-charts.md`'s "IV first-stage" promise has no matching section (PRIMARY TOPIC)

**Confirmed, gap is real.** The "Presentation Order for Causal Results" table (step 3) names
four identification strategies with their assumption-check chart:

| Strategy | Assumption-check chart named | Matching `##` section in this file |
|---|---|---|
| DiD | parallel trends chart | `## 2. Parallel Trends Check` — present |
| RDD | binned scatter continuity + density test | `## 4. RDD Binned Scatter` — present |
| PSM | propensity overlap chart | `## 5. Propensity Score Overlap` — present |
| IV | first-stage F-statistic + relevance test | **none** |

I re-read the file end to end: the five `##` sections are Coefficient Plot, Parallel Trends
Check, DiD Event Study, RDD Binned Scatter, Propensity Score Overlap. No section, subsection, or
even a passing code fragment addresses instrumental variables, first-stage regression, or
F-statistics anywhere else in the file (grepped for "IV", "instrument", "first-stage",
"F-stat" — the only hits are the one Presentation Order line itself). The "Common Causal
Inference Chart Mistakes" table at the bottom also only covers DiD/RDD/PSM/point-estimate
mistakes, not IV — so this isn't a case where IV guidance exists elsewhere in the file under a
different heading; the gap is total.

**Recommendation: write the missing section, don't soften the table.** Reasoning:

1. **Precedent.** Every prior promised-content gap the council found (T16 — SKILL.md's
   paper/journal path, T17 — model-evaluation-viz.md's KS Curve row) was resolved by *writing
   the missing content*, not by narrowing the promise, whenever the file was being kept as the
   canonical home for that content class. This file is explicitly kept ("KEEP" in the Scope
   Redirect pass) as the domain-interpretation home for causal charts — the same posture
   `model-evaluation-viz.md` had when T17 was resolved by adding the KS Curve section.
2. **The file's own stated purpose argues against softening.** The Core Principle at the top of
   this file says: *"A chart that shows only the point estimate without uncertainty, or that
   presents a DiD result without showing the parallel trends check, is incomplete regardless of
   how statistically correct the underlying analysis is."* That standard applies identically to
   IV — an IV estimate presented without the first-stage strength check is exactly the kind of
   "incomplete despite being statistically correct" chart this file exists to prevent. Removing
   the IV line from the table to avoid the gap would leave the file silently endorsing showing
   IV results without their assumption check, undercutting its own founding principle for one of
   the four canonical identification strategies it otherwise treats symmetrically.
3. **IV is not a niche strategy relative to the other three.** DiD/RDD/PSM/IV are the standard
   four-strategy causal-inference toolkit; a practitioner using this file specifically because
   they have an IV design (weak instruments being one of the most common reasons an IV causal
   claim is challenged) is exactly the reader this file should serve, per the same
   message-delivery/domain-interpretation criteria that kept this file in scope during the
   redirect.

**Suggested content shape**, matching the depth/structure of the other four sections (Use
when / Audience / Required inputs / Key design decisions):
- **Use when:** Validating instrument strength/relevance before presenting a 2SLS or IV
  estimate. This is an assumption diagnostic, not a result chart — show it before the main
  estimate, same rule as Parallel Trends/RDD/PSM.
- **Required inputs:** `instrument`, `endogenous_regressor`, `first_stage_f_stat`,
  `first_stage_coefficient` (+ CI), conventional weak-instrument threshold context (e.g. the
  commonly-cited rule-of-thumb F > 10, with the same "state your policy value, not a universal
  law" caveat this file already uses for PSI-style thresholds elsewhere in the skill).
- **Key design decisions:** bar or scatter of instrument vs. endogenous regressor with the
  first-stage F-statistic annotated directly on the chart (not buried in a table); flag visually
  when F falls below the weak-instrument threshold; report the relevance *and* (briefly)
  exclusion-restriction reasoning as a caveat, since the chart can only ever speak to relevance,
  not exclusion.

**If the council instead prefers the lighter fix** (softening/removing the IV line rather than
writing a new section) — e.g. on the grounds that IV designs are less common in this skill's
typical DS/credit-risk/business-analytics audience than DiD/RDD/PSM — I'd want that decided
explicitly rather than defaulted to, since it's a real scope trade-off, not a free action. My
own recommendation is still to write the section; I flag the alternative for the chairman.

**Confidence: high** (gap confirmed by full-file read plus targeted grep; recommendation
follows directly from the council's own established precedent in T16/T17).

---

## New promised-content gap found during the broader sweep (beyond T19–T23)

### NEW — `SKILL.md`'s Resources list promises "uplift" charts in `causal-inference-charts.md`; the file has none

**Location:** `SKILL.md`, Resources section:
```
### references/ — general analysis charts
- `model-evaluation-viz.md` — ROC, PR, calibration, confusion-matrix, KS, PSI charts
- `causal-inference-charts.md` — uplift, DiD, event-study charts
```

**The gap:** `causal-inference-charts.md`'s five sections are Coefficient Plot, Parallel Trends
Check, DiD Event Study, RDD Binned Scatter, Propensity Score Overlap. There is no uplift-related
content anywhere in the file — I grepped the entire skill for "uplift" and the *only* hit in the
whole tree is this one line in `SKILL.md`. Uplift modeling (Qini curves, uplift-by-decile
charts, heterogeneous treatment effect targeting) is a materially different chart family from
the four identification-strategy assumption-check charts this file actually contains — it's
about ranking/targeting individuals by estimated treatment effect, not about validating an
average-effect identification design. A reader following `SKILL.md`'s Resources pointer
specifically for uplift guidance finds nothing.

**Why this is the same bug class as T23, in a different location:** T23 is a promise made
*inside* `causal-inference-charts.md` (its own Presentation Order table) with no matching
section in that same file. This new gap is a promise made *about* that file from `SKILL.md`,
one level up, and it's arguably a cleaner miss than T23 — IV at least belongs to the same family
of chart (identification-strategy assumption check) as the other three; uplift belongs to a
different family entirely, so there's no partial credit here the way there arguably is for IV
sharing a table with DiD/RDD/PSM.

**My recommendation:** given the file is scoped around "assumption checks before showing a
causal estimate" (its stated Core Principle), and uplift modeling doesn't fit that frame
cleanly (there's no single "assumption chart" analog for uplift the way there is for
DiD/RDD/PSM/IV), I lean toward the lighter fix here: **drop "uplift" from `SKILL.md`'s
one-line description** rather than writing a new Uplift/Qini section, since adding one would
mean growing the file's scope to a second chart family (targeting/ranking) rather than closing
a gap within its existing one (identification-design assumption checks). This is a genuinely
different judgment call from my T23 recommendation, and I want that inconsistency-of-verdict
flagged explicitly rather than smoothed over: T23 I recommend writing the content; this one I
recommend removing the promise. The distinguishing factor for me is scope fit, not gap size —
IV fits the file's existing frame, uplift doesn't.

**Confidence: high** (the absence is unambiguous — a single grep across the entire skill
confirms "uplift" appears nowhere except the one promise).

---

## Other structural observations from the sweep (low confidence / not asserting as bugs)

These did not rise to the level of a clear promised-content gap, but I want them on the record
since the sweep was explicitly meant to be fresh rather than assuming Round 3 caught everything.

1. **`chart-selection.md`'s decision tree has several leaves with no dedicated
   "Chart-by-Chart Guide" section** (Area chart, Back-to-back bar, Stacked bar/100% bar,
   Histogram/density plot, Box/violin plot, Connected scatter, Big number+sparkline all appear
   only as tree leaves, not as their own worked subsection — contrast with Line Chart, Bar Chart
   (Vertical), Horizontal Bar Chart, Scatter Plot, and Slope Chart, which each get one). I rate
   this **low confidence as a bug**, not a new topic: unlike "IV first-stage F-statistic" or
   "uplift," these are self-explanatory, generic chart types where the one-line tree guidance
   ("Sort bars by size," "Only bottom series is readable") is arguably sufficient and doesn't
   promise a deeper section exists. The file's own heading ("Chart-by-Chart Guide") doesn't
   claim 1:1 coverage of every tree leaf. Flagging for completeness, not recommending action.

2. **`SKILL.md`'s Library Decision Tree routes to `model-evaluation-viz.md` for classifier-eval
   charts but has no equivalent leaf for `causal-inference-charts.md`**, even though both files
   sit side-by-side in the Resources list under "general analysis charts." This is an
   asymmetry, but not a broken promise — the tree never claims to cover domain-specific analysis
   charts exhaustively; the classifier-eval leaf is the odd one out for having a domain route at
   all. Low confidence / cosmetic; not recommending action, just noting for the record in case
   the chairman wants the tree symmetric.

3. **No other dangling references to previously-deleted content** were found beyond what
   `debate_log.md` already confirms clean (`journal-requirements`, `*.mplstyle`, `style_presets`,
   `PALETTE_DEEP`, `banking-visualization`, `COLOR_LIST`, `Ocean Dusk` — all zero hits, matching
   the Round 4 context note). I did not find any new dangling reference.

---

## Summary table

| Topic | My verdict | Confidence | Recommended fix |
|---|---|---|---|
| T19 | Confirmed, scoped to exactly 2 sites (no 3rd recurrence found) | High | Add interval params or soften docstrings — defer exact mechanism to member_code |
| T20 | Confirmed; sweep found no additional undiscovered drift sites | High | Replace inline 3-map list with a pointer to `color-palettes.md`'s table, matching this file's own existing pointer convention one line above |
| T21 | Confirmed but reframed: not redundant, undocumented-purpose pair | Medium | Add class docstring clarifying `ACCENT`/`ACCENT_BLUE` (general emphasis) vs. `ACCENT_POSITIVE`/`ACCENT_NEGATIVE` (goal/loss framing); flag unverified defaults to color lens |
| T22 | Deferred — internally consistent aggregate, subtype-precision is a color-science call | N/A | Defer to member_color |
| T23 | Confirmed, gap is real and total | High | **Write** the missing IV First-Stage F-Statistic section (matching depth of the other 4), per T16/T17 precedent — do not soften the table |
| NEW: SKILL.md "uplift" promise | Confirmed, gap is real and total | High | **Remove** "uplift" from SKILL.md's one-line description (different scope-fit judgment than T23 — flagged explicitly) |
