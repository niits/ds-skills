# Round 1 — Independent Findings — member_code (Code & Technical Correctness lens)

Scope verified independently: `SKILL.md`, every file in `references/`, every file in `assets/`
(`nature.mplstyle`, `nyt.mplstyle`, `presentation.mplstyle`, `publication.mplstyle`,
`style_presets.py`, `color_palettes.py`, `swd_style.py`). I did not take the chairman's
framing on faith — verdicts below are my own, with disagreements called out explicitly.

---

## T1 — Dangling `banking-visualization` reference + orphaned domain helpers in `swd_style.py`

**Verdict: CONFIRMED (both halves).**

**Evidence:**
- `grep` for `banking-visualization` across the skill hits exactly one place:
  `SKILL.md:43` — `└─ Banking domain chart (KS, PSI, vintage, fraud monitoring) → see
  \`banking-visualization\` skill`.
- `ls skills/` confirms only `banking-hypothesis-generation`, `databricks`,
  `feature-onboarding`, `metrics-evaluation`, `visualization` exist. No
  `banking-visualization`, no `plotnine-visualization`. The decision tree routes readers
  to a skill that will 404 for any agent that tries to open it.
- `assets/swd_style.py` lines 250–324 (`risk_colormap`, `psi_status`, `fmt_bps`,
  `waterfall_colors`) are credit-risk-specific: `psi_status` hardcodes PSI industry
  thresholds (0.10 / 0.25 — this is a legitimate, correctly-implemented convention, not a
  bug in itself), `fmt_bps` formats basis points, `waterfall_colors` is written for SHAP
  waterfalls in credit contexts. None of this is wrong code — `psi_status` even validates
  input (`np.isfinite`, non-negative) and documents the thresholds as "configurable rules
  of thumb, not evidence of harmful drift," which is good practice. The problem is
  placement: this is domain logic living in a skill that markets itself as
  `domain: general` (see `SKILL.md` frontmatter) with its former domain-specific sibling
  skill deleted.

