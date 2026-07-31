# Round 2 — member_color (Color Science & Accessibility lens)

Scope: respond to the chairman's Scope Redirect (message-delivery focus) per
`agent_council/debate_log.md`'s "## Scope Redirect" section, using my own Round-1
findings (T2, T3, T7, T8, T9, T10) as the color-science baseline. No files edited.

---

## 1. RdYlBu colorblind-safety — DEFINITIVE RULING

**RdYlBu IS colorblind-safe. This is now settled, not disputed.**

Verified directly against `RColorBrewer::brewer.pal.info`, which is generated
programmatically from Cynthia Brewer's own ColorBrewer classification (the same
"colorblind safe" flag exposed by the colorbrewer2.org UI checkbox) — fetched the
package source (`R/ColorBrewer.R`) and confirmed the literal `colorblindlist` vector:

```r
colorblindlist <- c("BrBG","PiYG","PRGn","PuOr","RdBu","RdYlBu",
                     "Dark2","Paired","Set2", seqlist)
```

For the 9 diverging (`div`) palettes ColorBrewer ships, the safe/unsafe split is:

| Diverging palette | ColorBrewer colorblind-safe? |
|---|---|
| BrBG | TRUE |
| PiYG | TRUE |
| PRGn | TRUE |
| PuOr | TRUE |
| RdBu | TRUE |
| **RdYlBu** | **TRUE** |
| RdGy | FALSE |
| RdYlGn | FALSE |
| Spectral | FALSE |

This matches my Round-1 T2 finding exactly (RdYlBu grouped with BrBG/PuOr/RdBu as
safe; RdGy/RdYlGn/Spectral unsafe) and now has a hard, checkable citation instead of
"web search returned inconsistent secondary sources." **`references/color-palettes.md`'s
RdYlBu claim (lines 135-138) is correct as written — no fix needed.**

**Bonus resolution — this same table also resolves the PRGn/PiYG half of T2 that
Round 1 left unverified.** Both PRGn and PiYG are colorblind-safe TRUE per ColorBrewer
— my Round-1 guess ("PRGn safe, PiYG probably not") was wrong; they're both fine. This
changes the recommended fix for `assets/color_palettes.py:62-69`
(`DIVERGING_COLORMAPS_SAFE`): Round 1 proposed either removing the caution comment on
both, or splitting PiYG out to the `_AVOID` list. **The correct fix is now
unambiguous: remove the "(use with caution)" comment from both `PRGn` and `PiYG` —
they are both genuinely safe, don't move PiYG to `_AVOID`.**

