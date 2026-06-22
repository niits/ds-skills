# ds-skills — Review Plan & Findings

Working document for the multi-turn council review.
**Turn 1 (overall repo)** = feedback only. **Turns 2+** = per-skill, apply edits directly.
Decisions locked: *fix existing content only* (defer new skills + shared-council extraction).

---

## Turn 1 — Overall repo findings (DONE, feedback only)

Synthesized from 3 council lenses (skill-authoring / content-coverage / cross-skill consistency).
Highest confidence = surfaced in ≥2 lenses (marked ★).

### A. Structural

| # | Sev | Finding | Fix |
|---|-----|---------|-----|
| S1 ★ | High | README L9 claims **every** skill ships `agent_council/review_council.py`, but `feature-onboarding` has none. | Add council OR soften README. (infra — deferred) |
| S2 | High | 3/6 `description` frontmatters lack "Use when…" trigger (`databricks`, `metrics-evaluation`, `feature-onboarding`); `databricks` is a 209-word feature list. | Rewrite each: lead with "Use when…", ≤80 words. |
| S3 ★ | High | `databricks/SKILL.md` = 890 lines; Steps 4/7/8 + Feature-Eng quick-ref duplicate existing reference files. | Compress to routing summaries → target ~300–350 lines. |
| S4 | High | `review_council.py` duplicated ×5; ~145/240 lines byte-identical infra. | Extract `shared/review_council_base.py`. (infra — deferred) |
| S5 | Med | Naming split kebab vs snake_case; 3 snake_case outliers inside `visualization/references/`. | Pick one rule for `.md`; document; rename outliers. |
| S6 | Med | `metrics-evaluation` uses `foundations/diagnosis/business/domains/` not `references/`. | Document subdir layout is skill-specific (no forced rename). |
| S7 | Med | README taxonomy: `feature-onboarding` floats with no parent heading; DBFS-adaptation claim false for `feature-onboarding`/`metrics-evaluation`. | Give it a home; scope the DBFS claim. |
| S8 | Med | `metrics-evaluation/agent_council/review_council.py` module docstring in Vietnamese (README mandates English). | Translate to English. |
| S9 | Low | `shared/` holds only `nyt_theme.py`; `visualization/assets/color_palettes.py` is reusable but trapped. | Promote to `shared/`. (infra — deferred) |
| S10 | Low | `visualization/SKILL.md` L136 import fails without `sys.path` wiring. | Show path-insertion snippet. |

### B. Content contradictions / duplication (cross-skill)

- **★ PSI≥0.25 action contradicts**: `banking-visualization/references/credit-risk-charts.md` says "retrain"; `feature-onboarding/references/stability_and_oot.md` teaches against auto-retrain. → Align banking-viz to careful version + cross-link. (**source of truth = feature-onboarding**)
- **Two `lead_scoring.md`** (metrics-evaluation vs feature-onboarding): complementary; only one-way cross-link exists → add inverse link.
- **"point-in-time" / "tautology"** defined only in feature-onboarding; metrics-evaluation uses undefined → add pointers.
- Minor SWD "pre-attentive" concept bleed into banking-visualization → defer to visualization.

### C. Coverage gaps (things to add — DEFERRED, not this pass)

1. Model Training & HPO (biggest gap: features→eval has no training skill).
2. Databricks platform depth (Unity Catalog, Feature Store, DLT, AutoML, Mosaic AI Model Serving).
3. Production monitoring & drift (no skill owns the always-on loop).
4. Secondary: general A/B / online experimentation, data-quality/validation, problem-framing, causal/uplift.
5. Domain balance: banking over-represented; fraud/NLP/time-series absent.

---

## Per-skill processing queue (Turns 2–7)

Each turn: review for correctness + clarity, then **apply edits** (remove inaccuracies, clarify, fix cross-skill contradictions). All content English.

- [x] **Turn 2 — databricks** DONE: frontmatter rewritten ("Use when…"); fixed point-in-time/time-travel conflation (Step 4 Pattern 2, leakage warning added); MLflow Pattern 3 now leads with UC aliases (stages = legacy note), Pattern 4 + checklist updated; softened "10x" → sketch-based/much-faster; flagged SKEW as Databricks-specific + auto-broadcast 10MB default note; trimmed Step 7 EDA + Feature-Eng quick-ref + Step 8 Arrow/createDataFrame to routing summaries (890→814 lines). REMAINING (optional): further trim Step 4/5 PySpark pattern blocks that duplicate join_strategies.md / window_aggregation_patterns.md.
- [x] **Turn 3 — feature-onboarding** DONE: skill is high-quality (passed prior expert reviews) — verified PSI guidance (confirmed source-of-truth: "don't auto-drop, distinguish drift vs pipeline breakage"), IV half-open bands, as-of/leakage treatment all correct. Only real fix: frontmatter rewritten to lead with "Use when" (S2). No manufactured edits.
- [x] **Turn 4 — metrics-evaluation** DONE: frontmatter → "Use when" (S2); translated VN docstring in review_council.py → English (S8); added inverse cross-link to feature-onboarding in domains/lead_scoring.md; added point-in-time definition pointer in diagnosis/patterns.md (line 309).
- [x] **Turn 5 — visualization** DONE: frontmatter already had "Use when" (no change). Renamed 4 snake_case outliers → kebab (color-palettes, journal-requirements, matplotlib-examples, publication-guidelines; repo agent missed matplotlib_examples) via git mv + updated ALL cross-refs (SKILL.md, matplotlib-examples.md, publication-guidelines.md, review_council.py focus_files); verified clean. Fixed S10: added `sys.path.append("..")` to Goal 3 nyt_theme import snippet.
- [x] **Turn 6 — banking-visualization** DONE: fixed the PSI≥0.25 contradiction (credit-risk-charts.md) — now "investigate first, distinguish drift vs pipeline breakage, don't auto-retrain", half-open intervals, + pointer to feature-onboarding stability_and_oot.md (the source of truth). Anchored "pre-attentive" term to visualization/references/pre-attentive-attributes.md (light touch — usage was correct application, not duplication).
- [x] **Turn 7 — banking-hypothesis-generation** DONE: strong skill, frontmatter already had "Use when". Added scope-distinction note vs feature-onboarding Phase 2 (model/phenomenon-level investigation hypothesis vs per-feature design hypothesis) to resolve the overlap flag. No inaccuracies found.
- [x] **Final — repo cleanup** DONE (content-only): README S1 softened ("Most skills ship… feature-onboarding does not yet"); S7 gave feature-onboarding an "ML-pipeline skills" parent heading + scoped the DBFS-adaptation claim to asset-shipping skills only.

### Deferred (infra / new skills — separate decision)
S1 add council, S4 shared council extraction, S9 promote color_palettes, all of section C.
