---
name: feature-onboarding
description: End-to-end lifecycle for onboarding a new feature group into a supervised ML pipeline — from data-source understanding to production code. Primary focus on lead scoring and credit scoring (binary classification, ranking-oriented). Extensible to recommendation systems. Covers source semantics verification, behavior-based feature naming, IV/WoE predictive power, leakage and tautology checks (temporal point-in-time AND definitional), redundancy + incremental-lift selection, lag-horizon analysis, PSI/out-of-time stability, null-handling conventions, and a Go/No-Go gate with documented soft thresholds. Language-agnostic to project structure; examples in PySpark.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: ds-skills
    domain: lead scoring / credit scoring (extensible to recsys)
    primary-label-type: binary classification
---

# Feature Onboarding for Supervised ML

## Overview

A disciplined process for taking a **new feature group** from idea to production code, with gates that catch the failures that actually kill models in production: **leakage**, **tautology**, **redundancy**, and **distribution drift**.

This skill is opinionated toward **lead scoring** and **credit scoring** — binary labels, ranking-driven decisions, regulated or semi-regulated settings. It is structured so the same backbone extends to **recommendation systems** later (see `domains/recsys_extension.md`).

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
| Typical use | Credit scoring, regulated lending | Lead scoring, internal ranking, recsys |
| Binning | **Monotonic supervised binning required**; features enter as WoE | Optional; raw values fine, splits learned by trees |
| Null handling | Must impute (no native NaN) → bin nulls as own group or impute + flag | Leave NaN where genuinely unknown; trees split natively |
| Monotonicity | Enforced per feature (reason codes, regulator scrutiny) | Optional monotone constraints |
| Redundancy tolerance | Low — multicollinearity breaks coefficient interpretability | Higher — trees tolerate correlated inputs |
| Fairness / proxy check | **Mandatory** (protected-attribute proxies are a legal risk) | Strongly recommended |

`★` If you cannot answer "scorecard or GBM?" yet, default to **GBM mode** for exploration and re-binning later — but know that credit scoring almost always ends in scorecard mode, so design features that can be monotonically binned.

See `references/null_handling.md` and `domains/credit_scoring.md` for the consequences of each mode.

---

## The 12 Phases

Phases 1–8 are **analysis on validation data only** (no test/OOT leakage into decisions). Phases 9–12 are **engineering**.

### Phase 1 — Data Source Understanding
**Goal**: Understand the source table before computing anything.
1. Identify source table, schema, **granularity** (what does 1 row represent?).
2. **Verify column semantics with formula checks — never assume.** Write `col_a + col_b == col_c` on a sample; record confirmed formulas and decomposition trees.
3. Data range: time-dimension min/max, row count per period.
4. Coverage: what % of target entities appear in this table?
5. Null rates for key columns.
6. Mutual exclusivity (columns that never co-occur on a row).

**Output**: documented columns + confirmed formulas, data range, coverage stats.

### Phase 2 — Feature Hypothesis Formulation
**Goal**: Design and name features by **observable phenomenon**, not assumed business meaning — and **justify each one before computing it**.

**Required artifact — a one-line hypothesis per candidate feature** *(write this before Phase 3 touches any data)*:

> `feature_name` — *from* `<source column(s) / their verified semantics>` — *measures* `<subject behavior/state>` — *expected to relate to the label because* `<business / domain reasoning>`.

If you cannot complete that sentence, the feature is not ready to compute. This is the gate against brute-forced, speculative features that waste compute and inflate false discoveries. The hypothesis must be rooted in three things together:
1. **Source-data semantics** — the *verified* meaning of the columns (from Phase 1 formula checks), not their names.
2. **The business problem** — what decision the model drives (rank leads for SDRs? approve credit?) and what behavior actually moves that outcome.
3. **Domain/operational reality** — how the subject behaves and how the institution's processes generate the data (billing cycles, funnel stages, product mechanics).

Every feature must answer: *"What behavior or state does this measure from the subject's perspective?"* Group into:
- **Structure** (point-in-time snapshot at T): concentration index, share, per-unit intensity, count, ratio.
- **Temporal** (change over time): MoM pct_change, lag-N diff, volatility, streak.

**Name by formula/measurement, never by assumed meaning:**
- Good: `dep_share`, `per_acct_mom_pct`, `hhi`, `eom_to_peak_ratio`
- Bad: `loyalty_score`, `risk_indicator`, `salary_ratio`

**Design red flags** (see `references/leakage_and_tautology.md`):
- Measures an **internal institutional metric** rather than subject behavior (changes when *policy* changes, not when the *subject* changes).
- Is a **direct proxy for the label definition** (tautology).
- **Binary flag for a tiny population** → insufficient variance.
- **Assumes causation from correlation** (naming a peak inflow "salary" without evidence).

