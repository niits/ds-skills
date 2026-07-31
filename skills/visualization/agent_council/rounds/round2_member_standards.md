# Round 2 — member_standards (post-Scope-Redirect audit)

Scope: verify the chairman's KEEP/PRUNE/DELETE plan (see "## Scope Redirect —
Message-Delivery Focus" in `debate_log.md`) leaves no dangling references, and give a
recommendation on the T7 content-gap fix and the T5/T6 moot-status question. No files
edited — findings only, mapped precisely to file/line so the fix pass can act on them.

---

## 1. SKILL.md — dangling references after the planned PRUNE

Read the current `SKILL.md` end-to-end against the chairman's cut list. The routing/
philosophy/SWD/audit content the plan wants kept is *not* self-contained once the listed
cuts are made — several surviving lines still point at material scheduled for DELETE.
Confirmed dangling references, in file order:

1. **Line 41** (Library Decision Tree): `Slide / presentation for stakeholders →
   matplotlib + NYT theme`. The chairman's plan only calls out cutting Goal 3's
   *code sample* (`plt.style.use(".../nyt.mplstyle")`); it never revisits this
   decision-tree leaf, which still names "NYT theme" — and `nyt.mplstyle` is DELETE.
   Left as-is, the routing tree itself (explicitly a KEEP item) sends the reader to a
   file that no longer exists.