**Proposed fix:**
- `SKILL.md:43`: either remove the banking row from the decision tree, or repoint it at
  wherever KS/PSI/vintage functionality now lives (if `swd_style.py`'s domain helpers are
  being kept, the line should say "→ use `risk_colormap`/`psi_status`/`waterfall_colors`
  in `assets/swd_style.py`" instead of naming a skill that doesn't exist).
- Decide and document one of: (a) move `risk_colormap`, `psi_status`, `fmt_bps`,
  `waterfall_colors` out of `swd_style.py` into a domain-specific location, or (b) keep
  them here and update the module docstring / `SKILL.md` metadata to acknowledge the
  skill now carries a banking-domain helper set, so a reader doesn't go looking for a
  `banking-visualization` skill that no longer exists.

---

## T2 — Wong vs Okabe-Ito duplication; self-contradicting "safe (use with caution)" diverging maps

**Verdict: CONFIRMED (duplication) / CONFIRMED (self-contradiction), with one correction to
the chairman's framing.**

**Evidence — Wong vs Okabe-Ito:**
- `references/color-palettes.md` Okabe-Ito: `#E69F00, #56B4E9, #009E73, #F0E442, #0072B2,
  #D55E00, #CC79A7, #000000`.
- Same file's "Wong Palette (Alternative for Categories)": `black, orange, sky_blue, green,
  yellow, blue, vermillion, purple` = `#000000, #E69F00, #56B4E9, #009E73, #F0E442,
  #0072B2, #D55E00, #CC79A7` — identical 8-color set, reordered (black moved to front).
- `assets/style_presets.py` `WONG_COLORS` (line 35) is the same 8 hex values reordered
  relative to `OKABE_ITO_COLORS` (lines 18–27).
- WebSearch confirms: Okabe & Ito published the palette in 2008 ("Color Universal
  Design"); Bang Wong's 2011 *Nature Methods* "Points of View" column republished the same
  set, which is why it is sometimes called "the Wong palette" even though the design work
  is Okabe & Ito's. One nuance the debate topic doesn't mention: Wong's 2011 column is
  commonly cited as a **7-color subset that omits black**, not the full 8. This skill's
  "Wong" is presented as the full 8-color set (black included) in both
  `color-palettes.md` and `style_presets.py` — so it's not just reordered Okabe-Ito, it's
  arguably mislabeled as "Wong" when it's exactly Okabe-Ito's 8, under a different name.
  Either way, presenting it as a distinct "alternative" choice a user might pick instead of
  Okabe-Ito is misleading — picking "wong" in `set_color_palette('wong')` changes nothing
  perceptually vs `'okabe_ito'`.

**Evidence — PRGn/PiYG self-contradiction:**
- `assets/color_palettes.py` lines 62–69, `DIVERGING_COLORMAPS_SAFE` list includes `'PRGn'`
  and `'PiYG'` with inline comments `# (use with caution)` — inside a list whose own name
  asserts these are safe.
- WebSearch against ColorBrewer's colorblind-safe classification confirms PiYG and PRGn
  are in fact among ColorBrewer's colorblind-safe diverging schemes (6 of ColorBrewer's
  diverging palettes are marked colorblind-safe, including PRGn/PiYG/BrBG; RdGy, RdYlGn,
  and Spectral are the ones to avoid). So the "(use with caution)" hedge isn't just
  self-contradictory relative to the list name — per ColorBrewer's own classification the
  hedge is unwarranted; these two are genuinely fine, no more caution-worthy than PuOr or
  BrBG in the same list.
- RdYlBu (also flagged for "independent verification" in the debate topic): WebSearch
  confirms RdYlBu is listed among ColorBrewer's colorblind-safe diverging schemes too. The
  claim in `color-palettes.md` line 135 is correct as stated.

**Proposed fix:**
- `color-palettes.md`: either drop the "Wong Palette (Alternative for Categories)"
  subsection entirely and note in the Okabe-Ito section "also cited as the 'Wong palette'
  after Wong (2011), *Nature Methods*," or keep it but state explicitly it's the same
  color set, not a second option, so users don't imagine they're diversifying options for
  a multi-figure paper by alternating between the two.
- `assets/color_palettes.py` line 67–68: drop the `(use with caution)` inline comments on
  PRGn/PiYG, or if the authors intend a genuine caution (e.g. dimmer midpoint contrast at
  certain saturations), move PRGn/PiYG out of `DIVERGING_COLORMAPS_SAFE` into a separate
  "use with caution" list instead of contradicting the list name in-place.

---

## T3 — "Ocean Dusk" default palette not verified as colorblind-safe

**Verdict: CONFIRMED, from a code-correctness/data-accuracy angle rather than a "this is a
bug" angle — this is an unverified factual/design claim baked into example code.**

**Evidence:**
- `references/data-visualization.md` lines 49–68: `COLORS` / `COLOR_LIST` ("Ocean Dusk")
  is presented as the *default* palette for every chart-type example in the file
  (`plot_training_curves`, `plot_ablation`, `plot_leaderboard`, `plot_scatter`,
  `plot_scaling`, `plot_stacked_bar`, `plot_distributions` all default to `COLOR_LIST` or
  named `COLORS[...]` entries). `OKABE_ITO` only appears afterward, framed as "(maximum
  colorblind safety)" — implying by contrast that the default is not maximally safe, with
  no lesser tier of safety claimed or evidenced for "Ocean Dusk" either.
- Nothing in the file cites a CVD simulation, ColorBrewer/Tol/Okabe-Ito provenance, or any
  other verification for the 6 non-borrowed "Ocean Dusk" hues (`#264653` teal, `#2A9D8F`
  cyan, `#E9C46A` gold, `#F4A261` orange, `#E76F51` coral, `#8C8C8C` gray). Two colors
  (`#0072B2`, `#56B4E9`) are explicitly commented as "Okabe-Ito accessible," which is
  correct but only covers 2 of 8 entries.