Citations:
- `RColorBrewer::brewer.pal.info` / `R/ColorBrewer.R` source (`colorblindlist`
  definition, https://github.com/cran/RColorBrewer/blob/master/R/ColorBrewer.R),
  which mirrors colorbrewer2.org's own "colorblind safe" filter.
- Cross-checked via secondary web search (independent query) returning the same
  membership list.

---

## 2. `references/color-palettes.md` — PRUNE boundary review

**Chairman's boundary is correct; one item should move from "defer" to a firm cut, one
piece of the keep-zone needs an accuracy fix while it's being touched anyway.**

- **CMYK section (lines 315-334, "Color Spaces / RGB vs CMYK")**: confirmed pure
  print-production content, zero message-delivery logic. Cut is correct.
- **Genomics/Microscopy "Special Purpose Palettes" (lines 162-201)**: I checked the
  actual content — `nucleotide_colors`, `fluorophore_colors` /
  `fluorophore_alt`. The "accessible alternative" dicts do embody the general
  red/green-avoidance substitution pattern (swap green→orange, red→vermillion), but
  that pattern is already stated as a generic rule elsewhere in this same file ("Don't:
  Use red/green combinations," line 216) and in `design-principles.md`. Nothing
  domain-specific here teaches a message-delivery technique not already covered
  generically. **Agree with cutting it** — not decoration, but genuinely out of scope
  for a general DS skill, and redundant with what's kept.
- **T10 stub (`simulate_deuteranopia`, lines 245-255)**: confirmed still a no-op
  (`pass` body) sitting in the "Testing for Colorblind Accessibility" section, which is
  otherwise being kept (online simulators list, CVD-type definitions — functional,
  in-scope). Must be fixed in place per chairman's directive: either implement via
  `colorspacious.cspace_convert(rgb, {"name": "sRGB1+CVD", "cvd_type":
  "deuteranomaly", "severity": 100}, "sRGB1")` or delete the function body and keep
  only the simulator links above it. Confirmed this survives the prune and is not
  moot.
- **T2 Wong-as-alternative fix**: confirmed still needed at lines 55-70. The prune
  doesn't touch this section, so the misleading "Alternative for Categories" framing
  ships unchanged unless explicitly rewritten per the Round-1 fix (Wong = historical
  citation synonym for Okabe-Ito, not a second palette).
- **Minor accuracy catch while this file is open anyway**: line 153 lists `RdGn
  (Red-Green)` under "Avoid These Diverging Maps." `RdGn` is not a real
  matplotlib/ColorBrewer colormap name (no such registered cmap) — likely a typo/stand-in
  the author meant as a generic label. Since `RdYlGn` is already listed separately
  right below it, recommend either removing the `RdGn` line or correcting it to a real
  name (e.g. clarify it's shorthand, not an importable cmap string) so a reader doesn't
  try `cmap='RdGn'` and get a matplotlib `ValueError`. Not one of the original
  T1-T10 items but directly in my lens and touches the file being pruned regardless.

**Nothing being cut is actually functional message-delivery content; nothing being
kept is pure decoration.** Boundary confirmed sound.

---

## 3. `references/style-guide.md` — PRUNE (heavy) boundary review

**Boundary is correct, with one explicit gap to flag: "Colors to Avoid" (lines
103-108) isn't named in the chairman's keep list and should be.**

- **Gradient-choice table (lines 93-101)**: this is exactly the "which use case → which
  map family" choice logic the redirect wants kept (Blues for single-variable,
  RdBu_r for diverging, viridis for perceptually-uniform, coolwarm for correlation,
  YlOrRd for attention weights). Confirmed functional, confirmed kept correctly.
- **Caption Best Practices (lines 286-294) and Accessibility Checklist (296-304)**:
  message-delivery / accessibility, correctly kept (checklist should be deduped
  against `design-principles.md`'s equivalent per the chairman's note — I see no
  material content unique to this file's checklist that `design-principles.md` lacks,
  so a straight dedupe/pointer is fine).
- **T8 fix (`PALETTE_DEEP`, lines 63-79)**: confirmed the false claim is exactly as
  Round 1 described — these are seaborn's `"deep"` default (not `"colorblind"`), and
  the 3rd/4th entries (`#55A868` green, `#C44E52` red) are a red/green pair sitting
  inside a palette labeled "distinguishable under all forms of color vision
  deficiency." This is a hard factual error and must be fixed in the same pass, not
  left as a trimmed-but-still-false claim — agree fully with the chairman's framing.
  Replace with `OKABE_ITO` (already the skill's canonical set) rather than inventing a
  third named palette.
- **Gap I'm flagging**: "Colors to Avoid" (lines 103-108: "Pure red + pure green,"
  "Rainbow/jet," "Light yellow on white," "Neon/saturated") is short, purely
  functional, and — per my own Round-1 T7 finding — is one of the four places in this
  skill that correctly states the red/green-avoidance rule, the same rule that
  `pre-attentive-attributes.md`'s "Gray Palette Strategy" currently violates. The
  chairman's explicit keep list for this file doesn't name this section, and if it
  falls into the "Layout Conventions"/"Typography" cut zone by omission, the skill
  loses one of its four independent statements of the rule right as we're fixing a
  place that contradicts it. **Recommend explicitly adding "Colors to Avoid" to the
  keep list** — 6 lines, zero decoration, directly reinforces the T7 fix.
- **Everything else in the chairman's cut list** (venue dimensions, LaTeX font
  matching, font-size pt tables, legend bbox/grid-alpha/spine snippets, Diagram Style
  Standards, LaTeX Integration): confirmed pure submission/aesthetic polish, no
  color-science or message-delivery content in any of it. Cut is correct.

**T7 confirmed to survive in `pre-attentive-attributes.md` and needs fixing there.**
Re-read the kept file directly: lines 101-102 still read
```
Negative:       red — financial loss, error states only
Positive:       green — goal achieved, up vs target only
```
inside the "Gray Palette Strategy" block that's explicitly the canonical reference
this file exists to provide (per its role in the KEEP list). This is the exact
contradiction flagged in Round 1: line 22 of the *same file* ("Colorblind-safe: avoid
red + green as the only differentiator") directly contradicts lines 101-102 fifteen
lines later. This is not a cross-file inconsistency anymore once style-guide.md's
similar line is pruned/rewritten — it's an **internal, single-file self-contradiction**
in the one document the redirect designates as the canonical emphasis-technique
reference. Highest-priority fix in this whole pass; proposed rewrite unchanged from
Round 1 (coral/vermillion for negative, blue or bluish-green for positive, explicit
"never pair as sole differentiator on one chart" note).

---

## 4. Is `assets/color_palettes.py` the right home for palette logic? What needs rescuing from `style_presets.py`?

**Yes, `color_palettes.py` is the right home. Nothing of unique color-science value in
`style_presets.py` needs rescuing before it's deleted.**

Checked every palette-adjacent piece of `style_presets.py` against `color_palettes.py`:

- `OKABE_ITO_COLORS`, `TOL_BRIGHT`, `TOL_MUTED`, `TOL_HIGH_CONTRAST`, `WONG_COLORS` in
  `style_presets.py` (lines 18-35) are **byte-identical values** to
  `OKABE_ITO_LIST`/`TOL_*`/`WONG` already in `color_palettes.py`. No unique data.
- `set_color_palette()` (lines 222-257) is a thin wrapper around the same dicts,
  functionally identical to `color_palettes.py`'s `apply_palette()`. Fully redundant,
  confirmed by Round 1's own note — nothing lost deleting it.
- `get_base_style()`, `apply_publication_style()`, `configure_for_journal()`,
  `create_style_template()`: pure rcParams/DPI/venue-sizing plumbing, zero color
  logic beyond re-applying the same prop_cycle. Correctly slated for deletion.
- **One function has genuinely unique logic not present anywhere else in the kept
  files**: `show_color_palettes()` (lines 363-395) renders palette swatches and picks
  black-vs-white label text via a relative-luminance formula
  (`0.2126*r + 0.7152*g + 0.0722*b`, threshold 0.45) so hex labels stay readable
  against each swatch. This is a legitimate small accessibility technique (contrast-
  aware text color) that doesn't exist in `color_palettes.py` today. That said: it's a
  documentation/preview convenience, not something that changes how an agent colors
  an actual chart for a message — I'd call this **optional, not mandatory** to port.
  If the chairman wants a "preview your palette" utility to remain available,
  fold this one function (with its luminance formula) into `color_palettes.py`;
  otherwise it's fine to let it go with the rest of the file, since the palette data
  it displays already lives on in `color_palettes.py`.
- **Consistency note, not a rescue**: `color_palettes.py` still carries
  `FLUOROPHORES_TRADITIONAL/ACCESSIBLE` and `DNA_BASES/DNA_BASES_ACCESSIBLE` (lines
  77-108), the code-level twin of the genomics/microscopy prose section I'm agreeing
  to cut from `color-palettes.md` in item 2 above. For prose/code consistency, these
  four dicts should be removed from `color_palettes.py` in the same pass — otherwise
  the reference doc no longer mentions genomics use cases but the asset file still
  ships genomics-only color dicts with no doc pointing to them.

---

## Summary for chairman

| Item | Verdict |
|---|---|
| RdYlBu colorblind-safe? | **Yes — definitively confirmed via `RColorBrewer::brewer.pal.info` (mirrors colorbrewer2.org). No fix needed to that claim.** |
| PRGn/PiYG in `color_palettes.py` | Both safe — remove "(use with caution)" from both, don't split PiYG to AVOID (corrects my own Round-1 uncertainty) |
| `color-palettes.md` PRUNE boundary | Correct. Add: fix stray `RdGn` typo (not a real cmap name) while in there |
| `style-guide.md` PRUNE boundary | Correct, but add "Colors to Avoid" (103-108) to the explicit keep list — it's functional and reinforces the T7 fix |
| T7 (`pre-attentive-attributes.md` red/green) | Confirmed still present at lines 101-102, now an internal self-contradiction (line 22 vs. 101-102) in the file the redirect names canonical — highest priority fix |
| `assets/color_palettes.py` as palette home | Correct home. Nothing mandatory to rescue from `style_presets.py`; `show_color_palettes()`'s luminance-based label-contrast logic is the only unique piece, optional port. Also drop the genomics dicts from `color_palettes.py` to match the pruned reference doc |
