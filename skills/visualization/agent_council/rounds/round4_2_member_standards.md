# Round 4.2 — member_standards Consolidated Findings (Cross-Critique)

**Lens:** standards / cross-file consistency. This round reads `round4_1_member_code.md`,
`round4_1_member_color.md`, and my own `round4_1_member_standards.md`, resolves the three
tensions the chairman flagged, and produces one final execution-ready verdict per topic
(T19–T23 plus the NEW "uplift" finding). No skill files edited — investigation/critique only.

---

## Resolution 1 — T21: `ACCENT_BLUE` — REVISING my Round-1 call from "keep and document" to "delete"

**Final verdict: DELETE `SWD.ACCENT_BLUE`. My original "keep and document" recommendation is
withdrawn.**

### Why the wrinkle changes the answer

My Round-1 framing treated `ACCENT`/`ACCENT_BLUE` as an *already-legitimate, merely
undocumented* second row in the Gray Palette Strategy spec ("Accent 1"/"Accent 2"), parallel to
the documented `ACCENT_POSITIVE`/`ACCENT_NEGATIVE` pair. That framing was wrong in one specific
way: I verified the *existence* of the Accent-1/Accent-2 mapping but never checked whether the
Accent-2 *use case* — two accent hues shown simultaneously for a direct comparison — had ever
been validated for CVD-safety. It hasn't. member_code confirmed `ACCENT_BLUE` has zero call
sites and is orphaned dead code left over from the T1 deletion of `waterfall_colors()`.
member_color independently confirmed the same zero-call-site fact and added the color-science
reasoning: a lone accent against gray needs only contrast verification (which CVD doesn't
affect), but two simultaneous hues need discrimination verification (which CVD does affect) —
and that second scenario is *specifically* what `ACCENT_BLUE`'s own inline comment and
`pre-attentive-attributes.md`'s "Accent 2" row describe as its job. Nobody has run that check on
`#E8664A` + `#1A77B5`.

That reframes the keep/delete choice entirely. "Keep and document" was only the cheap, safe
option under the assumption that `ACCENT_BLUE` was already doing legitimate, low-risk work
(single accent vs. gray). It isn't — it's zero-call-site, and its *documented* job is the one
CVD-sensitive scenario in this file that has never been checked. Keeping it "as documented" would
mean asserting a constant is ready for a two-hue comparison role it has never been verified for —
that's not a safe default to leave lying around for a future caller to trust; it's an unverified
claim dressed as a settled one. Responsibly keeping it now requires *new* verification work
(a CVD-simulation pass on the `#E8664A`/`#1A77B5` pair) that nobody has done and that isn't in
scope for this round. Deletion requires none.

### Applying the T10 precedent

T10's ruling on `simulate_deuteranopia` ("either implement for real or delete, don't leave a
no-op that looks functional") is not a perfect match — `ACCENT_BLUE` is a real, correctly-typed
hex constant, not a function silently returning the wrong thing while looking correct. But the
*structural* pattern is the same one T10 was guarding against: something present in shipped code
that *looks* ready to use for its stated purpose but isn't actually validated for that purpose,
with zero live callers to have caught the gap. The "function vs. color constant" distinction
doesn't change the core issue T10 was about — silent unreadiness masquerading as readiness. A
maintainer or downstream user has no way to discover, short of independently researching CVD
pairs, that `ACCENT_BLUE` is not safe to pair with `ACCENT` for a comparison chart. I read this
as close enough to T10's precedent to apply the same resolution: delete now, re-add with real
verification if/when a caller actually needs a second accent hue.

### Convergence

All three lenses now land on delete: member_code (dead-code diagnosis, high confidence),
member_color (zero call sites, no CVD-pairing scenario currently exists to protect, high
confidence), and me on reconsideration. **This is now a unanimous, non-tension finding — no
further debate needed on the ACCENT_BLUE keep/delete question itself.**

### Full T21 fix bundle (final)

