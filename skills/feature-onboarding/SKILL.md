---
name: feature-onboarding
description: Use when onboarding a new feature group into a supervised ML pipeline for lead scoring or credit scoring (binary, ranking-oriented) and you need to gate it against leakage, definitional tautology, redundancy, and out-of-time drift before production. Covers source-semantics verification, hypothesis-first feature design, IV/WoE screening, incremental-lift selection, point-in-time audits, PSI and out-of-time stability, mode-dependent null handling, and a predeclared Go/No-Go gate. Includes an unsupported recommendation-system design roadmap; examples use PySpark.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: ds-skills
    domain: lead scoring / credit scoring
    primary-label-type: binary classification
---

# Feature Onboarding for Supervised ML

## Overview

A disciplined process for taking a **new feature group** from idea to production code, with gates that catch the failures that actually kill models in production: **leakage**, **tautology**, **redundancy**, and **distribution drift**.

This skill supports **lead scoring** and **credit scoring** — binary labels, ranking-driven decisions, regulated or semi-regulated settings. `domains/recsys_extension.md` is an unsupported design roadmap, not an executable extension.

> **Core stance**: High univariate IV does *not* validate a feature. A feature earns its place only after it survives leakage checks, adds **incremental model lift** beyond existing features, and stays **stable out-of-time**. Everything before that is a filter, not a verdict.

> **Hypothesis before compute**: Every feature must originate from a *reason* — source
> semantics, the business problem, and the subject's domain/operational reality. **Do
> not generate features mechanically** (no "multiply every column pair", no feature
> factory, no compute-first-rationalize-later): it wastes compute, inflates the
> multiple-testing problem, and buries real signal. If you can't state *before
> computing* what a feature measures and why it should relate to the label, don't
> compute it. The enforcement is the **Phase 2 hypothesis artifact** and **Anti-pattern
> #15**; this is the principle behind them.

---

## Pick your Model Mode first

The whole pipeline branches on one decision. Make it before Phase 1 and keep it consistent.

| Decision | **Scorecard mode** (WoE + logistic) | **GBM mode** (tree ensemble) |
|---|---|---|
| Typical use | Credit scoring, regulated lending | Lead scoring, internal ranking |
| Binning | Supervised binning fitted on train; features enter as WoE | Optional; raw values may be used |
| Null handling | Must define every value → bin nulls as own group or impute + flag | Use native missing routing only when the chosen estimator and serving stack support it; otherwise impute + flag |
| Monotonicity | Common governance default; require when policy or domain reasoning calls for it | Optional monotone constraints |
| Redundancy tolerance | Low — multicollinearity breaks coefficient interpretability | Higher — trees tolerate correlated inputs |
| Fairness / proxy check | Required by applicable decision-domain governance, not model family | Required by applicable decision-domain governance, not model family |

`★` If you cannot answer "scorecard or GBM?" yet, GBM may be used for explicitly provisional exploration. A later mode change requires rerunning every mode-dependent phase, transformation, criterion, lift comparison, and validation result; GBM selection does not validate a WoE/logistic scorecard.

See `references/null_handling.md` and `domains/credit_scoring.md` for the consequences of each mode.

---

## The 12 Phases

Phases 1–7 use **development data**: fit bins, imputers, transformations, and models on train; make feature-selection decisions on chronological validation folds using only train-fitted artifacts. Phase 8 evaluates the frozen pipeline once on an untouched, later OOT window. If that result causes any revision, the inspected window becomes development data and a new untouched future holdout is required. Phases 9–12 are engineering and release work, not opportunities to tune on OOT.

### Phase 1 — Data Source Understanding
**Goal**: Understand the source table before computing anything.
1. Identify source table, schema, **granularity** (what does 1 row represent?).
2. **Verify column semantics with formula checks — never assume.** Reconcile candidate formulas over representative entities and periods using type-aware tolerances, units, null semantics, and documented exceptions; record the evidence and decomposition trees.
3. Data range: time-dimension min/max, row count per period.
4. Coverage: what % of target entities appear in this table?
5. Null rates for key columns.
6. Mutual exclusivity (columns that never co-occur on a row).

