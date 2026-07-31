# Round 4.2 — member_color Consolidated Findings (Cross-Critique)

**Lens:** color science / accessibility. **Inputs read in full this pass:**
`round4_1_member_code.md`, `round4_1_member_color.md` (my own Round 1), `round4_1_member_standards.md`,
plus a fresh re-read of `assets/swd_style.py` lines 1–40 and
`references/pre-attentive-attributes.md`'s Gray Palette Strategy table to verify claims directly
rather than trust prior summaries. No skill files edited — investigation only.

All three Round 1 reports agree on the underlying facts for T19–T23; the disagreements are about
*disposition*, not *diagnosis*. This round resolves the two disposition tensions the chairman
flagged, confirms T22's final text, and gives a final per-topic verdict from this lens.

---

## Tension 1 — Delete `ACCENT_BLUE`, or keep-and-verify it?

**Verdict: DELETE. This is a definitive call, not a lean.**

### Re-verified facts (grepped fresh, not trusted from Round 1 summaries)

- `assets/swd_style.py:26`: `ACCENT_BLUE = '#1A77B5'   # blue — second emphasis (use sparingly)`.
  Zero other occurrences of `ACCENT_BLUE` anywhere in `assets/swd_style.py` or the rest of
  `skills/visualization/` — confirmed via fresh grep across the whole skill directory, not just
  the file. Genuinely zero call sites, matching both member_code's and my own Round 1 finding.
- `references/pre-attentive-attributes.md:101–106`, the Gray Palette Strategy table, reads:
  ```
  Accent 1:       one bold color — THE focus, use once per chart
  Accent 2:       a second color — only for a direct comparison point
  Negative:       coral/vermillion — financial loss, error states only
  Positive:       blue — goal achieved, up vs target only
  ```
  This is the row member_standards cites as `ACCENT_BLUE`'s documented justification. Important
  wrinkle I confirmed by reading it directly: **the "Accent 2" row names no hex value and no
  specific color** — unlike the Negative/Positive rows two lines below it, which do name
  "coral/vermillion" and "blue" respectively (and which map to the *actually-verified*
  `ACCENT_POSITIVE`/`ACCENT_NEGATIVE` pair). "Accent 2" is an abstract role description, not a
  citation for `#1A77B5` specifically. Keeping `ACCENT_BLUE` doesn't operationalize a concrete
  documented color choice — it operationalizes an abstract slot that any hex could fill, and no
  code currently fills it.

### Answering the chairman's specific sub-question: is the coral/blue pair actually CVD-safe?

I ran a real (if simplified) simulation rather than reasoning by analogy alone, since "probably
fine by category" isn't the bar this skill applies elsewhere (T7 used an actual verification for
`ACCENT_POSITIVE`/`ACCENT_NEGATIVE`).

**Method:** converted both hexes to linear-light RGB via the standard sRGB EOTF, then applied a
standard deuteranopia simulation matrix (linear-RGB, the Brettel/Viénot-derived form used by most
CVD-simulation libraries):
```
R' = 0.367 R + 0.861 G − 0.228 B
G' = 0.280 R + 0.673 G + 0.047 B
B' = −0.012 R + 0.043 G + 0.969 B
```
- `ACCENT` coral `#E8664A` → linear RGB ≈ (0.807, 0.133, 0.069) → deuteranope-simulated ≈
  **(0.395, 0.319, 0.062)** — reads as yellow-olive/tan.
- `ACCENT_BLUE` `#1A77B5` → linear RGB ≈ (0.010, 0.185, 0.462) → deuteranope-simulated ≈
  **(0.057, 0.149, 0.456)** — stays blue.

The two simulated colors remain well separated (Euclidean distance ≈0.55 in a 0–1 linear-RGB
cube), and critically the B channel — driven by the S-cone, which is intact in deutan/protan
CVD — stays ~7x higher for the simulated blue than the simulated coral. This is the same
mechanism that makes Okabe-Ito's blue/vermillion pair (`#0072B2`/`#D55E00`) safe, and it holds
here too: coral and blue differ enough in both the surviving blue-channel signal and starting
luminance that a red-green dichromat should still tell them apart. Protanopia would show the same
qualitative separation (same confusion-line family); tritanopia (~0.01%, both channels affected
differently) is a non-issue here since the two colors also differ hugely in the R channel
(0.81 vs 0.01 linear), which tritanopia doesn't touch.