1. **Delete `SWD.ACCENT_BLUE`** from `assets/swd_style.py` (line 26).
2. **Adjust `references/pre-attentive-attributes.md`'s "Accent 2" row** — see Resolution 3 below;
   this is a necessary companion edit, not optional cleanup, because of how tightly that table
   maps to the `SWD` class's constants (see Resolution 3 for why).
3. **Add a short docstring/comment on the `SWD` class** distinguishing `ACCENT` (general
   single-highlight color, "Accent 1," used as the default in `apply_swd_palette`/
   `highlight_region`) from `ACCENT_POSITIVE`/`ACCENT_NEGATIVE` (the narrower, CVD-verified
   goal/loss-framing pair, not wired as any function's default — callers pass it explicitly).
   This part of my original T21 recommendation stands on its own merits regardless of the
   `ACCENT_BLUE` call: `ACCENT`'s hex (`#E8664A`) is visually close enough to
   `ACCENT_NEGATIVE`'s (`#D55E00`) that an undocumented class remains a "which one do I keep"
   trap for a future pruning pass, per my Round-1 finding.
4. **Non-blocking, flagged for a future round, not required to resolve T21 now:**
   member_color's finding that `ACCENT` (`#E8664A`) has thin WCAG contrast (2.03:1 against
   `GRAY_LIGHT`, the color it's most often composed against as `apply_swd_palette`'s default) is
   a real, independent accessibility property — but it's pre-existing, not a regression
   introduced by this round's fixes, and it's a genuinely different question (luminance contrast)
   from anything T21 originally asked about (CVD pairing). I agree with member_color that no
   CVD-simulator work is needed for `ACCENT` used alone against neutral gray — that would be
   solving a problem that doesn't exist for that usage pattern. Whether to also darken `ACCENT`
   for contrast is a legitimate follow-up but shouldn't block or complicate this round's T21
   resolution.

**Confidence: high** on delete + prose-line adjustment (unanimous across all three lenses on the
delete; the prose-adjustment necessity is my own finding, argued in Resolution 3, and I rate it
high-confidence given the literal 1:1 mapping demonstrated there). **Medium** on the exact
replacement wording for the "Accent 2" prose row (direction is unambiguous; phrasing is a
judgment call untested by the other two lenses).

---

## Resolution 2 — T23 vs. uplift: verdicts CONFIRMED, not revised — the standard is consistent

**Final verdict, T23: write the missing `## 6. IV First-Stage Diagnostic` section. Unchanged
from Round 1.**
**Final verdict, uplift: remove "uplift" from `SKILL.md`'s Resources one-liner. Unchanged from
Round 1.**

### Stress-testing the friendliest possible uplift reframing

The chairman's hypothetical: an "Uplift / Heterogeneous Treatment Effect Targeting" section
framed specifically as an assumption-check ("is the ranking itself well-calibrated/trustworthy"),
analogous to the other four. I considered this seriously rather than reflexively defending my
Round-1 call.

A version of this does exist in the wild — a Qini/AUUC curve checked against a random-targeting
baseline is, in a loose sense, an "assumption check before you trust the ranking." If I only
asked "can a chart be described in the assumption-check register," the answer is yes, and that's
what makes this a genuine stress test rather than a strawman.

But the file's frame is narrower than "any chart that checks something before trusting a number."
Rereading the Core Principle precisely: *"A chart that shows only the point estimate without
uncertainty, or that presents a DiD result without showing the parallel trends check, is
incomplete."* Every one of DiD/RDD/PSM/IV is a **strategy for identifying a single, average
treatment effect**, and each assumption-check chart validates the *specific threat to that
identification* the strategy is exposed to (pre-trend divergence, cutoff manipulation, poor
overlap, weak instruments). Uplift/HTE targeting is not a fifth way to identify an average
treatment effect — it's a different estimand entirely (individual-level heterogeneous effects
used for ranking/targeting), and it is typically *built on top of* one of the four identification
strategies (or an RCT), not a peer alongside them. A "Qini curve" assumption-check section would
not be validating a threat to *identification* the way the other four do — it would be validating
*ranking quality*, which is a model-evaluation question, structurally closer to what
`model-evaluation-viz.md` already does for classifiers (ROC/PR/calibration) than to what this
file does for identification designs. Grafting it in, even under assumption-check framing, would
smuggle in a second chart family (targeting/ranking evaluation) under cover of matching the
existing four's structure — which is exactly the scope-creep risk I flagged in Round 1, just
dressed more convincingly.

