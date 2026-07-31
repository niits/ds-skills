# Round 4.1 — member_color Findings

**Lens:** color science / accessibility (colorblind-safety claims, CVD prevalence statistics,
colormap/palette accuracy, contrast/accessibility correctness).

**Prior context reviewed:** full `debate_log.md`, including T2 (Wong/Okabe-Ito duplication,
RdYlBu/PRGn/PiYG safety), T7 (red/green contradiction fix — `ACCENT_POSITIVE`/`ACCENT_NEGATIVE`
Okabe-Ito pair added to `swd_style.py`, `pre-attentive-attributes.md`'s Gray Palette Strategy
rewritten), and T11 (diverging-safe list reconciled to 6 maps across `color-palettes.md` and
`color_palettes.py`, with sync comments added to both). All three are confirmed still resolved
on disk — no regressions found while reading the current files for this round.

---

## T22 — CVD subtype prevalence figures (PRIMARY FOCUS)

**Confidence: HIGH.**

### Finding

`references/color-palettes.md`'s "Types of Color Vision Deficiency" section is wrong on both
red-green rows, and wrong in a specific, identifiable way: it has attached the **anomalous-
trichromacy** (color-*weak*) prevalence numbers to the **dichromacy** (color-*blind*) subtype
names.

Current text:
```
- **Deuteranopia** (~5% of males): Cannot distinguish green
- **Protanopia** (~2% of males): Cannot distinguish red
- **Tritanopia** (<1%): Cannot distinguish blue (rare)
```

### What the literature actually says

Converging across multiple independent sources (Colour Blind Awareness — citing Sharpe, Stockman,
Jägle & Nathans 1999; Colblindor/color-blindness.com; National Eye Institute; Hereditary Ocular
Diseases database at U. Arizona), the standard breakdown of the ~8% of males with inherited
red-green CVD is:

| Subtype | Type | Prevalence (males) | Severity |
|---|---|---|---|
| Deuteranomaly | Anomalous trichromacy (green-**weak**) | **~5%** | Mild–moderate; most common CVD overall |
| Protanomaly | Anomalous trichromacy (red-**weak**) | **~1%** | Mild–moderate |
| Deuteranopia | Dichromacy (green-**blind**) | **~1%** | Severe — true "cannot distinguish" |
| Protanopia | Dichromacy (red-**blind**) | **~1%** | Severe — true "cannot distinguish" |
| Tritanomaly + Tritanopia | Blue-yellow, both anomalous + dichromacy | **~0.01%** (roughly 1 in 10,000) | Rare, autosomal — affects both sexes ~equally, unlike the X-linked red-green types |

Sum: 5 + 1 + 1 + 1 ≈ 8%, matching this same skill's own "~8% of males" figure used consistently
in `style-guide.md`, `pre-attentive-attributes.md`, `design-principles.md`,
`publication-guidelines.md`, and this same file's own "Common Mistakes" §2. That "~8%" aggregate
figure is correct and doesn't need touching — the bug is entirely in how this one section breaks
the 8% down by subtype.

### Diagnosis of each sub-claim in the prompt

**(a) Is "Deuteranopia ~5%" accurate?** No. ~5% is deuteranomaly's prevalence. Deuteranopia
(true dichromacy) is ~1%. The doc has the right number attached to the wrong subtype name.

**(b) Is "Protanopia ~2%" accurate?** No, and it doesn't map onto any single standard figure at
all — the closest match is protanomaly (~1%) + protanopia (~1%) added together (~2%), but that
combined figure is then mislabeled as if it were pure protanopia (which alone is ~1%). This is a
compounding version of the same error as (a): not just a subtype-name swap, but an unlabeled sum
of two subtypes presented as one.

**(c) Does "cannot distinguish green/red" mismatch the actual prevalence numbers being
described?** Yes. "Cannot distinguish" is an accurate description of dichromacy (deuteranopia/
protanopia — true color-blindness, one cone type entirely absent). It overstates deuteranomaly/
protanomaly (anomalous trichromacy — a shifted-sensitivity cone, not a missing one), which is
usually described as reduced discrimination / certain hues appearing shifted or muted, not
complete inability to distinguish. Since the ~5%/~2% figures the doc cites are dominated by the
anomalous-trichromacy population, the "cannot distinguish" framing is too absolute for the
prevalence numbers actually being quoted.

