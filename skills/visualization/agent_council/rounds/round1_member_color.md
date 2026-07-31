# Round 1 — Independent Findings: member_color (Color Science & Accessibility lens)

Investigated: `SKILL.md`, every file in `references/`, every file in `assets/` (including
`color_palettes.py`, `style_presets.py`, `swd_style.py`, and all four `.mplstyle` files).
Verified externally via web search: Okabe-Ito (2002) vs. Wong (2011) provenance/hex
values, and ColorBrewer's colorblind-safe flags for RdYlBu / PRGn / PiYG.

---

## T1 — Dangling `banking-visualization` reference & orphaned domain helpers in `swd_style.py`

**Verdict: Not primarily a color issue — but I checked the color choices in the orphaned helpers and they are technically sound, which weakens the case for urgency (not for removal).**

**Evidence:**
- `risk_colormap()` (assets/swd_style.py:253-278) returns `magma` for sequential rate
  data, `PuOr` + `TwoSlopeNorm(vcenter=0)` for change/drift data, and `YlOrRd` for
  volume — all defensible, CVD-tested choices (PuOr is one of the strongest
  colorblind-safe diverging maps; magma/YlOrRd are reasonable sequential picks).
- `psi_status()` (swd_style.py:281-303) returns a 3-step severity scale: green
  `#27AE60` (stable) → orange `#F39C12` (moderate) → coral `#E8664A` (significant).
  This is *not* a red/green pair — it deliberately avoids the classic confusion pair
  by using orange/coral instead of red for escalation. Reasonably safe, though the
  orange↔coral step is close enough in hue that I'd still recommend a redundant
  marker/label (which the docstring already tells callers to report as text).
- `waterfall_colors()` (swd_style.py:316-323) uses `SWD.ACCENT` (coral `#E8664A`) vs.
  `SWD.ACCENT_BLUE` (`#1A77B5`) — a safe coral/blue pair, not red/green.

**Proposed fix:** No color-specific objection to keeping or removing these helpers —
that's an organizational/scope question for other council members. If they stay,
no palette changes needed. If `SKILL.md`'s dangling decision-tree line is fixed,
independently verify it doesn't accidentally point at a palette-unsafe fallback.

---

## T2 — Okabe-Ito vs. "Wong" duplication, and self-contradictory diverging-map safety labels

**Verdict: Confirmed on both counts.**