There's also an asymmetry in *how* each promise was made that supports treating them differently,
independent of the family-fit argument above: IV's promise is made **from inside the file**, in
its own Presentation Order table, naming IV as one of four identification strategies the file
already treats symmetrically — that's the file making a promise about its own declared scope.
Uplift's promise is made **from outside the file**, in a one-line `SKILL.md` description that
reads as loose/summary phrasing rather than a scoped commitment (`SKILL.md`'s one-liner also says
"DiD, event-study" — not RDD, not PSM, not IV — so it was never trying to be an exhaustive
content manifest; "uplift" reads like drift from an earlier draft, not a deliberate scope
statement). A promise a file makes about itself carries more weight than a summary line elsewhere
getting one word wrong.

### Verdict on the standard itself

This is not two competing framings needing reconciliation — it's one standard ("does the
promised content belong to the family the file already covers, and was the promise made with
file-internal authority") applied to two different fact patterns that come out differently. I
confirm both verdicts without modification:

- **T23 — write the section.** IV shares the file's existing estimand family (average-effect
  identification-design validation) and was promised by the file's own internal table.
- **Uplift — remove the promise.** Uplift belongs to a different estimand family (individual-
  level targeting/ranking) and was promised only by an external, non-authoritative summary line.

**Confidence: high** on both, unchanged from Round 1. This was a genuine stress test (I looked
for the strongest version of the counter-case, not a token one) and it didn't move the
conclusion.

### One coordination note surfaced by this analysis (execution sequencing, not a verdict change)

`SKILL.md`'s Resources line currently reads `causal-inference-charts.md — uplift, DiD,
event-study charts`. Two of this round's fixes touch the *same line*: T23 adds an IV section to
the target file (which may warrant updating this summary line to mention IV, though that's a
"nice to have," not a broken promise — the line was never exhaustive), and the uplift fix removes
"uplift" from it. Whoever executes both should do this as **one edit**, not two independent
passes that could conflict or leave the line in an odd intermediate state (e.g., don't let one
executor remove "uplift" leaving "DiD, event-study" and a separate executor add "IV" in an
unrelated pass without checking the other happened).

---

## Resolution 3 — Cross-check: does deleting `ACCENT_BLUE` orphan `pre-attentive-attributes.md`'s "Accent 2" line?

**Yes — this is a real, newly-identified gap, and it does need a companion edit. This is the
main new finding from this round's cross-check.**

### Why this table is different from ordinary prose guidance

I re-read `pre-attentive-attributes.md`'s "Gray Palette Strategy" block (lines 93–113) against
`SWD`'s actual constants and found it is not loose design theory that happens to echo some code —
it is a **literal, currently-complete 1:1 legend** for the class:

| Table row | `SWD` constant |
|---|---|
| Background: white | `BACKGROUND` |
| Grid / borders: near-invisible light gray | `GRID` |
| Context data: light gray | `GRAY_LIGHT` |
| Secondary text: mid gray | `GRAY_MED` |
| Primary text: near-black | `NEAR_BLACK` / `GRAY_DARK` |
| Accent 1: one bold color — THE focus | `ACCENT` |
| Accent 2: a second color — only for a direct comparison point | `ACCENT_BLUE` |
| Negative: coral/vermillion | `ACCENT_NEGATIVE` |
| Positive: blue | `ACCENT_POSITIVE` |

Every single row currently has a matching constant. This isn't a coincidence — `ACCENT_BLUE`'s
own inline comment (`# blue — second emphasis (use sparingly)`) is near-verbatim to the table's
own language ("a second color — only for a direct comparison point"), which is strong internal
evidence the table was written as (or has been maintained as) a spec that `swd_style.py`
implements line-for-line, not a general essay that independently happens to overlap with the
code.