**So: if kept, the coral/blue pair would very likely pass a real CVD-pair check.** This is a
genuine, useful finding — but it does not change my delete recommendation, for a reason
orthogonal to CVD-safety:

### Why delete anyway

1. **Zero live callers.** This repo has an explicit precedent for exactly this situation — the
   T10 ruling on `simulate_deuteranopia`: *"either implement for real or delete, don't leave a
   no-op that looks functional."* An unused color constant that *would* pass verification if used
   is still, today, unverified-and-unused code. The right sequencing is: add it back with its
   real hex re-confirmed at the time a caller actually needs a second accent, not carry an idle
   constant now on the theory that it already would pass if asked.
2. **No concrete documentation ties `#1A77B5` specifically to "Accent 2."** As shown above, the
   prose row is abstract. Deleting the constant loses nothing concrete from the docs; nothing in
   `pre-attentive-attributes.md` needs to change.
3. **Keeping it perpetuates the exact "which blue is 'the' blue" confusion member_standards
   independently flagged** — `ACCENT_BLUE` (`#1A77B5`) sitting unused next to the verified
   `ACCENT_POSITIVE` (`#0072B2`, also blue) is a maintenance trap regardless of whether either one
   individually is CVD-safe. Deleting the dead one removes the trap outright rather than requiring
   a new docstring to permanently manage the ambiguity.

**This closes the question. My recommendation to the council: delete `ACCENT_BLUE`, no
CVD-verification comment needed in the deletion commit** (the constant being removed makes the
verification moot) — but if the council overrides this and keeps it, the record now shows the
coral/blue pair is very likely CVD-safe by the simulation above, so keeping it would not need to
block on a color-science objection, only on someone writing the concrete "second accent" caller
and a short comment citing this check.

**Confidence: high** on the delete verdict (dead code, no concrete doc requirement blocks
deletion). **Medium-high** on the CVD-pair-safety finding itself (methodologically sound
simplified-matrix simulation, consistent with the established blue/vermillion precedent in this
same file, but not a run through an authoritative tool like Coblis/colorspacious — flagging that
gap honestly rather than overstating certainty).

---

## Tension 2 — Final hex value for `ACCENT`

**Verdict: neither `#E69F00` nor `#D55E00`. Final recommendation: `#C0392B`.**

### `#E69F00` fails badly — this needs to be corrected, not adopted

I computed WCAG contrast for `#E69F00` (Okabe-Ito orange) using the same relative-luminance
method as my Round 1 `ACCENT` table:

| Comparison | Contrast ratio | Passes 3:1 (non-text minimum)? |
|---|---|---|
| `#E69F00` vs. white | **2.25:1** | **No** |
| `#E69F00` vs. `GRAY_LIGHT` `#CCCCCC` | **1.40:1** | **No, badly** |

This is worse than the color it would replace — current `ACCENT` (`#E8664A`) is 3.27:1/2.03:1,
already thin but clearing the white-background minimum. `#E69F00` clears neither. This is a real
and important correction to member_code's proposal: strong CVD pedigree (Okabe-Ito palette
membership) does not imply good contrast — orange/yellow hues are perceptually light, so they
sit close to white in luminance regardless of hue-safety. **`#E69F00` should not be adopted.**
Sanity check on the mechanism: this is the same reason pure yellow (`#FFFF00`) is a notoriously
bad accent-on-white choice (~1.07:1) — `#E69F00` is a less extreme case of the same problem.

### `#D55E00` (`ACCENT_NEGATIVE`'s vermillion) — technically better, but creates a naming collision

Per my Round 1 table: 3.87:1 vs. white, 2.41:1 vs. `GRAY_LIGHT`. Better than current `ACCENT`, but
still **under 3:1 against `GRAY_LIGHT`** — doesn't fully solve the contrast problem — and it
would make `ACCENT` and `ACCENT_NEGATIVE` byte-identical hexes under two different names, which
directly reproduces the "two constants, one color, unclear why they're separate" trap member_
standards flagged for `ACCENT`/`ACCENT_BLUE`, except now for a color that the class comment
explicitly restricts to "financial loss, error states only" (line 31). A general-purpose "the ONE
thing that matters" accent silently sharing vermillion's exact hex risks a reader inferring
semantic meaning ("this chart's accent means something went wrong") that isn't intended.
**Rejecting `#D55E00` for `ACCENT` on these two grounds** (incomplete contrast fix + semantic
collision), even though it would be a defensible fallback if the council wants zero new hexes in
the file.

### Final answer: `#C0392B`