- Looking at the hue relationships specifically: gold (`#E9C46A`), orange (`#F4A261`), and
  coral (`#E76F51`) are three adjacent warm hues in roughly the same yellow-orange-red
  band. That's exactly the kind of clustering that collapses under protanopia/deuteranopia
  simulation (reds/oranges/yellows desaturate toward each other), yet all three are used
  as if visually distinct in the same `COLOR_LIST` (e.g. `plot_ablation`,
  `plot_scaling` assign them to adjacent series by index).
- This directly conflicts with `SKILL.md`'s own blanket rule (line 112: "colorblind-safe
  categorical colors" required even in lightweight EDA) and with
  `publication-guidelines.md`'s Figure Checklist item "Colors are colorblind-friendly" —
  `data-visualization.md` is one of the five files `SKILL.md` points readers to for Goal 2
  (Publication), so an agent following the skill's own routing could pick up an unverified
  palette believing it inherits the skill's blanket colorblind-safety guarantee.

**Proposed fix:**
- Either (a) run "Ocean Dusk" through a CVD simulator (e.g. Coblis/Color Oracle, both
  already cited elsewhere in this skill) and document the result, replacing any hue that
  fails, particularly the gold/orange/coral cluster; or (b) relabel the section so it no
  longer reads as an unqualified default — e.g. "Ocean Dusk (aesthetic default — not
  verified colorblind-safe; use `OKABE_ITO` below when colorblind accessibility is
  required)" — and swap `OKABE_ITO` in as the default in the chart-type function
  signatures, consistent with every other reference file's stance.

---

## T4 — Dead/unreachable code in `apply_publication_style()`

**Verdict: CONFIRMED — this is a genuine bug, not a stylistic nit.**

**Evidence:** `assets/style_presets.py`:
- Lines 151–156:
  ```python
  if style_name in ('nature', 'presentation'):
      style_path = Path(__file__).with_name(f'{style_name}.mplstyle')
      if not style_path.is_file():
          raise FileNotFoundError(f"Style asset not found: {style_path}")
      plt.style.use(style_path)
      return
  ```
  This unconditionally returns for `style_name == 'nature'` or `'presentation'`.
- Lines 158–219 define `base_style = get_base_style()` then contain:
  ```python
  if style_name == 'nature':
      base_style.update({'font.size': 7, ..., 'savefig.dpi': 600})
  ...
  elif style_name == 'presentation':
      base_style.update({'figure.figsize': (13.333, 7.5), 'font.size': 18, ...})
  ```
  Both branches are unreachable — control flow can never reach line 161 or line 200 with
  `style_name` equal to `'nature'` or `'presentation'`, because the earlier `return` at
  line 156 already exited the function for those exact two values.
- Confirmed this is a *silent divergence*, not just redundancy: `nature.mplstyle` (the
  branch that actually executes) sets `savefig.dpi: 600` and `font.size: 7` — which
  happens to match the dead branch's `'savefig.dpi': 600, 'font.size': 7` numerically in
  this case, but `presentation.mplstyle` (`font.size: 18`, `axes.labelsize: 20`,
  `axes.titlesize: 24`, `figure.figsize: 13.333, 7.5`) also numerically matches its dead
  `elif` branch right now — so today the two definitions agree by coincidence. That's
  precisely the maintenance trap the debate topic describes: the two implementations can
  drift apart the next time someone edits one of the four (`.mplstyle` files vs. dict
  literals) without noticing the other exists, since the dict-literal one is unreachable
  and untested by any code path.
- Also relevant: `'science'`, `'cell'`, `'minimal'` styles have **no** corresponding
  `.mplstyle` asset file on disk (only `nature`, `nyt`, `presentation`, `publication`
  exist in `assets/`), so their `base_style.update(...)` branches (lines 172–198) are
  correctly reachable and are the only implementation — not dead code. The dead-code bug
  is specific to the `nature`/`presentation` names.

**Proposed fix:**
- Delete the unreachable `if style_name == 'nature': ...` and
  `elif style_name == 'presentation': ...` blocks (lines ~161–171 and ~200–212) from
  `apply_publication_style()` entirely, since `.mplstyle` files are the actual source of
  truth for those two names. This also shrinks the function and removes the drift risk.
  Alternatively, if the dict-literal path is meant to be a fallback when the `.mplstyle`
  file is missing, restructure as try/except around `plt.style.use` rather than an
  unconditional `return`.

