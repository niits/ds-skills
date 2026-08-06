# Round 8 — Correctness and Effectiveness Audit

Adversarial council review of the post-refactor skill. Five independent members,
one round. Members had read-only access and no knowledge of each other's findings.

## Question

Is `skills/metrics-evaluation` (a) technically correct — do its metric definitions,
statistical claims, and thresholds hold up against the literature — and
(b) operationally effective — does an agent loading `SKILL.md` route correctly and
produce a better evaluation than one that does not?

Out of scope: `agent_council/` records, other skills, prose style.

## Roster

| Member | Role | Assigned question |
|---|---|---|
| M1 | evidence-researcher | Factual correctness of every claim in `topics/` |
| M2 | source-verifier | `references/citations.md` validity + domain metric definitions vs. defining papers |
| M3 | assumption-challenger | Premises behind the skill's design; whether correctness is the right axis |
| M4 | counter-example-finder | Falsify "loading this skill improves the evaluation" |
| M5 | evidence-researcher | Link integrity, duplication, token cost, rule actionability, frontmatter |

## Verdict

Correctness: high. Effectiveness: coverage gaps and one literal-application bug.

## Confirmed defects

Chair verified each of the following directly against the file.

| # | Defect | Locator | Severity |
|---|---|---|---|
| 1 | Majority-class baseline formula is binary-only under a generic `## Classification` header. Applied to a 5-class problem with a 40% majority class it yields 60% instead of 40% — direction-flipped. | `topics/core/baselines.md:19-22` | High |
| 2 | Root README points at `skills/metrics-evaluation/foundations/citations.md`, which does not exist. Real path is `references/citations.md`. | `README.md:144` | Medium |
| 3 | Root README lists `business/` and `foundations/` as live supporting directories; neither exists anywhere in the repo. Line 53 correctly describes the new layout — the README contradicts itself. | `README.md:51-53` | Medium |
| 4 | `domains/credit.md` and `domains/fraud.md` deleted with no replacement. `KS statistic`, `Gini coefficient`, `disparate impact`, `adverse action`, `reject inference` now return zero matches skill-wide, while the root README chains `feature-onboarding` (credit scoring) into `metrics-evaluation` for the shipping verdict. | `README.md:47-48`, `README.md:64-71` | Medium |
| 5 | NDCG formula `rel_i / log2(i+1)` cited to Järvelin & Kekäläinen (2002). That paper defines DCG recursively with no discount below rank `b`. The `log2(i+1)` form is a later convention. | `domains/recommendation.md:58-63`, `references/citations.md:22` | Low |
| 6 | The only OCR citation is Morris, Maier & Green (2004), a connected-speech-recognition paper. It does not define CER and does not address OCR. The CER formula at `ocr.md:26` has no supporting citation in the repo. | `references/citations.md:34` | Low |
| 7 | Yurdakul PSI citation conflates the 2018 single-author WMU dissertation with the 2019 Yurdakul & Naranjo journal article. | `references/citations.md:15` | Low |
| 8 | Unsourced numeric claim: "In many products, new users = 30-50% of daily active users." | `domains/recommendation.md:245` | Low |
| 9 | Six of seven domain files never link to `references/citations.md` despite `citations.md` carrying dedicated sections for four of them. | `domains/vision/*`, `domains/representation_learning.md`, `domains/customer_analytics/*` | Low |
| 10 | `description` omits anomaly detection, recommendation, churn prediction, lead scoring — all of which the skill routes. Triggering-accuracy gap. | `SKILL.md:3` vs `SKILL.md:36,41-42` | Low |

## Coverage gaps (M4)

Task families with no route and no file: multi-label classification; semantic
segmentation (no routing row; `object_detection.md` is instance/box-AP framed);
probabilistic forecasting (no pinball loss, CRPS, or interval-coverage guidance
despite `description` naming forecasting); time-series anomaly-detection
point-adjustment inflation (anomaly detection is named in the routing table);
LLM/generative-output evaluation.

## What held up under attack

- M1 audited the paired-interval decision table at `topics/core/evaluation_protocol.md:36-43`
  by exhaustive case analysis. It is two three-way partitions, each mutually
  exclusive and jointly exhaustive, with consistent boundary handling. No gap, no overlap.
- M2 confirmed all 16 entries in `citations.md` resolve to real papers with correct
  venues. No fabricated citations.