### Phase 3 — Prototype in Exploration Notebook
**Goal**: Compute features quickly and check signal exists.
- Dedicated exploration notebook, separate from pipeline code.
- Load label + target population (observation periods only); load raw data over observation **+ historical** periods (enough for lag computation).
- **Single read** of source → **single heavy aggregation** → **persist one intermediate** → derive multiple outputs from it (aggregates, concentration metrics, pivots, lags). Keep distributed; no driver materialization; no diagnostic counts in production-bound code. (See `spark-query-optimization` skill for the join-chain mechanics.)

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

1. **Redundancy** — use **Spearman** (rank), not just Pearson, so monotonic non-linear duplication is caught. Pairwise `|r|` is *not enough*: a new feature orthogonal to each existing feature individually can still be a linear combination of several. Add a **multivariate check** (VIF, or R² of regressing the new feature on the existing set). In **scorecard mode** redundancy tolerance is low; in **GBM mode** it is higher.

| `|r|` | Interpretation | Action |
|---|---|---|
| ≥ 0.7 | Highly redundant | Drop (unless materially higher IV than the existing one) |
| [0.5, 0.7) | Moderate overlap | Keep only if IV clearly higher |
| [0.3, 0.5) | Some correlation | Keep — incremental info |
| < 0.3 | Orthogonal | Keep |

2. **Incremental lift (wrapper/embedded)** — IV/correlation are *filters*. Before locking a feature, confirm it **improves the model**: add it to the baseline and measure Gini/AUC (scorecard) or AUC/PR + permutation/SHAP importance (GBM) on **validation**. A feature with weak univariate IV can earn its place via interactions; a feature with strong IV can add nothing if its information is already in the model.

**Empirical note**: rate-of-change features (MoM pct_change) are typically near-orthogonal to level features → keep both.

### Phase 6 — Leakage & Tautology
**Goal**: Confirm the feature is not cheating. Two distinct failure families (full detail in `references/leakage_and_tautology.md`):

**6a. Temporal / point-in-time leakage** — *the most common real-world leak.*
- Draw the timeline: `feature cutoff T → [embargo/gap g] → label window [T+g, T+g+h]`.
- Assert every input to the feature uses data **≤ T** — including **late-arriving / restated** rows that look like they belong to T but were written later.
- No post-outcome field may enter the snapshot.
- A feature can have `|r| < 0.3` with a label proxy and *still* leak by using future data.

**6b. Definitional tautology.**
1. **What defines the label?** (threshold on which metric? horizon?)
2. **Does the feature directly measure that metric?** If label = `X crosses threshold` and feature ≈ `ΔX` → tautological. A derived/adjusted variant of X → needs verification.
3. **Causal direction**: feature → label (predictive) OK; same root cause → both (co-symptoms) OK but weaker; feature ≈ label (same quantity) → **drop**.

**Verification**: correlate the suspect feature with a **direct proxy of the label metric**. `|r| > 0.8` → proxy, drop or document with extreme care. `< 0.3` → confirmed not tautological. `0.3–0.8` → investigate mechanical vs behavioral.

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
| Verdict | **PRIMARY** | Drop if collinear | **SUPPLEMENTARY** |

**Typical outcome**: keep shortest (primary) + longest feasible (different time perspective); drop intermediate lags (redundant with shortest). **Never** design lags longer than the source history supports → null-dominated features.

> **Mode note**: the IV-vs-horizon comparison here is the binary *screen* and applies to both modes. In **scorecard mode** the surviving lag features still enter the model as WoE-binned characteristics, not raw values.

### Phase 8 — Stability & Out-of-Time Validation — *do not skip*
**Goal**: Confirm the feature holds up over time, not just in one validation slice (detail in `references/stability_and_oot.md`).
1. **PSI** of each feature's distribution across periods — flag/drop if `PSI ≥ 0.25` (significant shift).
2. **IV by period**, not only pooled IV — a feature whose IV collapses in recent periods is dying.
3. **OOT confirmation**: after the feature set is provisionally locked, evaluate it once on an **out-of-time** window *after* train/validation. Report the Gini/AUC drop. High in-sample IV that does not survive OOT is a trap.

### Phase 9 — Final Feature Selection
**Drop if ANY**:
- IV < 0.02 **and** no interaction value **and** no incremental lift.
- `|r| > 0.7` with an existing feature of equal/higher IV (multivariate-confirmed).
- Tautological (`|r| > 0.8` vs label proxy) or temporally leaky.
- Measures institutional perspective only.
- Binary flag for population < 5%.
- `PSI ≥ 0.25` or IV collapses out-of-time.