---

## T5 — Serif "Times New Roman" vs. sans-serif default

**Verdict: PARTIALLY VALID — real inconsistency, but I disagree with treating it purely as
a defect; it reflects a genuine, defensible split in venue convention that the skill fails
to surface at the routing layer.**

**Evidence:**
- `references/data-visualization.md` lines 15–17: `"font.family": "serif", "font.serif":
  ["Times New Roman", "DejaVu Serif"]` under a comment literally reading "Publication
  defaults."
- `references/style-guide.md` lines 112–120 (Typography table) independently corroborates
  this is intentional for ML venues: NeurIPS/ICML/ICLR/ACL/AAAI all list "Document Font:
  Times" and "Figure Font Setting: `font.family: serif`, `font.serif: Times New Roman`" —
  this is a real, correct convention (ML conference LaTeX templates typically use Times or
  a Times-like Type 1 font, and mismatched figure fonts are a common desk-reject-adjacent
  nitpick in reviews).
- Meanwhile `references/publication-guidelines.md` line 40 ("Font family: Sans-serif fonts
  (Arial, Helvetica, Calibri) for most journals"), `references/matplotlib-examples.md`
  lines 20–21, `assets/style_presets.py` `get_base_style()` line 56-57, and all four
  `.mplstyle` files use sans-serif — correct for life-science/general journals (Nature,
  Cell, PLOS, etc., per `journal-requirements.md`'s "Fonts: Arial or Helvetica" entries
  across every publisher listed there).
- Both conventions are independently correct for their venue family. The technical gap is
  that `SKILL.md`'s "Goal 2: Publication / ML Papers" section (lines 116–137) points to
  `publication-guidelines.md`, `journal-requirements.md`, `matplotlib-examples.md` — all
  sans-serif — without ever mentioning `data-visualization.md` or `style-guide.md` by name
  in that section (they're only listed later under "Resources", line 222, undifferentiated
  from the sans-serif files). An agent following Goal 2's explicit reading list would never
  even encounter the serif convention, so in practice this isn't "an agent could apply the
  wrong font" so much as "an agent using `data-visualization.md` on its own (e.g. arriving
  there via the Resources index rather than the Goal-2 walkthrough) has no signal that its
  serif default is ML-conference-specific, not general-purpose."

**Proposed fix:**
- Add one sentence to `data-visualization.md`'s rcParams block comment: change
  `"# --- Publication defaults (polished, not generic) ---"` to something like
  `"# --- ML-conference defaults (NeurIPS/ICML/ICLR/ACL — Times-based LaTeX templates).
  For life-science/general journals use references/publication-guidelines.md's sans-serif
  defaults instead. ---"`.
- In `SKILL.md`'s "Goal 2" section (~line 136-137), add `data-visualization.md` and
  `style-guide.md` to the explicit reading list with a one-line disambiguator, e.g. "ML
  conference paper (NeurIPS/ICML/...) → `references/style-guide.md`,
  `references/data-visualization.md` (Times-based fonts); life-science/general journal →
  `references/publication-guidelines.md`, `references/journal-requirements.md`
  (sans-serif fonts)."

---

## T6 — DPI on vector PDF output; inconsistent Nature line-art DPI figures

**Verdict: CONFIRMED on both counts — this is the clearest hard technical error in the
skill.**

**Evidence — DPI on vector formats is a real conceptual error:**
- WebSearch against Matplotlib's own documentation/community consensus confirms: for
  vector output formats (PDF, SVG, EPS), `dpi` has no effect on path/text sharpness since
  vector formats are resolution-independent — `dpi` only matters for any *rasterized
  sub-elements* embedded in the vector file (e.g. `imshow`/rasterized scatter with huge
  point counts, or if `rasterized=True` is set on an artist). This matches
  general matplotlib knowledge and is not disputed by any source found.
- `references/matplotlib-examples.md` line 564: `fig.savefig('nature_figure.pdf',
  dpi=1000, bbox_inches='tight', facecolor='white', edgecolor='none')` — this is
  presented in "Example 10: Publication-Ready Figure for Nature" as satisfying Nature's
  line-art DPI requirement. Since Panel c in that same example is a rasterized
  `imshow(cmap='viridis')` heatmap embedded in the PDF, `dpi=1000` *does* affect that one
  panel's raster resolution — but the code comments/framing present `dpi=1000` as a
  general "Nature requirements" setting for the whole vector figure, which teaches the
  wrong mental model: a reader would reasonably believe raising `dpi` improves the line
  art (axes, text, vector paths) too, and it does not.
- Immediately below in the same example, `fig.savefig('nature_figure.png', dpi=300, ...)`
  correctly uses dpi on a raster PNG — so the file **does** get the PNG case right, which
  makes the PDF case's implicit "dpi=1000 satisfies Nature line-art dpi" framing more
  likely to mislead (a reader sees `dpi=` used correctly right next to it and reasonably
  assumes the same logic applies).

**Evidence — inconsistent numeric guidance across 3 files:**
- `references/journal-requirements.md` line 17: "Line art: 1000-1200 DPI" for Nature.
- `references/publication-guidelines.md` line 16: "Line art and graphs: 600-1200 DPI (or
  vector format)" — a wider, unattributed-to-any-journal range.