**Tritanopia "<1%"** is directionally not wrong (true prevalence ~0.01% easily clears the "<1%"
bound) but is a very loose upper bound compared to how precisely the other two rows are (falsely)
stated — worth tightening while the section is being rewritten anyway, and worth noting it's
autosomal (affects males and females roughly equally), unlike the X-linked red-green types, which
the current one-line treatment doesn't mention.

### Proposed fix

Prefer **option (a) from the task framing — correct the subtype names** rather than relabeling to
anomalous-trichromacy-inclusive numbers, because the doc already separates rows by subtype (it's
clearly trying to be precise, not just give one combined figure) and the skill's other files
already carry the correct combined "~8%" figure — this section's job is to be the one place that
correctly unpacks that 8%. Suggested replacement:

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

This keeps the section internally consistent with the rest of the skill's "~8%" claim (closes the
loop instead of just replacing one wrong number with another), and downgrades "cannot distinguish"
to the two rows where it's actually accurate.

### Sources
- Colour Blind Awareness — "Types of Colour Blindness" (citing Sharpe, Stockman, Jägle & Nathans,
  1999): breakdown of the 8% as ~1% deuteranopes, ~1% protanopes, ~1% protanomalous, ~5%
  deuteranomalous. https://www.colourblindawareness.org/colour-blindness/types-of-colour-blindness/
- Colblindor / color-blindness.com — "Types of Color Blindness": deuteranomaly ~5%, protanomaly
  ~1%, deuteranopia ~1%, protanopia ~1%, tritanomaly/tritanopia ~0.01%.
  https://www.color-blindness.com/types-of-color-blindness/
- National Eye Institute (NIH) — "Types of Color Vision Deficiency": deuteranopia/protanopia
  described as "unable to tell the difference between red and green at all" (dichromacy);
  deuteranomaly/protanomaly described as shifted-hue perception (anomalous trichromacy), matching
  the same ~5%/~1%/~1%/~1% split. https://www.nei.nih.gov/eye-health-information/eye-conditions-and-diseases/color-blindness/types-color-vision-deficiency
- Hereditary Ocular Diseases (U. Arizona) — corroborates ~1% deuteranopia, ~1% protanopia, ~1%
  protanomaly, ~5% deuteranomaly (Caucasian male population figures, the population most CVD
  epidemiology is historically drawn from — worth a passing caveat if the doc wants to be fully
  rigorous, though not required for this fix).

**Flag for other lenses:** none needed — this is a pure content-accuracy fix, no code touches it.

---

## T20 — `publication-guidelines.md`'s stale 3-map diverging subset (third T11 recurrence)

**Confidence: HIGH.**