**Output**: documented columns + confirmed formulas, data range, coverage stats.

### Phase 2 — Feature Hypothesis Formulation
**Goal**: Design and name features by **observable phenomenon**, not assumed business meaning — and **justify each one before computing it**.

**Required artifact — feature decision ledger** *(start it before Phase 3 touches any data and update it through Phase 9)*. One row per candidate records: name and formula; verified source semantics and lineage; population and grain; hypothesis; event/effective time; recorded/available time; scoring cutoff and boundary convention; null meaning; lag definition; model mode; predeclared screening, lift, stability, and uncertainty criteria; phase results; final decision and reason; owner; and data/code versions.

The hypothesis field uses this format:

> `feature_name` — *from* `<source column(s) / their verified semantics>` — *measures* `<subject behavior/state>` — *expected to relate to the label because* `<business / domain reasoning>`.

If you cannot complete that sentence, the feature is not ready to compute. This is the gate against brute-forced, speculative features that waste compute and inflate false discoveries. The hypothesis must be rooted in three things together:
1. **Source-data semantics** — the *verified* meaning of the columns (from Phase 1 formula checks), not their names.
2. **The business problem** — what decision the model drives (rank leads for SDRs? approve credit?) and what behavior actually moves that outcome.
3. **Domain/operational reality** — how the subject behaves and how the institution's processes generate the data (billing cycles, funnel stages, product mechanics).

Every feature must answer: *"What behavior or state does this measure from the subject's perspective?"* Group into:
- **Structure** (point-in-time snapshot at T): concentration index, share, per-unit intensity, count, ratio.
- **Temporal** (change over time): MoM pct_change, lag-N diff, volatility, streak.

Before computing a candidate, establish its temporal eligibility in the ledger. Define the exact scoring timestamp, non-overlapping label interval, source event/effective timestamp, source recorded/available timestamp, and whether each cutoff is open or closed. A closed period may use `≤ T` only when the source is finalized before scoring; event-driven scoring normally uses feature data `< T` and outcomes `(T+g, T+g+h]`, unless a stable sequence key proves transaction order. If historical values cannot be reconstructed as they were knowable at each cutoff, mark the candidate **BLOCKED**.

**Name by formula/measurement, never by assumed meaning:**
- Good: `dep_share`, `per_acct_mom_pct`, `hhi`, `eom_to_peak_ratio`
- Bad: `loyalty_score`, `risk_indicator`, `salary_ratio`

**Design red flags** (see `references/leakage_and_tautology.md`):
- Measures an **internal institutional metric** rather than subject behavior (changes when *policy* changes, not when the *subject* changes).
- Is a **direct proxy for the label definition** (tautology).
- **Binary flag for a tiny population** → insufficient variance.
- **Assumes causation from correlation** (naming a peak inflow "salary" without evidence).

### Phase 3 — Prototype in Exploration Notebook
**Goal**: Compute temporally eligible features quickly and check signal exists.
- Dedicated exploration notebook, separate from pipeline code.
- Load label + target population (observation periods only); load raw data over observation **+ historical** periods (enough for lag computation).
- **Single read** of source → **single heavy aggregation** → **persist one intermediate** → derive multiple outputs from it (aggregates, concentration metrics, pivots, lags). Keep distributed; no driver materialization; no diagnostic counts in production-bound code. (See the `databricks` skill for the join-chain mechanics.)

**Output**: structure-features DF, temporal-features DF, named column lists per group.

### Phase 4 — Predictive Power (IV/WoE) — *filter*
**Goal**: Quantify discriminative signal cheaply, to **prune**, not to decide.

> **Scope**: IV/WoE assume a **binary label**. For regression/multiclass targets use the alternatives in `references/predictive_power.md`.