- `assets/nature.mplstyle` line 56: `savefig.dpi: 600  # 1000 for line art, 600 for
  combination` — the comment describes a conditional rule the file's single scalar value
  can't implement; whatever figure type the user is making, they get 600, with a comment
  that only makes sense if they manually override it for line art.
- I went further than the debate topic and checked what Nature's *own* current author
  guidance actually says (WebSearch against Nature's for-authors pages and third-party
  aggregators of that guidance): Nature's modern stance is **"do not rasterize line art or
  text — submit vector formats,"** with a flat **300 dpi minimum** commonly cited for
  raster content and 600 dpi as a safe default for combination (mixed raster+vector)
  figures. The "1000-1200 DPI for line art" figure that both `journal-requirements.md` and
  the `nature.mplstyle` comment cite appears to be older/secondary guidance (commonly
  repeated across third-party "how to prepare a Nature figure" blog posts) rather than
  Nature's current primary instruction, which is closer to "don't rasterize it at all."
  This doesn't make the skill's number fabricated, but it means none of the three files'
  numbers can be cited as *the* authoritative current Nature figure without a citation,
  and the skill should say "vector preferred; do not rasterize line art" as the primary
  rule with DPI numbers as a fallback for when rasterization is unavoidable, rather than
  presenting DPI as the primary lever the way `matplotlib-examples.md` Example 10 does.

**Proposed fix:**
- `matplotlib-examples.md` Example 10: change the PDF save line's comment to make clear
  `dpi` only affects rasterized sub-elements of the PDF (the `imshow` heatmap panel), not
  the vector line art/text, e.g.:
  ```python
  # dpi only affects rasterized sub-elements embedded in the PDF (e.g. the imshow panel
  # below) — it does not increase the resolution of vector paths/text. Nature's primary
  # rule is "do not rasterize line art"; keep axes/lines/text as vector paths.
  fig.savefig('nature_figure.pdf', dpi=1000, bbox_inches='tight',
              facecolor='white', edgecolor='none')
  ```
- Reconcile the three numeric claims: pick one figure (or a cited range with source) and
  use it consistently in `journal-requirements.md`, `publication-guidelines.md`, and the
  `nature.mplstyle` comment. Given the uncertainty found above, I'd suggest leading with
  "vector format preferred; do not rasterize line art" and demoting the DPI number to
  "if rasterization is unavoidable, use ≥600 DPI" rather than asserting a precise
  1000-1200 figure as settled fact.
- `assets/nature.mplstyle` line 56: either implement the split (not possible with a single
  scalar rcParam — `savefig.dpi` applies file-wide) or drop the misleading inline comment
  since the file cannot act on it; state plainly that `savefig.dpi: 600` is a
  combination-figure default and pure line-art figures should be saved as vector with no
  DPI dependency.