### Finding
Confirmed as described: `publication-guidelines.md` line 26 reads `**Diverging (negative to
positive)**: RdBu, PuOr, BrBG (colorblind-safe)`. This is a strict subset of the now-authoritative
6-map table in `color-palettes.md` (`RdYlBu`, `RdBu`, `PuOr`, `BrBG`, `PRGn`, `PiYG`) and
`color_palettes.py`'s `DIVERGING_COLORMAPS_SAFE`. It's not a false-safety claim (the 3 it names
are indeed safe), just an incomplete, un-synced copy — exactly the drift pattern T11 fixed twice
already (doc vs. code in Round 3; the doc's own "Avoid" vs. "Safe" list mismatch before that).

### Why this is likely to recur a 4th time if fixed the same way
T11's fix added one-line sync comments to `color-palettes.md` and `color_palettes.py` pointing at
each other. That worked for those two files, but this third location was never touched and the
repo has no CI to catch drift mechanically (noted explicitly in the Round 3 ruling). Any fix that
hardcodes a third copy of the list — even a "complete" 6-map copy — reopens the same risk the
moment any of the three files is edited again without the other two in hand.

### Proposed fix
Don't duplicate the list a third time. Replace the inline enumeration with a pointer to the
canonical table:

```
- **Diverging (negative to positive)**: colorblind-safe maps only — see
  `color-palettes.md`'s "Colorblind-Safe Diverging Maps" table (e.g. `RdBu`, `PuOr`, `BrBG`)
```

This keeps a couple of example names inline for skimmability (so the line still reads usefully on
its own) but removes the implicit claim that the list is exhaustive, and makes `color-palettes.md`
the single source of truth the other two files already sync against. This is a stronger fix than
another sync-comment pair, since a pointer can't drift out of date the way an enumerated list can.

**Flag for other lenses:** none — straightforward doc edit, no code implication.

---

## T21 — `swd_style.py`'s unverified `ACCENT`/`ACCENT_BLUE` vs. verified `ACCENT_POSITIVE`/`ACCENT_NEGATIVE`

**Confidence: MEDIUM** (the core premise in the debate topic is partly stale; the residual issue
is real but smaller than framed).

### Is a single accent color against gray inherently fine regardless of CVD-verification?

**Yes, as a general color-science matter.** CVD is fundamentally a hue-*discrimination* deficit —
it impairs telling two specific hues apart along a confusion line (red↔green for deutan/protan,
blue↔yellow for tritan). It does not impair perceiving a single color against a neutral
(gray/white/black) background; that discrimination is governed by **luminance contrast**, which
is orthogonal to CVD entirely (a protanope and a color-typical viewer perceive the same luminance
contrast between a hue and gray, roughly speaking — CVD shifts hue perception, not lightness
perception in any comparable way). So "does this single accent color need to be tested against a
colorblind simulator" is close to a non-question when it's only ever shown against neutral gray —
what actually needs checking there is contrast ratio, not CVD-pair-safety. CVD verification only
becomes meaningful the moment **two** data-carrying hues appear together and must be told apart
(which is exactly why `ACCENT_POSITIVE`/`ACCENT_NEGATIVE` needed Okabe-Ito verification under T7 —
those two are designed to appear on the same chart as a positive/negative pair).

### But the debate topic's stated premise needs a correction

I checked whether `ACCENT` and `ACCENT_BLUE` are actually ever used *together* on one chart, which
is the scenario that would require CVD verification. They are not, in the current file:

- `grep` shows `ACCENT_BLUE` has **zero call sites** anywhere in `swd_style.py` or the rest of the
  skill — it is declared (`swd_style.py:26`) and never read. The only function that historically
  paired `SWD.ACCENT` with `SWD.ACCENT_BLUE` was `waterfall_colors()` (per
  `agent_council/rounds/round1_member_color.md:25-26`, which describes it as "a safe coral/blue
  pair, not red/green") — and `waterfall_colors` was one of the four banking-domain helpers
  **already deleted** from this file under the T1 fix (Round 2, per debate_log.md line 67: "cut
  from `swd_style.py`"). So the specific pairing scenario T21 is worried about no longer exists in
  shipped code.
- `ACCENT` itself is used only in two places, both single-accent-vs-neutral patterns:
  `apply_swd_palette` (accent vs. `GRAY_LIGHT`) and `highlight_region` (accent wash vs.
  background). Per the reasoning above, this doesn't need CVD-pair verification.
- `ACCENT_POSITIVE`/`ACCENT_NEGATIVE` (the T7-verified pair) also have **zero call sites** inside
  `swd_style.py`'s own functions — they exist purely as documented constants for a caller to pass
  explicitly (e.g., `label_bars(..., color=SWD.ACCENT_POSITIVE)`), which is a legitimate pattern
  for a color-constants class, but means the "verified pair" and the "unverified pair" are
  currently symmetric in one sense: neither is wired into the six helper functions' *default*
  behavior for the two-hue case.

### The real residual issue: dead code / a confusing near-duplicate, not a CVD-safety bug

`ACCENT_BLUE` is orphaned dead code (only surviving because its one caller, `waterfall_colors`,
was deleted around it rather than deleted with it) and its existence next to `ACCENT_POSITIVE`
creates a "which blue is 'the' blue" maintenance trap the topic correctly identifies — but this is
a code-hygiene finding, not a color-science one. I'd rate it low-severity from my lens and defer
severity/disposition to the code lens.

### One genuine color-science finding I did surface: `ACCENT`'s contrast margin is thin

I computed WCAG relative-luminance contrast ratios (not CVD-specific — this is the general
low-vision/contrast axis, separate from hue-discrimination):

| Color | vs. white | vs. `GRAY_LIGHT` (#CCCCCC) |
|---|---|---|
| `ACCENT` coral `#E8664A` | **3.27:1** | 2.03:1 |
| `ACCENT_BLUE` `#1A77B5` | 4.83:1 | 3.01:1 |
| `ACCENT_POSITIVE` Okabe blue `#0072B2` | 5.19:1 | 3.23:1 |
| `ACCENT_NEGATIVE` Okabe vermillion `#D55E00` | 3.87:1 | 2.41:1 |

`ACCENT` (the coral that's actually the *default* used by `apply_swd_palette`/`highlight_region`)
has the lowest contrast of the four against both white and the class's own `GRAY_LIGHT` — it just
barely clears WCAG's 3:1 minimum for non-text graphical objects against white, and falls under 3:1
against `GRAY_LIGHT` specifically (2.03:1), which matters here because `GRAY_LIGHT` is the
*default base color* `apply_swd_palette` pairs `ACCENT` against. This is a real, independent
accessibility finding — not what T21 asked about, but surfaced by investigating it — and unlike
the CVD-pairing question, this one *is* a legitimate reason to reconsider `ACCENT`'s hex value
regardless of whether `ACCENT_BLUE` sticks around.

### Proposed fix
1. Delete `ACCENT_BLUE` — it's dead code orphaned by the T1 prune, not a currently-reachable
   accessibility concern one way or the other. (Code-lens call on whether dead-constant removal is
   in scope this round; flagging here since I found it while investigating T21.)
2. Optionally strengthen `ACCENT`'s contrast: since it's used as the sole highlight-vs-gray color
   skill-wide, consider moving it closer to `ACCENT_NEGATIVE`'s vermillion (`#D55E00`, 3.87:1 vs.
   white) or otherwise darkening it slightly — this is a contrast fix, not a CVD-safety fix, but
   it's the more substantive of the two accessibility properties actually in play here.
3. No CVD-simulator verification work is needed for `ACCENT` as long as it continues to be used
   only against neutral gray/white (per the reasoning above) — don't spend Round 4 effort
   "verifying" it against a colorblind simulator; that would be solving a problem that doesn't
   exist for this usage pattern.

**Flag for other lenses:** (a) code lens — confirm `ACCENT_BLUE` really has zero call sites
skill-wide before deleting (I only grepped `skills/visualization/`); (b) standards/design lens —
whether adjusting `ACCENT`'s hex value for contrast is worth doing this round vs. deferring, since
it's a real but pre-existing property, not a regression.

---

## T19 — Docstring/implementation gap (code-correctness topic)

**Confidence: N/A (not my lens) — comment only.**

Confirmed by reading `plot_ablation` and `plot_leaderboard` in `data-visualization.md`: both
docstrings promise interval/uncertainty display with no matching parameter or `yerr`/error-bar
code in the body, exactly as described in the debate topic. I checked for a color angle
specifically (e.g., does either function's color logic misrepresent uncertainty, such as using
color intensity to fake a confidence signal) and found none — `plot_ablation`'s color usage is a
plain `OKABE_ITO_LIST[i % len(...)]` per-method cycle (correctly modulo-guarded per the T15 fix),
and `plot_leaderboard`'s is the standard accent-vs-`BASELINE` single-highlight pattern. No
color-accessibility content here; this is purely a statistical-honesty/code-completeness bug for
the code or standards lens to own.

---

## T23 — `causal-inference-charts.md` missing IV first-stage section (structural-gap topic)

**Confidence: N/A (not my lens) — comment only, confirmed not color-relevant.**

Checked the file's color-related content specifically: the four present chart sections use only
the skill's already-established accent-vs-gray/neutral pattern (§1 "neutral color for all
estimates; reserve accent for a prespecified focal estimand," §3 "gray... pre-period" vs. "accent
color... post-period," §5 "distinct color" for the shaded overlap region) — no red/green pairing,
no unverified palette claims, nothing that would change if/when an IV first-stage section is
added. The gap itself is a content-completeness issue (same class as T16), not a color-science
one. If a fix is written, the only color-lens ask would be that the new section follow the same
accent-vs-gray convention already used by the other four — I'd expect that to happen by default
since it's the file's established house style, not something that needs enforcing.

---

## Summary table

| Topic | My confidence | Verdict | Action needed |
|---|---|---|---|
| T19 | N/A | Not color-relevant | None from this lens |
| T20 | High | Real drift, 3rd recurrence | Replace inline 3-map list with pointer to `color-palettes.md`'s table |
| T21 | Medium | Premise partly stale (pairing scenario's only caller was already deleted); real residual issue is dead code + thin contrast on `ACCENT`, not CVD-pairing | Delete dead `ACCENT_BLUE`; consider contrast fix for `ACCENT`; no CVD-simulator work needed |
| T22 | High | Confirmed real error: prevalence figures are deuteranomaly/protanomaly numbers mislabeled as deuteranopia/protanopia | Rewrite the 4-line subtype list with correct names/numbers per the table above; keep skill-wide "~8%" figure as the reconciling total |
| T23 | N/A | Not color-relevant | None from this lens |