I computed contrast for a candidate that keeps `ACCENT` in the same warm red/coral family (so the
"coral accent" identity in the class comment stays true) but pulled deeper/more saturated to fix
the luminance problem — `#C0392B` (a standard, widely-documented deep red, sometimes called
"Pomegranate" in flat-UI palettes):

| Comparison | Contrast ratio | Passes 3:1? |
|---|---|---|
| `#C0392B` vs. white | **5.44:1** | Yes, comfortably (clears the 4.5:1 text minimum too) |
| `#C0392B` vs. `GRAY_LIGHT` `#CCCCCC` | **3.39:1** | Yes |

This solves the actual problem (`ACCENT`'s contrast against its own paired `GRAY_LIGHT` base
color, the real accessibility defect I found in Round 1) without inheriting `#E69F00`'s
contrast failure or `#D55E00`'s naming collision. On CVD: per the reasoning established in Round
1 and re-confirmed under Tension 1's simulation above, a **single accent shown only against
neutral gray/white does not need CVD-pair verification** — CVD is a hue-discrimination deficit
between two simultaneous hues, not a single-hue-vs-neutral problem, which is governed by
luminance contrast (what the table above tests). Since `ACCENT_BLUE` is being deleted (Tension 1),
there is no live two-hue scenario left for `ACCENT` to be verified against — contrast is the
correct and sufficient bar here.

One residual note, not a blocker: `#C0392B` reads as a straightforward "red," and red carries a
soft cultural association with "negative/danger" that could mildly compete with `ACCENT`'s
documented neutral "the ONE thing that matters" role (distinct from `ACCENT_NEGATIVE`'s explicit
negative-only semantic). I don't think this rises to a real problem — the hue is visibly distinct
from `ACCENT_NEGATIVE`'s orange-leaning vermillion (`#D55E00`, hue angle ~24°) vs. `C0392B`'s true
red (~6°), and `ACCENT_NEGATIVE` isn't wired as any function's default in this file, so the two
won't appear side-by-side by default — but I'm flagging it so the standards/design lens can weigh
in if they see it differently. If the council wants a color further from the "red = bad"
connotation while keeping the contrast fix, any hue clearing ≥3:1 against both white and
`#CCCCCC` and staying visually distinct from `#0072B2`/`#D55E00` would satisfy the same
constraint — I'm not wedded to this exact hex, just providing one concrete, computed, working
answer as asked.

**Confidence: high** on the contrast math (same verified method as Round 1, redone carefully by
hand for both new candidates). **High** on rejecting `#E69F00`. **Medium-high** on `#C0392B` as
the specific final pick (the contrast/CVD reasoning is solid; the exact hue choice among all
hexes satisfying the two constraints is a legitimate design taste call, flagged as such).

---

## T22 — Final text confirmation

**Confirmed final, high confidence, no residual uncertainty that should block shipping this
correction.** Re-checked my Round 1 sourcing:

- Four independent sources converge on the same breakdown: Colour Blind Awareness (citing Sharpe,
  Stockman, Jägle & Nathans 1999), Colblindor/color-blindness.com, National Eye Institute (NIH),
  and the Hereditary Ocular Diseases database (U. Arizona) all give deuteranomaly ~5%,
  protanomaly ~1%, deuteranopia ~1%, protanopia ~1%, tritanomaly+tritanopia ~0.01% (males).
- Internally consistent with this skill's own "~8% of males" aggregate figure used in
  `style-guide.md`, `pre-attentive-attributes.md`, `design-principles.md`,
  `publication-guidelines.md`, and `color-palettes.md`'s own "Common Mistakes" section
  (5+1+1+1≈8) — the fix doesn't touch that figure, it only corrects how one section unpacks it.
- The one honest caveat, already noted in Round 1 and not new: these are historically
  Caucasian-male-population-derived epidemiological figures; prevalence varies somewhat by
  ancestry (e.g., red-green CVD is measurably rarer in populations of African and East Asian
  descent). This doesn't undermine the fix — the current wrong numbers have the same
  unstated-population caveat and the doc isn't claiming population-specific precision either way
  — but if the standards lens wants maximal rigor, a one-clause "(figures vary somewhat by
  ancestry)" could be added. Not required for this fix to ship.