---

## T7 (NEW) — `style-guide.md` claims a non-CVD-optimized seaborn "deep"-style palette is safe "under all forms of color vision deficiency," and pairs red+green in it

**Verdict: CONFIRMED — this is a materially incorrect accessibility claim, arguably worse
than T2/T3 because it's an unambiguous false statement rather than an unverified/ambiguous
one.**

**Evidence:**
- `references/style-guide.md` lines 63–79:
  ```
  ### Recommended Colorblind-Safe Palette
  This palette is distinguishable under all forms of color vision deficiency:
  PALETTE_DEEP = [
      "#4C72B0",  # blue
      "#DD8452",  # orange
      "#55A868",  # green
      "#C44E52",  # red
      "#8172B3",  # purple
      "#937860",  # brown
      "#DA8BC3",  # pink
      "#8C8C8C",  # gray
  ]
  ```
- These 8 hex values are matplotlib/seaborn's **"deep"** categorical palette (seaborn's
  *default* qualitative palette), confirmed via WebSearch against seaborn's palette
  reference and third-party palette catalogs matching all 8 hex codes exactly.
- Seaborn explicitly ships a *different*, separately-named **"colorblind"** palette for
  CVD accessibility (`sns.color_palette("colorblind")`), distinct from `"deep"`. Search
  results explicitly describe `"deep"` as aesthetically pleasing default hues that "may be
  more difficult to discriminate" and recommend `"colorblind"` when accessibility is the
  priority — i.e., seaborn's own documentation contradicts this file's claim that `"deep"`
  is the accessible one.
- Concretely: `PALETTE_DEEP` places green (`#55A868`) and red (`#C44E52`) in the same
  8-color set, at positions 3 and 4. Red/green in the same categorical set is exactly the
  combination `style-guide.md` itself tells readers to avoid one section later ("Colors to
  Avoid" → "Pure red + pure green — indistinguishable for ~8% of males", line 105) and
  that every other reference file in this skill (`color-palettes.md`,
  `publication-guidelines.md`, `data-visualization.md`) also warns against. The file
  contradicts itself within ~40 lines: labels a red+green-containing palette "Recommended
  Colorblind-Safe" at line 63-65, then warns against red+green at line 105.
- This is the most concrete, unambiguous defect I found across the whole skill: it's not
  "unverified" (T3) or "self-contradictory hedge" (T2) — it's a false accessibility claim
  attached to a palette that visibly violates the skill's own stated rule two sections
  later, likely to be trusted and used verbatim by an agent following `style-guide.md` for
  an ML-conference paper (which is exactly the file `SKILL.md` points to for that use
  case).

**Proposed fix:**
- Replace `PALETTE_DEEP`'s values with an actually colorblind-verified palette (e.g.
  Okabe-Ito subset, or seaborn's own `"colorblind"` palette, or Tol) OR relabel the
  section honestly: drop "Colorblind-Safe" from the heading and the "distinguishable under
  all forms of color vision deficiency" claim, since this is seaborn's `"deep"` default,
  not its `"colorblind"` palette. Cross-reference `color-palettes.md`'s Okabe-Ito section
  instead of introducing a fourth, unverified palette into the skill.

---

## Summary Table

| Topic | Verdict |
|---|---|
| T1 | Confirmed |
| T2 | Confirmed (with correction: Wong 2011 is usually a 7-color subset omitting black; this skill's "Wong" is the full 8 incl. black, i.e. literally Okabe-Ito under another name) |
| T3 | Confirmed (framed as unverified-claim issue, not a "bug") |
| T4 | Confirmed — genuine unreachable-code bug |
| T5 | Partially valid — both conventions are independently correct for their venue; the defect is in `SKILL.md`'s routing/disambiguation, not in either file's content |
| T6 | Confirmed — both the DPI/vector conceptual error and the 3-way numeric inconsistency |
| T7 (new) | Confirmed — false "colorblind-safe" claim on seaborn's non-accessible "deep" palette, self-contradicts the same file's own red/green warning |