Method, thresholds, and the practical traps (zero-event bins → ±∞ WoE, sparse/tie features that won't split into 10 deciles, **minimum event count per bin**, rare-event instability) are in `references/predictive_power.md`.

| IV | Strength | Action |
|---|---|---|
| ≥ 0.3 | Strong | Keep — but ≥ 0.5 is "too good to be true": **suspect leakage**, verify in Phase 6 |
| [0.1, 0.3) | Medium | Keep |
| [0.02, 0.1) | Weak | Keep **only if** orthogonal AND it adds lift (Phase 5) |
| < 0.02 | Useless univariately | Drop — **unless** kept for a known interaction (univariate IV misses interactions) |

*(Bands are half-open — `[a, b)` — so each IV falls in exactly one row; `predictive_power.md` subdivides the top into `[0.3, 0.5)` strong / `[0.5, 0.8)` suspicious / `≥ 0.8` verify-hard-but-don't-auto-reject.)*

**Red flag**: non-monotonic event rate across bins — but distinguish *genuine non-linearity* from *small-sample noise* using the min-event-per-bin rule before concluding.

### Phase 5 — Redundancy & Incremental Lift
**Goal**: Confirm the feature carries genuinely **new** information *and* improves the model.

This is two checks, not one (see `references/redundancy_and_lift.md`):

1. **Redundancy** — use **Spearman** (rank), not just Pearson, so monotonic non-linear duplication is caught. Pairwise `|r|` is *not enough*: a new feature orthogonal to each existing feature individually can still be a linear combination of several. Add a **multivariate check** (VIF, or R² of regressing the new feature on the existing set). In scorecard mode, calculate coefficient-collinearity diagnostics on the train-fitted WoE design matrix; raw-column VIF is only exploratory. In GBM mode, correlation is a diagnostic, not a drop rule.

| `|r|` | Interpretation | Action |
|---|---|---|
| ≥ 0.7 | Highly redundant | Investigate with mode-specific ablation and governance needs |
| [0.5, 0.7) | Moderate overlap | Compare stable conditional/group lift |
| [0.3, 0.5) | Some correlation | Keep — incremental info |
| < 0.3 | Orthogonal | Keep |

2. **Incremental lift (wrapper/embedded)** — IV/correlation are *filters*. Before locking a feature, confirm it **improves the model** through paired baseline-versus-candidate evaluation on identical chronological validation folds. Permutation importance and SHAP are usage/attribution diagnostics, not proof of incremental value; correlated groups require grouped/conditional diagnostics or explicit ablation. A feature with weak univariate IV can earn its place via interactions; a feature with strong IV can add nothing if its information is already in the model.

**Hypothesis to test**: rate-of-change features can be near-orthogonal to level features. Keep both only when measured redundancy and validation ablation support it.

### Phase 6 — Leakage & Tautology
**Goal**: Verify in implemented lineage and code that the pre-computation eligibility check was correct. Two distinct failure families (full detail in `references/leakage_and_tautology.md`):

**6a. Temporal / point-in-time leakage** — *the most common real-world leak.*
- Draw the timeline: `feature cutoff T → [optional gap g] → label window [T+g, T+g+h]` and declare endpoint conventions.
- Assert every input satisfies the ledger's event/effective-time and recorded/available-time predicates, including late-arriving or restated rows.
- No post-outcome field may enter the snapshot.
- A feature can have `|r| < 0.3` with a label proxy and *still* leak by using future data.

**6b. Definitional tautology.**
1. **What defines the label?** (threshold on which metric? horizon?)
2. **Does the feature contain, reconstruct, or overlap the realized label-window quantity?** A historical pre-cutoff measurement of the same kind of quantity can be a valid predictor; identity of variable type alone is not tautology.
3. **Causal direction**: feature → label (predictive) OK; same root cause → both (co-symptoms) OK but weaker; feature ≈ label (same quantity) → **drop**.

**Verification aid**: correlate the suspect feature with a direct proxy of the label metric. Any cutoff is only an investigation trigger: low correlation does not clear a feature, and high correlation does not prove circularity. Decide from lineage, timing, formula overlap, and production availability.

> **Key lesson**: An IV of 0.9 that comes from measuring the label's own definition is worthless — circular reasoning disguised as signal.

### Phase 7 — Lag Horizon Analysis
**Goal**: Choose optimal lag horizons for temporal features.
1. Determine earliest available period.
2. Coverage per lag (lag-N first usable obs = `data_start + N`).
3. **Collinearity between lags** (lag-1 vs lag-3 usually `> 0.5`).
4. Compare IV across horizons.

| Criterion | Short (1) | Medium (3) | Long (6) |
|---|---|---|---|
| Coverage | Highest | Medium | Lowest |
| IV | Highest (recency) | Medium | Medium-term |
| Collinearity w/ short | — | High | Lower |
| Illustrative role | Often recent | Often overlapping | Often longer-term |

**Selection**: treat the table as an illustration, not a verdict. Select horizons from measured coverage, stable validation lift, and redundancy. Define lag-N as exactly N calendar/business periods, not N preceding rows; use a complete entity-period spine or an exact-period keyed join. Never design lags longer than the source history supports.

> **Mode note**: the IV-vs-horizon comparison here is the binary *screen* and applies to both modes. In **scorecard mode** the surviving lag features still enter the model as WoE-binned characteristics, not raw values.

### Phase 8 — Stability & Out-of-Time Validation — *do not skip*
**Goal**: Confirm the feature holds up over time, not just in one validation slice (detail in `references/stability_and_oot.md`).
1. **PSI** of each feature's distribution across development periods — `PSI ≥ 0.25` is a default investigation trigger, not an automatic drop.
2. **IV by development period**, not only pooled IV — a feature whose IV collapses in recent development periods is dying.
3. **OOT confirmation**: after the complete pipeline is locked, evaluate it once on an **out-of-time** window after train/validation. Report the predeclared metrics and uncertainty. OOT failure produces NO-GO for that frozen configuration; do not diagnose, remove features, and retest on the same window.

### Phase 9 — Final Decision Recording
Record the frozen pre-OOT feature decisions and the OOT `PASS/NO-GO` result. Do not
change feature selection from the inspected OOT result; any revision requires a new
future holdout.

Use the predeclared criteria in the decision ledger. The numeric bands in this skill are review defaults, not universal laws. Drop a candidate for temporal leakage or proven label reconstruction; otherwise require evidence appropriate to sample size, uncertainty, operational cost, and model mode. Correlation, prevalence, null rate, IV, or PSI alone does not mandate removal.

**Keep priority** (high→low):
1. Strong IV (≥ 0.3) + orthogonal + adds lift.
2. Medium IV ([0.1, 0.3)) + orthogonal + adds lift.
3. Weak IV ([0.02, 0.1)) + highly orthogonal + measurable lift (new information despite weak univariate IV).
4. Medium IV + moderate correlation (0.3–0.5) + stable conditional/group lift, when interpretably distinct.

> **Mode note**: this priority is stated in IV terms (the binary screen). In **scorecard mode**, require compliance with the declared monotonicity policy, including any approved exception, and pass the fairness/reason-code filters from `domains/credit_scoring.md`; in **GBM mode**, prefer incremental-lift evidence from Phase 5 over raw IV.

**Null handling** is mode-dependent — see `references/null_handling.md`. Summary: establish structural absence from independent eligibility/ownership evidence, then encode as 0 plus an absence flag; keep unknown ratios and missing lag history missing unless the selected estimator requires a train-fitted representation. No prior observation is not zero change.

### Phase 10 — Module Implementation
**Function contract**: input = entity population, time range, optional lookback; output = `[entity_id, time_period, ...feature_cols]`; deterministic; handles partial history and null source.

**Computation**: single read (filter time + population early) → persist the heaviest intermediate **only when it fans out to ≥ 2 downstream branches/actions** → derive outputs. Before row-based lag, assert one row per entity-period and densify the declared calendar; otherwise use an exact-period keyed join. Prefer `MEMORY_AND_DISK`. No side effects (no writes, counts, or driver materialization).

> **`unpersist` footgun**: do **not** `unpersist()` the cached intermediate *before* returning a still-lazy derived DataFrame — Spark hasn't computed it yet, so releasing the parent forces a full recompute from source on the caller's first action, defeating the cache. Either materialize the result before unpersisting, or (cleaner for a library function) **don't cache inside the function at all** and let the caller own the cache lifecycle.

**Documentation**: feature groups + count; what was excluded and why; null convention; data-availability constraints (e.g. "source starts period X"); **model mode** assumed. Export feature-name constants. No implicit notebook-state dependencies.

### Phase 11 — Integration
1. Register the compute function in module exports.
2. Add the call to the feature pipeline.
3. Register the feature group in the project's feature store / persistence mechanism.
4. Reinstall/reload the package if needed.
5. Run end-to-end.

**Train/serve consistency** (the point of all the point-in-time work): the *same*
transformation must feed both offline training and online/batch scoring. Do not
reimplement the logic twice. On Databricks, the mechanism depends on *when* the feature
is computed:
- **Precomputed features**: `FeatureLookup` serves the *materialized values* — but only
  if you **publish the offline table to the online store** (sync/publish). The lookup
  alone does not recompute; it fetches what you published.
- **On-demand features** (computed at request time): require **on-demand feature
  functions** (Python UDFs registered in Unity Catalog), *not* a plain `FeatureLookup`.
- **Point-in-time training sets**: `create_training_set` only does the as-of lookup if
  you declare a **`timestamp_lookup_key`** — without it you get current values, i.e. the
  leak. This prerequisite *is* the point-in-time correctness this skill cares about.

Verify offline↔online **parity** on a sample and define freshness/TTL for the online
store. A feature that is point-in-time-correct offline but recomputed differently at
serving time reintroduces the skew you just eliminated.

**Reproducibility** means the same declared key set, schema, and feature values within declared numeric tolerances. Use deterministic window ordering with stable tiebreakers; record source versions, transform/code version, parameters, runtime and dependency versions, and seeds. Distributed execution does not generally guarantee byte-identical files or floating-point reductions.

**Verify** in a one-time integration/data-quality layer: declare the output primary key; assert uniqueness; reconcile expected and actual population keys with anti-joins in both directions; document intentional exclusions; validate schema, null rates, finite values, ranges, and period/source-coverage segments. Aggregate row counts are diagnostics, not proof of grain preservation.

**Production monitoring handoff**: before release, record monitored features and score, frozen reference bins/windows, freshness and publication lag, key uniqueness, coverage/null/range checks, feature/score drift, delayed-label performance, cadence, thresholds, owner, escalation action, and retraining/review trigger. Credit deployments also require governance-defined fairness and calibration monitoring.

**Integration stop condition**: train/serve parity, primary-key uniqueness, and finite-value integrity are unconditional hard stops. Release is `BLOCKED` until they pass. Approved dispositions may cover only declared semantic exceptions such as intentional population exclusions, expected nullable fields, or governance-approved freshness/range limits; record each exception explicitly.

### Phase 12 — Cleanup
Move the exploration notebook to an experiments directory; strip diagnostic cells from production code; fix moved relative paths; prepare a change summary and suggested commit message. Commit only when explicitly authorized by the host workflow or user.

---

## Go / No-Go Gate

Before Phase 10 (implementation), **all** gates must PASS:

| Gate | Criterion |
|---|---|
| Data OK | Unknown-data missingness and structural absence meet separate predeclared criteria; coverage is adequate for the intended decision |
| Predictive | At least one candidate or candidate group meets its predeclared univariate or interaction evidence standard |
| Adds lift | Frozen feature set exceeds a noise-aware, predeclared validation-lift threshold |
| Not redundant | Mode-specific ablation and model-matrix diagnostics justify retained overlap |
| Temporally safe | Every feature satisfies declared event/effective and recorded/available-time predicates; any gap is estimand- or latency-driven |
| Not tautological | Lineage and formula review finds no realized-label reconstruction or overlap |
| Stable | Drift triggers are investigated and dispositioned; the frozen pipeline passes one untouched OOT confirmation |
| Motivated | Every feature has a written hypothesis grounding it in source semantics + business + domain; none were generated mechanically |
| Conceptual | Measures subject behavior, not internal metric |
| Lag feasible | Source range supports exact-period lags with predeclared coverage |
| Mode-consistent | Binning, null handling, monotonicity, fairness all match the chosen Model Mode |
| Auditable | Decision ledger contains predeclared criteria, evidence, disposition, owner, and versions for every candidate |

Adopt or replace all default thresholds before viewing results. Undefined terms such as “adequate,” “measurable,” or “acceptable” produce **BLOCKED**, not discretionary PASS.

### Tiering — so the process isn't skipped wholesale

The full gate is realistic for a handful of credit characteristics; for a 200-feature lead-scoring group, refitting per-candidate lift, per-period IV, VIF, and bitemporal reconstruction for *every* feature is too heavy and teams will quietly drop to "IV filter only" — exactly the failure this skill warns against. So separate **non-negotiables** from **scale-as-you-can**:

- **Must run, every time (cheap or catastrophic if skipped)**: the temporal-leakage audit (Phase 6a), the tautology label-proxy check (Phase 6b), and the single OOT confirmation (Phase 8). These catch the silent disasters and cost little.
- **Run at the group level when per-feature is too heavy**: incremental lift on the *whole new group* rather than per-feature; vectorized IV/PSI across all features in one pass; VIF only on the features that survive the IV/lift screen.

State which tier you ran in the documentation. Never trade away the non-negotiables for throughput.

---

## Anti-patterns

1. **Skip the temporal-leakage check** — definitional tautology gets attention; point-in-time leaks (future / restated data) cause more silent disasters.
2. **Decide on univariate IV alone** — misses interactions (false negatives) and ignores whether the model actually improves (false positives). IV filters; lift decides.
3. **Pearson-only redundancy** — misses non-linear (use Spearman) and multivariate (use VIF/R²) duplication.
4. **Ship without OOT / PSI** — a feature strong in-sample but drifting is a time bomb.
5. **Assume column meaning** — verify with formula checks; internal columns have non-obvious semantics.
6. **Keep all lag horizons without evidence** — test every retained horizon with measured redundancy, coverage, and validation ablation.
7. **Name by assumed meaning** — name by what you measure.
8. **Include institutional-perspective features** — profitability/strategy metrics measure the *institution's* decisions, not subject intent.
9. **Ignore data availability** — long lags on short history = null-dominated features.
10. **Conflate "absent" with "unknown"** — prove structural absence from independent evidence before encoding 0 plus an absence flag.
11. **Materialize to driver during computation** — keep distributed until final viz/fit.
12. **Multiple reads of the same source** — persist one intermediate, derive many outputs.
13. **Validate selection on test/OOT** — fit artifacts on train and make selection decisions on development validation; OOT confirms the locked pipeline once.
14. **Mode-straddling** — WoE binning + "let trees handle NaN" in the same pipeline is incoherent. Commit to a Model Mode.
15. **Brute-forcing features / feature factories** — generating transforms en masse and screening afterward wastes compute and time, inflates multiple-testing false discoveries (Phase 5), and drowns real signal. Compute only features you can justify *in advance* from source semantics + business + domain (Phase 2). Quality and motivation over quantity.

---

## Resources

### references/
- `predictive_power.md` — IV/WoE method, binary-only scope + regression/multiclass alternatives, binning traps (zero-event smoothing, min event per bin, sparse/tie features, rare-event instability), monotonic supervised binning.
- `redundancy_and_lift.md` — Spearman vs Pearson, VIF / multivariate redundancy, filter→wrapper→embedded selection, incremental-lift measurement, multiple-testing caution.
- `leakage_and_tautology.md` — point-in-time correctness, embargo, late-arriving/restated data, label-proxy correlation test, causal-direction taxonomy.
- `stability_and_oot.md` — PSI computation and thresholds, IV-by-period, out-of-time validation protocol.
- `null_handling.md` — absence vs unknown, missingness flags, mode-dependent imputation, division-by-zero / inf guards.

### domains/
- `credit_scoring.md` — scorecard/WoE mode, monotonic binning, reason codes, fairness / protected-attribute proxy check, reject-inference note.
- `lead_scoring.md` — ranking framing, feature latency, SDR capacity & selection bias on contacted leads, label timing.
- `recsys_extension.md` — unsupported recommender-system roadmap covering prerequisites and known transfer limits.