2. **Line 43** (Library Decision Tree): `Banking domain chart (KS, PSI, vintage, fraud
   monitoring) → see \`banking-visualization\` skill`. This is T1's original dangling
   reference, carried over unresolved — the chairman's SKILL.md ruling acknowledges it
   ("the domain routing concept itself... is in-scope even though the old pointer is
   dead") but defers the actual fix to the T7 content-gap work in
   `model-evaluation-viz.md`. Still broken today; must be repointed (or removed) in the
   same pass, not left dangling pending a separate file's edit.

3. **Line 143 + 146-152** (Goal 3 intro + code block): `**Primary: matplotlib + bundled
   NYT style.**` followed by the `plt.style.use("skills/visualization/assets/nyt.mplstyle")`
   block. The plan explicitly cuts the code block, but the prose sentence introducing it
   ("bundled NYT style") is not mentioned and would survive as a claim about a deleted
   asset if only the fenced code is removed. Needs rewording, not just a code deletion.

4. **Lines 171-179** ("Publication Styling Reference (matplotlib)" section) — entirely
   cut per plan. Confirmed this fully removes its embedded references to
   `journal-requirements.md`, `assets/style_presets.py`, and all four `.mplstyle` files
   (lines 173-179) — no partial-cut risk here, the whole block goes. Listed for
   completeness, not as an open issue.

5. **Line 188** (Databricks Rendering section — **this section is explicitly KEEP**):
   `Upload \`assets/\` helpers to DBFS ... before importing \`style_presets\` /
   \`swd_style\`.` This is the most important find: it's a dangling reference to a
   DELETE-marked file (`style_presets.py`) sitting *inside* content the chairman
   ruled KEEP outright, not inside anything on the cut list. Must strip `style_presets`
   from this sentence (leave `swd_style` only) or the kept section ships broken on day one.

6. **Resources section, lines 212-231**:
   - Line 221: `` `publication-guidelines.md`, `journal-requirements.md`, `style-guide.md` ``
     — `journal-requirements.md` is DELETE; must be removed from this line.
   - Line 230: `` `style_presets.py`, `color_palettes.py` — publication rcParams &
     colorblind palettes`` — `style_presets.py` is DELETE, `color_palettes.py` is KEEP;
     line must drop the first name (and probably its half of the description clause,
     since "publication rcParams" was `style_presets.py`'s job, not `color_palettes.py`'s).
   - Line 231: `` `nature.mplstyle`, `publication.mplstyle`, `presentation.mplstyle`,
     `nyt.mplstyle` `` — all four are DELETE. Entire line must be removed, not edited.

7. **Structural/numbering orphan**: the plan cuts "Goal 2: Publication / ML Papers" as a
   whole heading (not just its code/pointers — re-read the instruction: "cut Goal
   2/publication-styling sections"). If Goal 2's heading disappears, the document jumps
   from "Goal 1: EDA & Exploration" straight to "Goal 3: Business Presentation," leaving
   an orphaned "3" with no "2" — a reader has no way to know a goal was removed on
   purpose vs. a numbering bug. Needs renumbering (Goal 1→Goal 2) or a switch to
   unnumbered headings.

8. **Soft/conceptual dangling reference** — Overview & Philosophy, lines 29-31: "This
   skill merges three concerns that used to be separate skills — the SWD framework,
   publication/scientific styling (matplotlib/seaborn), and the grammar of graphics
   (plotnine) — into one goal-based reference." This sentence still advertises
   "publication/scientific styling" as one of the skill's three founding pillars and
   calls the document "goal-based," but the goal that pillar mapped to (Goal 2) is being
   deleted. Not a broken link, but a stale self-description that will confuse a reader
   trying to understand why there are only two Goals left. Flag for rewrite alongside
   the renumbering in (7).

**Count: 6 hard dangling references (1, 2, 3, 5, and the two sub-bullets of 6) + 1
structural numbering orphan + 1 conceptual staleness note.** None of these are
hypothetical — every one is a line that exists in `SKILL.md` today and would still exist,
unfixed, if the editor executes only the cuts explicitly spelled out in the chairman's
per-file bullets without independently re-reading the surviving prose for cross-references.

---

## 2. T7 recommendation — write the KS/PSI content, don't just delete the pointer

Checked the dependency chain, not just `model-evaluation-viz.md` in isolation.
`references/audience-adaptation.md` — a file with **zero previously-flagged bugs, ruled
KEEP outright** — uses "KS curve" and "PSI bar" repeatedly as named, presumed-defined
chart types in its own worked examples:

- Line 22: `Diagnostic charts (KS curve, calibration, SHAP, PSI)`
- Line 27: `Keep: discrimination chart (KS or ROC), stability chart (PSI), headline metrics`
- Line 30: title example `"Model discrimination adequate; PSI stable at 0.08"`
- Line 50: `| Practitioner | KS curve + score distribution overlay | "KS = 0.42 — acceptable discrimination..." |`
- Line 51: `| Risk Committee | KS summary + PSI bar | "Model meets validation threshold (KS > 0.35)..." |`

This means the "just delete the table row" fix in `model-evaluation-viz.md` does **not**
close the gap — it only relocates it. `audience-adaptation.md` would still promise, by
name, audience-tailored KS/PSI charts that no file in the kept skill shows how to build.
Removing the pointer trades one small dangling table row for a larger, less obvious
dangling dependency spread across five lines of a different KEEP file that nobody has
flagged for editing yet.

**Recommendation: write the content**, not remove the pointer. This is also the more
scope-consistent choice under the message-delivery redirect, not just the safer one:
- A KS curve (cumulative distribution separation between goods/bads, threshold-marked)
  and a PSI stability chart/trend are chart-*selection*-and-*audience*-tailoring
  decisions — exactly the genre of content the redirect keeps for ROC/PR/Calibration in
  the same file. It is not decoration; it's "which chart answers this credit-risk
  question, and how do you title/annotate it for a practitioner vs. a risk committee,"
  the same treatment already given to Sections 1-7.
- The lift is bounded and matches an existing template: two new sections
  (`## KS Curve`, `## PSI Stability Chart`) following the same structure already used by
  the file's other seven sections (description, required inputs, key design decision,
  audience note) — this is not open-ended scope creep, it's filling two gaps in an
  otherwise-complete pattern.
- It also finally gives decision-tree line 43 (finding 2 above) a real, live target to
  repoint to instead of the dead `banking-visualization` link — one content addition
  closes T1, T7, and dangling-reference finding #2 together, which is the efficient
  order of operations (write the content, then repoint the two pointers to it).

Effort-vs-scope-creep counterpoint, for the chairman's weighing: this is the one piece of
genuinely *new* writing in an otherwise subtractive pass, and it requires domain
knowledge (KS statistic construction, PSI banding/thresholds) not otherwise exercised
elsewhere in this skill. If the chairman prefers to cap new-content risk in this pass,
the fallback is to remove the table row *and* strip "KS curve"/"PSI bar" as named
artifacts from `audience-adaptation.md`'s five lines above (generalizing to "discrimination
chart" / "stability chart" without a specific named chart type) — but that is a larger,
uglier edit to a currently-clean file than the content addition would be. My
recommendation stands: write the two sections.

---

## 3. T5 / T6 — moot-status check against the actual planned cuts

### T5 (serif "Publication defaults" vs. sans-serif skill-wide default)

**Fully moot.** T5 depended on three loci existing simultaneously: (a)
`data-visualization.md`'s serif/Times rcParams block labeled "Publication defaults" with
no venue qualifier, (b) `style-guide.md`'s venue→font mapping table (which was the one
place that *correctly* explained serif is right for ML-conference LaTeX templates), and
(c) `SKILL.md`'s Goal 2 pointer that routed readers to sans-serif-only files without
differentiating venue type.

- (a) is cut: chairman's `data-visualization.md` ruling explicitly cuts "the rcParams
  'Publication defaults' setup block" in full.
- (b) is cut: chairman's `style-guide.md` ruling explicitly cuts "'Typography' → Font
  Matching LaTeX Documents and Font Size Guidelines tables."
- (c) is cut: Goal 2 is removed from `SKILL.md` wholesale (see §1 above).
- Checked `design-principles.md` (a KEEP file) directly for residual font-family
  guidance: only one relevant line exists, `references/design-principles.md:98` — "One
  font family; vary weight (regular, bold) rather than switching fonts" — this is
  generic typographic-consistency advice with no serif/sans-serif claim, no venue
  claim, and no contradiction with anything. Confirmed no remnant.