- M2 confirmed COCO AP conventions, HOTA/DetA/AssA/LocA, MOTA negativity, IDF1, and CER
  are accurate as stated.
- M1 confirmed MASE, RMSSE, PR-AUC-vs-AP interpolation, the prevalence baseline for AP,
  the AUC-ROC-does-not-inflate-under-imbalance correction, and micro/macro aggregation.
- M2 found no unsupported numeric thresholds in the domain files beyond item 8. Where a
  threshold could have been asserted, the files say "no verified threshold" instead.
- M5 found zero content contradictions and zero dangling links inside the skill's own tree.
- M4 tried to break the Evidence Gate into producing improper refusals and failed:
  `topics/core/evaluation_protocol.md:63-67` requires substantive partial evaluation when
  no baseline exists, and the gate text is scoped to the requested decision conclusion.

## Unresolved dispute

**Evidence Gate: quality gate or refusal trap.** Interpretive, not settleable by
further research.

- M3: for the most common real request ("Model A AUC 0.85 vs Model B 0.80, which ships?"),
  4+ of 9 applicable gate items are missing, so the gate fires as literally written.
  The `< 2 hours` fast path that would relieve this lives in
  `topics/diagnosis/checklist.md:5-9`, which the workflow loads only for weak or
  suspicious results — not for a ship decision, which routes to
  `topics/reporting/evaluation_report.md` where no equivalent leniency exists.
- M4: the gate is scoped to "the requested decision conclusion," and Hard Rule 1
  (`SKILL.md:55`) requires stating a baseline or explaining why none applies rather than
  refusing. Partial hedged answers are the designed behaviour.

Both readings are supported by the text. The gate's real firing rate is an empirical
question about agent interpretation that static review cannot settle.

## Falsified prior-round decision

Round 3's log records: "No compatibility stubs were retained for old paths because no
external path consumer was established." An external path consumer existed — the root
`README.md`, which still carries three stale references (defects 2 and 3). The Round 3
premise was wrong.

## Rule actionability (M5)

Of the 10 Hard Rules at `SKILL.md:55-68`: 5 mechanically checkable against the agent's
own output; 4 require facts only the user or environment supplies; 1 unverifiable prose
(`SKILL.md:66`, "diagnose instead of describe"). All 11 Evidence Gate items require
externally supplied facts.

## Token cost (M5, estimates)

| Path | Tokens |
|---|---|
| `SKILL.md` alone | ~1,130 |
| Always-loaded (`SKILL.md` + `evaluation_protocol.md`) | ~2,240 |
| Typical single-domain | ~7,950 |
| Worst case (everything routable) | ~24,000 |

Conditional loading saves roughly 3x typical-vs-worst and 10x minimal-vs-worst,
conditional on the agent honouring the routing table rather than reading defensively.

## Compliance risk (M3)

The file-loading step at `SKILL.md:19-21` is phrased as a descriptive clause, not an
imperative. Every hard deontic marker in the document (`INSUFFICIENT EVIDENCE`,
`SKILL.md:47`) governs output rules. The prerequisite for all of them — actually reading
the routed file — carries the weakest instruction force in the file. Nothing in the skill
or in CI verifies that loading occurred.

## Chair's note

Council output is a report. No file under `topics/`, `domains/`, `references/`, or
`SKILL.md` was modified by the council itself. Remediation was a separate, user-authorized
step, recorded below.

---

## Remediation (user-authorized, after the report)

The user directed: correct all content, and remove the vision domain. On the credit/fraud
question the user chose deletion over restoration, stating the domain is outside their
expertise and they could not verify correctness. That is recorded as a deliberate scope
decision, not an oversight.

### Scope removals
- Deleted `domains/vision/ocr.md`, `domains/vision/object_detection.md`,
  `domains/vision/multi_object_tracking.md`.
- Deleted `topics/core/structured_output_matching.md`. It existed only to serve the three
  vision overlays and became orphaned; nothing else routed to it.
- Credit and fraud remain deleted by decision. The root README now states the gap
  explicitly rather than implying coverage.

### Defect fixes