Deleting `ACCENT_BLUE` without touching this line breaks that previously-perfect mapping and
leaves "Accent 2: a second color — only for a direct comparison point" describing a code
constant that no longer exists. That is exactly the "chart-framework concept with no
corresponding code" pattern the chairman asked about — and per the council's own T16/T17/T23
standard (promised content needs a matching landing spot), I don't think this can be waved off as
"prose is allowed to exist independently of code," because unlike a generic design-principle
aside, this specific line is doing double duty as a legend entry with a 1:1 track record. The
bar for "prose may stand alone" should be reserved for lines that were never functioning as a
spec-to-implementation mapping in the first place (e.g., generic advice like "use gridlines
sparingly" that no constant could ever "match"). This line doesn't qualify for that exemption —
it's part of a table where every other row does have a match, which is what makes its post-
deletion state conspicuous rather than merely abstract.

### Fix — do not delete the row; reword it

I recommend keeping the "Accent 2" row (the underlying design principle — limit yourself to at
most one comparison accent alongside the main one, and verify it before combining hues — is valid
guidance independent of whether a canned constant exists for it) but rewording it so it stops
implying a ready-made, pre-verified constant backs it:

> `Accent 2:       a second color for a direct comparison point — swd_style.py has no preset
> for this; pick one and verify it (e.g. run it through the same CVD-simulation check
> ACCENT_POSITIVE/ACCENT_NEGATIVE received) before pairing two accent hues on one chart, or reuse
> ACCENT_POSITIVE/ACCENT_NEGATIVE directly if the comparison is a goal/loss framing.`

This keeps the table's remaining rows accurate (still 1:1 where a constant exists), stops
promising a nonexistent constant, and gives the reader an actionable path instead of a dead end.

**Confidence: high** that the gap exists and needs fixing (the 1:1-mapping evidence is
mechanical and unambiguous). **Medium** on the exact replacement wording (untested by the other
two lenses this round).

### Rest of the cross-check — no further new inconsistencies found

I re-swept all three Round-1 files' proposed fixes against the rest of the skill for
second-order breakage:

- **T20 fix** (pointer replacing the 3-map inline list in `publication-guidelines.md`): all
  three lenses converge on the same direction. No other file references that specific 3-map
  subset; my Round-1 skill-wide grep for every diverging-map name already confirmed no other
  drift sites exist. No new inconsistency.
- **T19 fix** (add `errors`/`yerr` params to `plot_ablation`/`plot_leaderboard`): the only
  external pointer to these functions is `SKILL.md`'s "Color and Statistical-Honesty Reference"
  paragraph, which already claims (inaccurately, until this fix lands) that
  `data-visualization.md` covers "showing uncertainty honestly." Once T19 is fixed, that claim
  becomes true — no further edit needed to `SKILL.md` itself.
- **T22 fix** (rewrite the CVD-subtype prevalence list): re-grepped the entire skill for
  "Deuteranopia," "Protanopia," "Tritanopia," "~5%," "~2%" — the disputed figures appear in
  exactly one place, `references/color-palettes.md` lines 203–205. No other file duplicates or
  depends on the specific per-subtype numbers being corrected; the skill-wide aggregate "~8%"
  figure used elsewhere is (per both my Round-1 check and member_color's) internally consistent
  with the corrected breakdown and needs no changes. No new inconsistency.
- **T23 + uplift fixes**: see the coordination note in Resolution 2 — both land on the same
  `SKILL.md` line and should be executed together.
- **T21 fix**: the only place besides `swd_style.py` itself referencing `ACCENT_BLUE` or the
  "Accent 2" concept is `pre-attentive-attributes.md` (handled above) and historical council
  records (`debate_log.md`, `round1_member_color.md`, this round's own files) — those are
  investigation artifacts, not shipped skill content, and don't need editing.

No other undiscovered cross-file breakage found from executing any of this round's proposed
fixes.

---

## Final consolidated table — execution-ready

| Topic | Final verdict | Final fix | Confidence |
|---|---|---|---|
| T19 | Confirmed — docstring/body mismatch in `plot_ablation` and `plot_leaderboard` | Add optional `errors_data`/`errors` params plumbed through as `yerr`/`xerr` with explicit `capsize` (member_code's verified-against-matplotlib-3.10.8 implementation); update both docstrings to match. Optional non-blocking polish: adjust `plot_leaderboard`'s value-label offset so it doesn't collide with error caps. | High |
| T20 | Confirmed — stale 3-map subset, 3rd recurrence of the T11 drift pattern | Replace `publication-guidelines.md` line 26's inline `RdBu, PuOr, BrBG` list with a pointer to `color-palettes.md`'s Colorblind-Safe Diverging Maps table (matching the pointer convention already used one line above for the categorical/qualitative case); keep 2–3 example names inline for skimmability if desired, but the list must not claim to be exhaustive. | High |
| T21 | **Revised**: delete `ACCENT_BLUE` (converged, unanimous across all three lenses) | (1) Delete `SWD.ACCENT_BLUE`. (2) Reword `pre-attentive-attributes.md`'s "Accent 2" row so it stops promising a nonexistent preset constant (see Resolution 3 for suggested text). (3) Add a short docstring/comment distinguishing `ACCENT` from `ACCENT_POSITIVE`/`ACCENT_NEGATIVE`. (4) Non-blocking follow-up, not required this round: consider darkening `ACCENT` for contrast (member_color's finding, pre-existing property, not a regression). | High on (1)/(2)-necessity/(3); Medium on (2)'s exact wording |
| T22 | Confirmed (color lens's finding) — prevalence figures mislabel deuteranomaly/protanomaly numbers as deuteranopia/protanopia | Adopt member_color's corrected 5-row breakdown (Deuteranomaly ~5%, Protanomaly ~1%, Deuteranopia ~1%, Protanopia ~1%, Tritanopia/Tritanomaly ~0.01%), explicitly reconciling to the skill-wide "~8%" aggregate already used elsewhere. Single-file fix, `color-palettes.md` only. | High |
| T23 | Confirmed, unchanged after stress test — gap is real and total | Write `## 6. IV First-Stage Diagnostic`, matching the depth/template of the other four sections (Use when / Required inputs / Key design decisions), covering weak-instrument risk and a conventional F-statistic threshold (Staiger-Stock F > 10 rule-of-thumb or a Stock-Yogo pointer). Coordinate with the uplift fix below — both touch `SKILL.md`'s Resources line. | High |
| NEW: uplift promise | Confirmed, unchanged after stress test — different estimand family, promise made only externally (not the file's own table) | Remove "uplift" from `SKILL.md`'s `causal-inference-charts.md` Resources one-liner. Do not add an Uplift/Qini section — even the friendliest assumption-check framing would smuggle in a second chart family (ranking/targeting evaluation) that doesn't match this file's identification-design-validation frame. Execute together with T23's `SKILL.md` line touch. | High |

---

## Unresolved after this pass

**None.** All three chairman-flagged tensions have definitive, final calls:

1. T21 — delete `ACCENT_BLUE` (revised from my Round-1 "keep and document"), plus a necessary
   companion edit to `pre-attentive-attributes.md`'s "Accent 2" row that no prior round had
   surfaced.
2. T23/uplift — both verdicts confirmed unchanged; the differing outcomes reflect one consistent
   standard (estimand-family fit + who made the promise), not two competing ones. One execution-
   sequencing note added (shared `SKILL.md` line).
3. Full fix-set cross-check — one new interaction found (T21 → `pre-attentive-attributes.md`),
   everything else confirmed clean.

The council has a single, non-contradictory recommendation per topic going into execution.