No kept file asserts a font-family default of any kind after the plan executes, so there
is nothing left to contradict. Nothing to fix beyond confirming the four cuts above
actually happen as described.

### T6 (DPI on vector PDF; numeric disagreement across 3 files)

**Fully moot.** All four original loci are gone under the plan:
- `journal-requirements.md` (Nature: "1000-1200 DPI") — DELETE, whole file.
- `publication-guidelines.md`'s "Resolution and File Format" → "Resolution Requirements"
  section (lines 12-17, "600-1200 DPI") — confirmed present in the current file and
  explicitly on the chairman's cut list ("Resolution and File Format" is named). Its
  sibling "Journal-Specific Considerations" section (line 198, `**Nature journals**: RGB,
  300 DPI minimum...`) is also independently cut ("pointer to the now-deleted
  `journal-requirements.md`") — so both DPI mentions in this file are covered, not just
  one.
- `matplotlib-examples.md` Example 10 — read directly (`references/matplotlib-examples.md:497-570`):
  confirmed it is a self-contained, cuttable unit — Nature 89mm sizing, panel-label
  convention, and the `fig.savefig('nature_figure.pdf', dpi=1000, ...)` /
  `fig.savefig('nature_figure.png', dpi=300, ...)` pair are the *only* place in the whole
  example, and nothing outside Example 10 depends on it. Chairman's plan cuts "Example
  10 in full" — confirmed this is a clean, complete removal of the dpi-on-vector-PDF bug
  with no fragment left behind.
- `assets/nature.mplstyle`'s unimplemented "1000 for line art, 600 for combination"
  comment — DELETE, whole file.

One adjacent thing checked and ruled irrelevant to T6: `SKILL.md`'s Databricks Rendering
code sample (kept) still has `fig.savefig(out.with_suffix(".png"), dpi=300)` — this is a
generic raster-PNG-for-inline-display instruction with no journal/vector-PDF framing and
no cross-file numeric claim attached to it, so it does not resurrect T6.

**Minor residual note (not T5/T6, adjacent):** T9 (Example 6's bare `'r-'` red vs. the
file's "all examples use colorblind-friendly palettes" overview claim) is very likely
also moot, since the chairman's keep-list for `matplotlib-examples.md` names Examples 1,
4, 7, and 9 specifically and Example 6 is not among them — but the ruling doesn't say
"cut Examples 2/3/5/6/8/10" explicitly, it says "Cut: ... Example 10 in full" only by
name. If the editor executes the plan literally (keep exactly 1/4/7/9, drop everything
else by omission), T9 is moot. If Example 6 is accidentally left in during the prune,
T9's bug reactivates. Flagging so the fix pass treats "which examples survive" as an
explicit list, not an inference.

---

## 4. Cross-check: KEEP files referencing DELETE-marked files

Grepped all seven KEEP-listed files (`audience-adaptation.md`, `chart-selection.md`,
`causal-inference-charts.md`, `design-principles.md`, `grammar-of-graphics.md`,
`narrative-structure.md`, `clutter-elimination.md`) for any mention of
`journal-requirements.md`, any `.mplstyle` filename, `style_presets`,
`banking-visualization`, or `plotnine-visualization`.

**Result: zero matches.** None of the seven KEEP files reference any DELETE-marked file
or the two already-deleted sibling skills. These seven are clean and require no
dangling-reference fixes from this cross-check. (They still carry whatever
content-level issues other council members raised in Round 1, if any — this check was
scoped only to references-to-deleted-material, per the task.)

The only KEEP-marked *section* found with a dangling reference is `SKILL.md`'s own
Databricks Rendering section (finding 5 in §1) — which is inside `SKILL.md`, not one of
the seven separately-listed reference files, but is explicitly called out as KEEP by the
chairman and therefore fits this cross-check's intent. Included above rather than
repeated here.

---

## Summary

| # | Finding | Status |
|---|---|---|
| SKILL.md dangling refs | 6 hard references (NYT theme in decision tree; dead banking-visualization link; NYT-style Goal 3 prose; `style_presets` in kept Databricks section; 2 Resources-list lines) + 1 numbering orphan (Goal 3 without Goal 2) + 1 stale self-description | Must fix in same pass as the prune |
| T7 | Recommend **writing** KS Curve + PSI Stability Chart sections in `model-evaluation-viz.md`, not deleting the table row — `audience-adaptation.md` (clean KEEP file) already depends on these chart types existing by name | Action: write content |
| T5 | Fully moot — all three source loci (data-visualization.md rcParams block, style-guide.md font table, SKILL.md Goal 2) are cut; design-principles.md checked clean | No fix needed beyond confirming the cuts |
| T6 | Fully moot — all four source loci (journal-requirements.md, publication-guidelines.md Resolution section, matplotlib-examples.md Example 10, nature.mplstyle) are cut; Example 10 confirmed cleanly self-contained | No fix needed beyond confirming the cuts |
| Cross-check (7 KEEP files) | Zero dangling references to DELETE-marked files | Clean |