**Final replacement text (unchanged from Round 1, restating as final):**
```
- **Deuteranomaly** (~5% of males): Green-weak (anomalous trichromacy) — the most common CVD;
  green hues appear shifted/muted, not indistinguishable
- **Protanomaly** (~1% of males): Red-weak (anomalous trichromacy) — similar, milder shift
- **Deuteranopia** (~1% of males): Green-blind (dichromacy) — cannot distinguish red from green
- **Protanopia** (~1% of males): Red-blind (dichromacy) — cannot distinguish red from green
- **Tritanopia/Tritanomaly** (~0.01% combined, both sexes): Blue-yellow confusion; rare and
  autosomal (unlike the X-linked red-green types above)

Combined, deuteranomaly + protanomaly + deuteranopia + protanopia account for the skill's
"~8% of males" figure used elsewhere in this reference set.
```
No changes from Round 1. Ready to ship as a high-confidence fact correction.

---

## Per-topic final verdicts (T19–T23, plus NEW)

| Topic | Final verdict (my lens) | Confidence | Notes |
|---|---|---|---|
| **T19** — docstring/body uncertainty-display gap | Not color-relevant. Confirmed no color-logic angle (checked both functions for anything that fakes uncertainty via color intensity — found none; plain Okabe-Ito cycling and accent-vs-baseline patterns, both fine). | N/A | Defer entirely to code lens; no objection to member_code's proposed `yerr=`/`xerr=` fix. |
| **T20** — stale 3-map diverging subset in `publication-guidelines.md` | Agree unanimously with both other members: replace the inline 3-map list with a pointer to `color-palettes.md`'s authoritative 6-map table, matching the pattern already used one line above in the same file for the categorical case. All 6 maps remain independently verified from the T11 fix; this is a doc-structure fix, not a re-verification. | High | No disagreement across all three Round 1 reports — treat as settled. |
| **T21** — `ACCENT`/`ACCENT_BLUE` | **Delete `ACCENT_BLUE`** (Tension 1 above). **Change `ACCENT` to `#C0392B`** (Tension 2 above). Reject `#E69F00` (fails contrast) and `#D55E00` (incomplete contrast fix + naming collision with `ACCENT_NEGATIVE`). No CVD-pair verification work needed for `ACCENT` post-fix since it's single-accent-vs-neutral only. | High (delete) / Medium-high (hex pick) | Both tensions now have a definitive call each; see full reasoning above. |
| **T22** — CVD subtype prevalence figures | Confirmed final text as drafted in Round 1, high confidence, sources solid. | High | See confirmation above. |
| **T23** — missing IV first-stage section | Not color-relevant, agree with both other members it's a structural content gap (same class as T16/T17). If the section is written, it should follow the file's existing accent-vs-gray convention (already used consistently in all 5 present sections) — I'd expect this by default, not something needing enforcement. | N/A | No objection to member_standards' recommendation to write the section rather than soften the table. |
| **NEW** — `SKILL.md`'s "uplift" promise in `causal-inference-charts.md` | Not color-relevant. No comment on the scope-fit judgment (write vs. remove) — that's a content-scope call, not a color one. | N/A | Confirmed via the file's existing color conventions (accent-vs-gray) that nothing color-specific would need to change either way. |

---

## Outstanding items after this pass

1. **T21 hex pick (`#C0392B`) is a concrete, verified-by-me answer but still a design-taste
   choice among several hexes that would satisfy the same two constraints** (≥3:1 contrast
   against both white and `#CCCCCC`; visually distinct from `#0072B2`/`#D55E00`). If the
   chairman or standards lens has a strong preference for staying closer to the original coral
   hue angle (vs. my pick, which shifts toward true red), that's a legitimate alternative within
   the same constraints — flagging so it isn't read as the only possible answer, just the one I'm
   committing to.
2. **The coral/blue CVD-pair-safety finding under Tension 1 is a simplified-matrix simulation,
   not an authoritative-tool run** (e.g., Coblis, colorspacious with a real image render). I'm
   confident enough in it to state the pair is "very likely safe," but if `ACCENT_BLUE` is kept
   despite my delete recommendation, I'd want an actual tool-based check before calling that
   fully closed rather than resting on hand-derived matrix math alone.
3. **Minor residual, flagged not blocking:** `#C0392B`'s hue reads as "red," which has a soft
   negative connotation that could mildly compete with `ACCENT`'s neutral "the ONE thing that
   matters" role. Not rising to a real problem given `ACCENT_NEGATIVE` isn't wired as a default
   anywhere in the file, but noted for the standards/design lens in case they weigh it
   differently.
4. **No disagreement remains on T20, T22, T23, or the NEW uplift finding from this lens** — those
   are ready to move forward per the verdicts above.