**Evidence — Okabe-Ito vs. Wong:**
Web search confirms: Okabe & Ito published the 8-color Color Universal Design palette
in 2002 (orange `#E69F00`, sky blue `#56B4E9`, bluish green `#009E73`, yellow
`#F0E442`, blue `#0072B2`, vermillion `#D55E00`, reddish purple `#CC79A7`, black
`#000000`). Bang Wong's 2011 *Nature Methods* "Points of view: Color blindness" column
did not introduce a new/different palette — it **popularized this same Okabe-Ito set**
(dropping black, since Wong's context was plotting on white). Every "Wong" list in this
skill (`references/color-palettes.md:60-69`, `assets/style_presets.py:35`
`WONG_COLORS`, `assets/color_palettes.py:32-33` `WONG`) is byte-for-byte the same 7-8
hex values as `OKABE_ITO`, just reordered (black moved to front in the two Python
files). Presenting "Wong" as an "Alternative for Categories" in
`references/color-palettes.md:55` is misleading: an agent following the skill could
reasonably conclude these are two independently-validated 8-color sets it could
alternate between across a paper's figures, when in fact using both "Okabe-Ito" and
"Wong" in different figures of the same submission is combining the *same* colors under
two names — not a source of additional variety, and reviewers who know the history may
flag it as sloppy.

**Evidence — PRGn/PiYG self-contradiction:**
`assets/color_palettes.py:62-69`:
```python
DIVERGING_COLORMAPS_SAFE = [
    'RdYlBu', 'RdBu', 'PuOr', 'BrBG',
    'PRGn',      # Purple-Green (use with caution)
    'PiYG',      # Pink-Yellow-Green (use with caution)
]
```
Putting a caveat *inside* a list literally named `_SAFE` is self-contradicting — a
caller who does `import DIVERGING_COLORMAPS_SAFE` and picks the first available option
programmatically gets no signal that two of the six need extra scrutiny. This is worse
than cosmetic: my best-available cross-check (ColorBrewer's `colorblind` flag, as
encoded in `RColorBrewer::brewer.pal.info` / colorbrewer2.org) has historically rated
these two *differently* — **PRGn is generally flagged colorblind-safe, PiYG is
generally flagged NOT colorblind-safe** (Purple-Green vs. Pink-Yellow-Green — the
latter's yellow-to-green transition sits closer to the deuteranopia/protanopia
confusion axis). My web search on this point returned inconsistent secondary sources,
so treat the PRGn/PiYG split as "very likely, verify directly against
`colorbrewer2.org` or `RColorBrewer::brewer.pal.info` before shipping a fix" rather than
100% certain — but the file's own uniform "(use with caution)" treatment of both is
already wrong under either reading: either both are safe (caveat should be removed) or
they differ (caveat should be split and PiYG should probably move to
`DIVERGING_COLORMAPS_AVOID` or its own "conditionally safe" tier).

**Evidence — RdYlBu claim:** Confirmed correct. RdYlBu is a standard ColorBrewer
colorblind-safe diverging map (grouped with BrBG, PuOr, RdBu as safe; RdGy, RdYlGn,
Spectral are the ones ColorBrewer flags unsafe). No fix needed for that specific claim
in `references/color-palettes.md:135-144`.

**Proposed fix:**
1. In `references/color-palettes.md`, rewrite the "Wong Palette" section to state
   plainly: "Wong (2011, *Nature Methods*) popularized the Okabe-Ito (2002) palette —
   same colors, not a second option. Use `OKABE_ITO` as the canonical name; treat 'Wong
   palette' as a historical/citation synonym, not an alternative to switch to for
   variety." Do the same in the docstrings of `color_palettes.py` and
   `style_presets.py` (currently `style_presets.py:34` just says "# Wong palette" with
   no clarification).
2. In `color_palettes.py`, verify PRGn vs. PiYG against `RColorBrewer::brewer.pal.info`
   or colorbrewer2.org directly, then either (a) remove the "(use with caution)"
   comment if both check out safe, or (b) split them — keep PRGn in
   `DIVERGING_COLORMAPS_SAFE`, move PiYG to a distinct tier or to
   `DIVERGING_COLORMAPS_AVOID` with an explanatory comment.

---

## T3 — "Ocean Dusk" default palette contradicts the skill's colorblind-safety rule

**Verdict: Confirmed — and worse than the debate topic implies. This is not just a framing problem; the palette contains a specific, checkable CVD failure.**

**Evidence:** `references/data-visualization.md:52-61`:
```python
COLORS = {
    "teal":   "#264653",
    "cyan":   "#2A9D8F",
    "gold":   "#E9C46A",
    "orange": "#F4A261",
    "coral":  "#E76F51",
    "blue":   "#0072B2",   # Okabe-Ito accessible blue
    "sky":    "#56B4E9",   # Okabe-Ito accessible sky
    "gray":   "#8C8C8C",
}
```
Three of the eight colors — gold `#E9C46A` (233,196,106), orange `#F4A261`
(244,162,97), coral `#E76F51` (231,111,81) — form a near-monotonic sequence that
differs almost entirely by decreasing green channel (196 → 162 → 111) at roughly
constant red. That is exactly the axis destroyed by deuteranopia/protanopia (red-green
CVD, ~8% of men): under a deuteranopia simulation these three collapse toward the same
perceived hue, differing mainly by a lightness gradient that is easy to misread as
"three shades of the same category" rather than three distinct categories. This is a
concrete, verifiable failure, not a hypothetical — I'd expect a Coblis/Color Oracle
simulation to show gold/orange/coral as substantially harder to tell apart than the
other five colors in this set. The file's own inline comments implicitly concede this:
only `blue` and `sky` are annotated "Okabe-Ito accessible," which silently signals the
other six (including the 3 problem colors) were not vetted the same way — exactly the
contradiction the debate topic flags, and my simulation-based reasoning confirms the
underlying palette is not safe, not merely "unlabeled."

Also note `references/data-visualization.md` never states a rule like "COLOR_LIST is
default; substitute OKABE_ITO for accessibility-critical venues," so an agent skimming
this file in isolation has no signal to prefer the safe option — it reads "Ocean Dusk"
first, under the heading "(default — professional, distinctive)," a much more
prominent framing than "Okabe-Ito" gets two headings later.

**Proposed fix:**
1. Either (a) replace `gold`/`orange`/`coral` in "Ocean Dusk" with hues verified against
   a CVD simulator (e.g., swap orange for a blue-purple to break the yellow→red
   monotonic run), or (b) demote "Ocean Dusk" from "default" to "aesthetic option for
   ≤2-color highlight use (e.g., `OUR_COLOR` vs. `BASELINE_COLOR`, which only uses
   coral vs. gray and is fine)" and promote `OKABE_ITO` to the actual default for any
   ≥3-category categorical encoding.
2. Make `SKILL.md`'s Goal 2 section and `references/data-visualization.md` agree
   explicitly: `SKILL.md:126` already recommends `set_color_palette("okabe_ito")` as
   the colorblind-safe categorical default — `data-visualization.md` should not
   silently override that with a different, unvetted "default."

---

## T4 — Dead code in `apply_publication_style()`

**Verdict: Not a color-science issue.** No accessibility or perceptual angle — the
unreachable `nature`/`presentation` branches inside `get_base_style()`-derived
`base_style.update(...)` (style_presets.py:161-171, 200-212) don't touch color; they
adjust font sizes and DPI. I confirm the bug exists as described (early return at
style_presets.py:151-156 makes lines 161-171 and 200-212 unreachable for those two
names) but defer to other council members on remediation. One incidental note: the
*unreachable* `nature` branch (line 169) sets `savefig.dpi: 600`, while the *reachable*
`nature.mplstyle` (assets/nature.mplstyle:56) also sets `savefig.dpi: 600` — so the two
diverging definitions happen to agree on DPI even though one is dead. They do NOT
diverge on color (both inherit `OKABE_ITO_COLORS` / the mplstyle's Okabe-Ito cycler),
so at least this particular dead-code trap has not (yet) produced a color-palette
inconsistency, only a font/DPI one.

---

## T5 — Serif vs. sans-serif typography contradiction

**Verdict: Not a color-science issue.** Font family choice doesn't interact with color
perception. No comment beyond confirming it's out of my lens.

---

## T6 — DPI on vector PDF, inconsistent Nature DPI figures

**Verdict: Confirmed as described; from a color-science angle, the DPI bug itself does not create a color-reproduction risk, but there is a real, separate color/print-reproduction gap the skill should address given this section's focus.**

**Evidence:** `dpi` on `fig.savefig(..., format='pdf')` only affects rasterized
sub-elements (e.g., alpha-blended `imshow`/`scatter` rasterization if `rasterized=True`
is set) — vector paths, markers, and text in a PDF store exact color values (RGB
triples or ICC-referenced values) independent of any DPI setting. So the DPI
inconsistency across `matplotlib-examples.md`, `journal-requirements.md`,
`publication-guidelines.md`, and `nature.mplstyle` (flagged by the debate topic) is a
resolution/print-fidelity issue, not a color-fidelity one — I have no color-specific
correction to add to the DPI figures themselves.

What IS a genuine color-reproduction gap, and sits right next to this topic: multiple
files in this skill (`references/color-palettes.md:315-330`,
`references/publication-guidelines.md:71-74`) correctly warn that "colors appear
different in print vs. screen" and recommend CMYK preview, but none of them warn that
the skill's own recommended colorblind-safe hex values were chosen/verified in sRGB —
Okabe-Ito's blue (`#0072B2`) and vermillion (`#D55E00`) are both fairly saturated and
can shift or clip on CMYK conversion for print journals, potentially degrading the very
colorblind-safety property being aimed for. `journal-requirements.md` correctly notes
most journals are RGB/digital-first now, which reduces this risk in practice — but
`publication-guidelines.md:71-74` still tells readers to "convert to CMYK... ensure
sufficient contrast remains" without saying "re-verify colorblind-safety after CMYK
conversion, not just contrast." Minor, but worth a one-line addition given this file
already discusses both DPI and color-space conversion together.

**Proposed fix:** Add one sentence to `publication-guidelines.md`'s CMYK section:
"CMYK conversion can shift or desaturate Okabe-Ito/Wong hues — re-check colorblind
safety with a simulator on the converted proof, not just on the original RGB file."

---

## Additional issues beyond T1–T6

### T7 (new) — Skill-wide contradiction: "red = negative, green = positive" is codified as a rule, directly opposite the skill's own "avoid red/green" rule

**Verdict: Confirmed, and this is the most consequential finding in my review — it is a live, actionable contradiction inside the SWD framework the skill treats as mandatory for every chart ("SWD is always on," `SKILL.md:20`).**

**Evidence:**
- `references/pre-attentive-attributes.md:101-102` (the canonical "Gray Palette
  Strategy" reference, linked from `SKILL.md`'s SWD Framework section) states as a
  documented, prescriptive rule:
  ```
  Negative:       red — financial loss, error states only
  Positive:       green — goal achieved, up vs target only
  ```
  This is a semantic red/green binary — exactly the pairing that
  `references/color-palettes.md:216` ("Don't: Use red/green combinations"),
  `references/publication-guidelines.md:63` ("Avoid red/green combinations"),
  `references/style-guide.md:105` ("Pure red + pure green — indistinguishable for ~8%
  of males"), and `references/design-principles.md:86` ("Is there a red + green color
  pairing as the sole differentiator? → Replace with blue + orange") all tell the
  reader to avoid, in the same skill, in files linked from the same `SKILL.md`.
- `assets/swd_style.py:26-29` hard-codes this into the reusable `SWD` class:
  `ACCENT_GREEN = '#27AE60'   # positive outcome / goal achieved` and
  `ACCENT_RED = '#C0392B'   # negative / loss / critical (financial contexts)` — so an
  agent that imports `SWD.ACCENT_GREEN` for a "goal met" bar and `SWD.ACCENT_RED` for a
  "loss" bar in the *same* chart (which is exactly the documented use case in
  `pre-attentive-attributes.md`) produces a chart that fails for ~8% of male viewers,
  in direct violation of four other files in the same skill.
- Notably, the actual domain helper functions in the same file (`psi_status()`,
  `waterfall_colors()`) do NOT use this red/green pair — they use green vs.
  orange/coral instead (see my T1 notes). So the *code* mostly self-corrects, but the
  *documented rule* in `pre-attentive-attributes.md` and the *class attribute names* in
  `swd_style.py` actively invite a colorblind-unsafe pattern that isn't used anywhere
  else in the skill's own examples — meaning an agent following the letter of
  `pre-attentive-attributes.md` (rather than pattern-matching off the other helper
  functions) would introduce a real accessibility bug.
- `design-principles.md:84-90` gets this right and even offers the correct fix (blue +
  orange, or Okabe-Ito), which makes the contradiction with `pre-attentive-attributes.md`
  more glaring, not less — the skill contains its own correct answer two files away
  from the wrong one.

**Proposed fix:** Rewrite `pre-attentive-attributes.md:101-102` to something like:
```
Negative:       coral/vermillion (e.g. #D55E00 or SWD.ACCENT) — financial loss,
                error states only. Never pair with the Positive color as the sole
                differentiator on the same chart.
Positive:       blue or bluish-green (e.g. #0072B2 or #009E73) — goal achieved, up
                vs target only.
```
And rename or re-document `SWD.ACCENT_RED`/`SWD.ACCENT_GREEN` in `swd_style.py` to
either (a) note explicitly "do not use both on the same chart as the sole
differentiator — pair with SWD.ACCENT_BLUE instead, or add hatching/icons," or (b)
replace `ACCENT_GREEN` with a blue-family "positive" color to match what
`psi_status()`/`waterfall_colors()` already do in practice.

### T8 (new) — `style-guide.md`'s `PALETTE_DEEP` is a false colorblind-safety claim

**Verdict: Confirmed factual error.**

**Evidence:** `references/style-guide.md:63-79`:
```
### Recommended Colorblind-Safe Palette
This palette is distinguishable under all forms of color vision deficiency:

PALETTE_DEEP = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52",
    "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
]
```
These are the exact hex values of seaborn's *default* `"deep"` palette
(`sns.color_palette("deep")`), confirmed via web search against seaborn's source. This
is seaborn's general-purpose aesthetic default — it is a **different, separately-named
palette from seaborn's own `"colorblind"` palette** (which uses Okabe-Ito-family hues:
`#0173B2`, `#DE8F05`, `#029E73`, `#D55E00`, `#CC78BC`, `#CA9161`, `#FBAFE4`, `#949494`,
`#ECE133`, `#56B4E9`). Seaborn's docs and design intent do not claim `"deep"` is
CVD-safe. Concretely, `PALETTE_DEEP` places `#55A868` (a medium forest green) and
`#C44E52` (a muted brick red) third and fourth in the cycle — a green/red pair that is
a documented risk for protanopia/deuteranopia, even muted. Labeling this set "safe...
under all forms of color vision deficiency" is a stronger, more actionable false claim
than T3's "Ocean Dusk" issue, because this section explicitly recommends it *for ML
conference figures* (the file's stated scope) and gives no alternative — an agent
following `style-guide.md` alone, without cross-referencing `color-palettes.md`, would
ship a genuinely CVD-unsafe default believing it verified-safe.

**Proposed fix:** Replace `PALETTE_DEEP` with `OKABE_ITO`/Tol or seaborn's actual
`"colorblind"` palette, and correct the heading to not claim universal CVD safety for
a palette that was never designed for that. If the intent was "a distinctive
non-Okabe-Ito option for variety," retitle it "Aesthetic palette (verify with a
simulator before using for red/green-adjacent categories)" rather than asserting safety.

### T9 (new) — NYT `.mplstyle` color cycle is unverified for colorblind safety, unlike the other three `.mplstyle` files

**Verdict: Plausible gap, not confirmed unsafe — flagging for verification.**

**Evidence:** `assets/nature.mplstyle:30`, `assets/presentation.mplstyle:28`, and
`assets/publication.mplstyle:32` all bake in the Okabe-Ito hex cycle verbatim. By
contrast `assets/nyt.mplstyle:79` uses an entirely different, unrelated 6-color cycle:
```
axes.prop_cycle: cycler('color', ['326891', 'C9553E', '3A7D44', '7B5EA7', '2A8C8A', 'C4A35A'])
```
This is the palette `SKILL.md` designates **primary** for Goal 3 (Business
Presentation) — described as "the most SWD-demanding" goal (`SKILL.md:159`). Nowhere
in `SKILL.md`, `nyt.mplstyle`, or any reference file is this specific 6-color set
claimed or verified as colorblind-safe (contrast with the Okabe-Ito-based styles, which
are explicitly labeled as such throughout). The 2nd/3rd colors in the cycle,
`#C9553E` (a muted brick-red/orange) and `#3A7D44` (a mid-value green), sit in a
red-to-green relationship that warrants a simulator check before being trusted as safe
for a stacked bar chart or multi-line chart using colors #2 and #3 together — I could
not fully resolve this without running an actual CVD simulation, which I don't have
tool access to do here.

**Proposed fix:** Run `nyt.mplstyle`'s prop_cycle through Coblis/Color Oracle (or
`colorspacious`) before shipping; if any adjacent pair is high-risk, reorder the cycle
so the riskiest pair is never colors #1/#2 or #2/#3 (the pair most likely to appear
together in a 2-3 series chart), or swap one hue for a less saturated variant.

### T10 (new, minor) — Colorblind-simulation "how-to" code in `color-palettes.md` is a non-functional stub

**Verdict: Confirmed, minor.**

**Evidence:** `references/color-palettes.md:245-255`:
```python
# Using colorspacious to simulate colorblind vision
from colorspacious import cspace_convert

def simulate_deuteranopia(image_rgb):
    from colorspacious import cspace_convert
    # Convert to colorblind simulation
    # (Implementation would require colorspacious library)
    pass
```
This is the skill's only code-level answer to its own repeated instruction to "test
with a colorblind simulator." The function body is `pass` — it does nothing. An agent
that trusts this snippet (as it trusts the working grayscale-conversion snippet two
sections earlier at the same file, lines 302-307) would silently no-op instead of
actually verifying accessibility, which undermines every other "test with a simulator"
instruction across the skill (`design-principles.md:89`, `style-guide.md:298-303`, T9
above).

**Proposed fix:** Either implement it for real using `colorspacious`'s CVD space
(e.g. `cspace_convert(rgb, {"name": "sRGB1+CVD", "cvd_type": "deuteranomaly",
"severity": 100}, "sRGB1")`), or remove the stub and just point to the external tools
list (Coblis / Color Oracle) that's already given immediately above it, so nothing in
the file implies a working local simulation exists when it doesn't.

---

## Summary table

| Topic | Verdict | Severity |
|---|---|---|
| T1 | Not a color issue; helpers are color-safe as written | — |
| T2 | Confirmed (both sub-issues) | Medium |
| T3 | Confirmed, worse than stated (specific CVD failure identified) | High |
| T4 | Not a color issue | — |
| T5 | Not a color issue | — |
| T6 | DPI/color are orthogonal; adjacent CMYK gap noted | Low |
| T7 (new) | Confirmed — skill-wide red/green contradiction in core SWD rule | **Highest** |
| T8 (new) | Confirmed — false CVD-safety claim on seaborn's non-safe default palette | High |
| T9 (new) | Plausible, unverified — primary presentation palette never CVD-checked | Medium |
| T10 (new) | Confirmed, minor — non-functional simulation code stub | Low |