| # | Resolution |
|---|---|
| 1 | `topics/core/baselines.md`: binary section retitled and scoped. Added Multi-Class section with the correct majority baseline `max_c p_c`, uniform-random `1/C`, and prior-matching `Σ p_c²`, plus an explicit warning that `1 - positive_rate` is wrong for `C > 2`. Added Multi-Label section with per-label, subset-accuracy, and label-powerset baselines. |
| 2 | `README.md:144` repointed to `references/citations.md`. |
| 3 | `README.md:51-53` no longer lists `business/` and `foundations/`. |
| 4 | Root README skill table and workflow step 4 now state that credit/fraud overlays do not exist and that KS, Gini, and fair-lending checks are not covered. |
| 5 | `references/citations.md`: NDCG entry now records that the `log2(i+1)` form is the later TREC convention, not the formula in Järvelin & Kekäläinen (2002), and requires stating the convention before cross-system comparison. |
| 6 | Morris et al. (2004) removed with the OCR section. |
| 7 | PSI entry split into the 2018 dissertation and the Yurdakul & Naranjo (2020) journal article, flagged as one work rather than two sources. |
| 8 | `domains/recommendation.md`: the unsourced "30-50% of DAU" claim replaced with an instruction to measure the product's own new-user share. |
| 9 | Citation links added to `churn_prediction.md` (Qini) and `representation_learning.md` (linear-probe protocol). |
| 10 | `SKILL.md:3` description rewritten to name every routed task family. |

### Coverage added (user-selected)
- **Multi-label classification**: baselines, the micro/macro/weighted/sample averaging
  table, per-label thresholding, label-correlation resampling, checklist block, report
  profile, KPI row.
- **Probabilistic forecasting**: empirical-residual and climatological baselines, pinball
  loss formula, CRPS, propriety, PICP with mandatory width reporting, per-horizon
  coverage, checklist block, report profile, KPI rows. Gneiting citations added.
- **Anomaly point-adjustment trap**: warning in `topics/core/baselines.md` with the
  required handling and the Kim et al. (2022) citation.

The user did not select the explicit out-of-scope block; LLM/generative evaluation,
survival analysis, and uplift-model evaluation remain uncovered and unmarked.

### Evidence Gate
The unresolved M3/M4 dispute was closed by making the narrow reading explicit in the text
rather than leaving it to inference. `SKILL.md` now states that the gate governs the
requested decision conclusion only, that descriptive and partial-evidence answers stay in
scope, and that a question answerable with a correctly scoped conclusion must not be
refused. `matching protocol` was dropped from the gate list with the vision removal,
leaving 10 items.

### Also corrected
- Multi-class AUC-ROC disclosure requirement (one-vs-rest / one-vs-one, macro / weighted).
- Micro-averaged precision, recall, F1, and accuracy noted as identical under single-label
  multi-class assignment, so reporting several is not corroboration.
- `mAP` disambiguated: per-class one-vs-rest AP averaging versus per-query ranking MAP.
- `Lift = AP_model / positive_rate` given its missing `[Definitional]` provenance tag.
- Isotonic calibration nuance: non-decreasing rather than strictly increasing, so it merges
  scores into ties and reduces the number of distinct operating points.
- Vision vocabulary (boxes, frames, crops, scenes, annotation units, matching/ignore rules)
  removed from `evaluation_protocol.md`, `checklist.md`, `kpi_mapping.md`, and
  `evaluation_report.md`; the retrieval/identity language representation learning needs was
  kept.
- `topics/decision/kpi_mapping.md` and `topics/decision/impact_translation.md` now named
  individually in the Topic Index, matching how `topics/diagnosis/` files are listed.
- Stale cross-skill path in `skills/feature-onboarding/domains/lead_scoring.md:6` repointed
  to `domains/customer_analytics/lead_scoring.md`.

### Verification
- Every `topics/`, `domains/`, `references/` path referenced anywhere in the skill resolves
  to an existing file: 0 dangling.
- Every existing normative file is named in `SKILL.md`: 0 orphans.
- Repo-wide grep for `foundations/`, `business/`, `domains/vision`,
  `structured_output_matching`, `domains/credit`, `domains/fraud`,
  `domains/churn_prediction`, `domains/lead_scoring`, `diagnosis/patterns`: no stale hits
  remain outside `agent_council/` records.
- `SKILL.md` frontmatter parses as valid YAML.
- Corpus is 1,905 lines across 14 normative files, down from 2,245 across 18.

Not verified: whether an agent actually loads the routed files, and the Evidence Gate's
real firing rate. Both need live transcript sampling. The M3 compliance finding stands
unaddressed — `SKILL.md:19-21` still phrases file loading as a descriptive clause.