**Keep priority** (high→low):
1. Strong IV (≥ 0.3) + orthogonal + adds lift.
2. Medium IV ([0.1, 0.3)) + orthogonal + adds lift.
3. Weak IV ([0.02, 0.1)) + highly orthogonal + measurable lift (new information despite weak univariate IV).
4. Medium IV + moderate correlation (0.3–0.5) but interpretably distinct.

> **Mode note**: this priority is stated in IV terms (the binary screen). In **scorecard mode**, also require the feature to bin monotonically and pass the fairness/reason-code filters from `domains/credit_scoring.md`; in **GBM mode**, prefer the incremental-lift/permutation-importance evidence from Phase 5 over raw IV.

**Null handling** is mode-dependent — see `references/null_handling.md`. Summary: absence-based → fill 0 **plus a missingness flag** (don't conflate "structurally absent" with "unknown"); ratio/share → leave NaN (GBM) or bin-as-group (scorecard); lag pct_change → NaN (genuinely unknown); lag absolute diff → fill 0 (no prior = no change).

### Phase 10 — Module Implementation
**Function contract**: input = entity population, time range, optional lookback; output = `[entity_id, time_period, ...feature_cols]`; deterministic; handles partial history and null source.

**Computation**: single read (filter time + population early) → persist the heaviest intermediate **only when it fans out to ≥ 2 downstream branches/actions** (a single linear pass should not cache — it just adds serialization/spill overhead) → derive all outputs from it → one window definition computes all lags in one pass. Prefer `MEMORY_AND_DISK`. No side effects (no writes, counts, or driver materialization).

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

**Reproducibility**: deterministic given the same inputs means **deterministic window
ordering** (Spark ordering is nondeterministic without an explicit `orderBy` tiebreaker
in each window), fixed seeds for any sampling/CV, and recording the **data + code
version** with each snapshot (Delta table version / `TIMESTAMP AS OF`, plus the code
git SHA or a transform hash) so a feature set can be regenerated byte-for-byte.

**Verify** (one-time integration check / data-quality layer — *not* counts inside the
compute function): schema = `[entity_id, time_period]` + declared cols; row count ≈
`target_population × observation_periods`; null rates within documented bounds; no
inf / division-by-zero artifacts; value distributions sane (min/max/median).

### Phase 12 — Cleanup
Move exploration notebook to an experiments dir; strip diagnostic cells from the production notebook (keep compute + persist); fix moved relative paths; write a clear commit documenting what was added and from what source.

---

## Go / No-Go Gate

Before Phase 10 (implementation), **all** gates must PASS:

| Gate | Criterion |
|---|---|
| Data OK | Coverage adequate for the feature's intent (a sparse-but-strong feature is fine **with a missingness flag**); null < 20% for key features |
| Predictive | ≥ 3 features with IV > 0.05 (deliberate mid-weak-band screening floor, between the 0.02 "drop" and 0.1 "medium" lines; **IV assumes a binary label** — for regression/multiclass use the alternatives in `references/predictive_power.md`) |
| Adds lift | Feature set measurably improves the model on validation (not just univariate IV) |
| Not redundant | Majority `|r| < 0.5` vs existing, **multivariate-confirmed** (VIF / R²) |
| Temporally safe | Every feature uses data ≤ cutoff; embargo between cutoff and label window; no late-arriving leakage |
| Not tautological | No feature `|r| > 0.8` vs label proxy |
| Stable | `PSI < 0.25` across periods; IV does not collapse out-of-time |
| Motivated | Every feature has a written hypothesis grounding it in source semantics + business + domain; none were generated mechanically |
| Conceptual | Measures subject behavior, not internal metric |
| Lag feasible | Source range supports chosen lags with acceptable coverage |
| Mode-consistent | Binning, null handling, monotonicity, fairness all match the chosen Model Mode |

`★` The original "Coverage ≥ 80%" hard gate was **softened on purpose**: coverage and predictive power interact. A feature covering 40% of entities with strong signal on that 40% is valuable *if* you add an explicit missingness indicator. Don't discard it on a blanket coverage rule.

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
6. **Keep all lag horizons** — intermediate lags are usually redundant with the shortest.
7. **Name by assumed meaning** — name by what you measure.
8. **Include institutional-perspective features** — profitability/strategy metrics measure the *institution's* decisions, not subject intent.
9. **Ignore data availability** — long lags on short history = null-dominated features.
10. **Conflate "absent" with "unknown"** in null fill — fill 0 *and* add a missingness flag.
11. **Materialize to driver during computation** — keep distributed until final viz/fit.
12. **Multiple reads of the same source** — persist one intermediate, derive many outputs.
13. **Validate selection on test/OOT** — all engineering decisions use **validation only**; the test/OOT slice confirms the *locked* set once.
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
- `recsys_extension.md` — extending the backbone to recommenders: user/item/context features, per-interaction point-in-time, implicit-feedback leakage, popularity/position bias.
