# Experimental Design Patterns — Banking Domain

## Testing Hypotheses in Banking DS

Banking DS experiments operate under constraints not present in academic research:
- **Regulatory oversight:** Model changes require documented validation and approval
- **Production risk:** A bad champion-challenger experiment can affect thousands of customers
- **Long outcome windows:** Credit default outcomes may take 12–24 months to observe
- **Selection bias:** We only observe outcomes for approved applicants (reject inference problem)
- **Ethical / fair lending:** Experiments cannot discriminate on protected characteristics

Choose the design that answers the question with the least production risk and fastest time-to-signal.

---

## Design Selection Framework

| Question type | Recommended design | Time to result |
|---|---|---|
| Would a new feature improve model? | Offline ablation / holdout test | Hours–days |
| Is model degradation due to population shift? | Vintage segmentation analysis | Hours–days |
| Is a data quality issue causing performance degradation? | Feature audit + imputation analysis | Hours–days |
| Would a new model outperform the current champion in production? | Champion-challenger (shadow then live) | Weeks–months |
| Would a policy change (cutoff, credit limit) affect default rate? | A/B test or quasi-experimental | Weeks–months |
| What is the causal effect of a past policy change? | Diff-in-diff or regression discontinuity | Days (retrospective) |
| How would the model perform under a stress scenario? | Simulation / stress test | Hours–days |

---

## Pattern 1: Offline Ablation / Holdout Experiment

**Use when:** Testing whether adding, removing, or changing a feature affects model performance, without changing production.

**Design:**
- Use a pre-existing holdout set (held out before training, never seen by the model)
- Train two versions: baseline model and modified model (different features or architecture)
- Evaluate on the same holdout set
- Compare primary metric (KS, AP, AUC) and secondary metrics (PSI stability, calibration)

**Key controls:**
- Holdout must be drawn from the same period and population as the training set
- Use time-based split (train on earlier vintages, hold out on recent) — not random split
- Report metric with confidence interval (bootstrap or DeLong test for AUC)

**Decision rule:** State before running: "If KS improvement ≥ 3 points and PSI < 0.10, proceed to champion-challenger."

**Banking example:**
```
Hypothesis: Adding CB_UTILIZATION_3M increases KS on revolving credit model.
Train: Jan 2022 – Dec 2023 originations (12-month outcome window)
Holdout: Jan 2024 – Jun 2024 originations (6-month early delinquency proxy)
Baseline: 28 features, KS = 0.38
Modified: +CB_UTILIZATION_3M, all else equal
Decision threshold: KS improvement ≥ 0.03 on holdout → proceed to C/C
```

**Pitfalls:**
- Random train/test split on time-series credit data → information leakage from future → inflated metrics
- Testing on the same data used to select features → overfit evaluation
- Not checking if holdout population matches production (PSI between holdout and recent originations)

---

## Pattern 2: Backtesting / Walk-Forward Validation

**Use when:** Evaluating model or feature stability across time, or testing whether a methodology would have performed well historically.

**Design (walk-forward):**
- Define a series of expanding or rolling training windows
- For each window: train model, evaluate on the next N-month window
- Summarize metric stability (mean, std dev, min across windows)

**When to use rolling vs. expanding window:**
- **Expanding (cumulative) window:** Default for credit models — more data = better PD estimation; use unless population is clearly non-stationary
- **Rolling window (fixed size):** Use when recent data is more relevant (behavioral models, fraud, AML) or when population shift is confirmed

**Key metrics to track across windows:**
- KS / AUC on each test window
- PSI between training and test populations
- Calibration drift (predicted PD vs. observed default rate)

**Banking example:**
```
Hypothesis: Using 6-month behavioral window is more stable than 12-month for card revolvers.
Design: Walk-forward, quarterly steps, Jan 2020 – Dec 2023
Model A (12-month): Train window 24 months rolling, test next quarter
Model B (6-month): Train window 12 months rolling, test next quarter
Compare: KS std dev across quarters, PSI mean, calibration RMSE
Decision: If Model B KS std dev < Model A std dev by ≥0.02, proceed to champion-challenger
```

**Pitfalls:**
- Too short a test window → insufficient defaults observed → noisy metrics
- Backtesting during atypical periods (COVID window) without flagging it as an anomaly
- Not accounting for reject inference → backtest performance overstates production performance

---

## Pattern 3: Champion-Challenger (Shadow Mode → Live Split)

**Use when:** Validated offline improvement exists and production validation is required before full deployment.

**Two-stage approach:**

**Stage 1 — Shadow mode:**
- New model scores all applicants but decisions are made by champion only
- No customer impact; pure observation
- Run for 1–2 months to confirm score distribution, PSI, and rank-ordering
- Decision gate: if shadow PSI < 0.10 and KS difference from offline test holds, proceed to Stage 2

**Stage 2 — Live traffic split:**
- Random sample (typically 5–20%) assigned to challenger model for live decisions
- Remaining traffic continues under champion
- Monitor: approval rate, score distribution, early delinquency (30+ DPD at 3 months)
- Full performance evaluation after minimum observation window (6–12 months for credit)

**Key controls:**
- Randomization must be at customer level, not product or time level (to avoid confounds)
- Document randomization seed and assignment logic — required for model validation
- Run statistical power calculation before launch: what sample size needed to detect target KS improvement?
- Define stopping criteria: if early delinquency in challenger cohort exceeds champion by X%, revert immediately

**Regulatory requirements (Vietnam):**
- Champion-challenger changes to NHNN-supervised models require documentation of methodology change and business rationale
- Credit scoring model changes at commercial banks typically require internal credit committee approval before live split
- Retain full audit trail: who approved, what date, what criteria were used

**Banking example:**
```
Hypothesis: New fraud model (v2) reduces false positive rate by 15% at same recall.
Stage 1 (Shadow, 6 weeks): Score all fraud candidates with v2; decisions by v1
  Gate: v2 PSI vs v1 < 0.10; rank-order correlation > 0.95
Stage 2 (10% live split, 12 weeks): Challenger = v2, Champion = v1
  Primary metric: FPR@95% recall
  Secondary: Customer complaint rate, manual review queue size
  Decision threshold: FPR reduction ≥ 12% with p < 0.05 → full champion swap
```

---

## Pattern 4: A/B Test (Policy / Product Experiment)

**Use when:** Testing the causal effect of a policy change, pricing decision, credit limit, or product feature — not a model change.

**Design:**
- Random assignment of customers/applicants to treatment (A) and control (B) groups
- Treatment receives new policy; control receives existing policy
- Primary metric must be defined before launch (pre-registration)
- Run for a fixed duration agreed upfront (avoid peeking)

**Sample size calculation (required before launch):**
```
n = 2 × (z_α/2 + z_β)² × σ² / δ²
where:
  δ = minimum detectable effect (e.g., 0.5pp reduction in default rate)
  σ = estimated standard deviation of outcome
  z_α/2 = 1.96 for α=0.05 two-tailed
  z_β = 0.84 for 80% power
```

**Banking-specific A/B test examples:**

| Experiment | Treatment | Control | Primary metric |
|---|---|---|---|
| Credit limit increase for mid-risk segment | Limit +20% | No change | 12-month default rate |
| New collections messaging (SMS vs call) | SMS-first contact | Phone-first contact | Cure rate at 30 DPD |
| Lower interest rate offer to reduce churn | Rate -1.5% | Standard rate | 6-month retention rate |
| New application form (fewer fields) | Short form | Standard form | Completion rate + approval rate |

**Key controls:**
- Randomize at the correct unit of analysis (customer-level for credit limit; account-level for collections; session-level for digital)
- Check for spillover effects (treatment customer referring control customer to same product)
- Monitor for Novelty effect (short-term behavioral change that reverts)

**Pitfalls:**
- Running the test too short → underpowered → false negatives
- Peeking at results before agreed end date → inflated false positive rate (use sequential testing if early stopping is needed)
- Not defining primary metric before launch → HIPPO overrides results with post-hoc secondary metric

---

## Pattern 5: Difference-in-Differences (Policy Change Causal Analysis)

**Use when:** A policy was already implemented (no random assignment was possible) and you need to estimate its causal effect retrospectively.

**Design:**
- Identify treatment group (affected by policy) and control group (not affected)
- Measure outcome before and after the policy change for both groups
- Effect = (treatment_after − treatment_before) − (control_after − control_before)
- Key assumption: parallel trends (treatment and control would have moved similarly absent the policy)

**Parallel trends check:** Plot outcome trends for both groups for at least 4 periods before the policy. If trends diverge before treatment, DiD is invalid.

**Banking examples:**

| Context | Treatment group | Control group | Policy |
|---|---|---|---|
| NHNN rate cap implementation | Products with rate > cap | Products below cap | Rate ceiling circular |
| Branch closure effect on churn | Customers served by closed branch | Customers at open branches | Branch network restructuring |
| New credit underwriting policy | Products under new policy | Products on old policy (grandfathered) | Policy rollout by product line |
| Collections strategy change | Accounts assigned to new team | Accounts on existing team | Pilot rollout by geography |

**What DiD cannot answer:** If the treatment and control groups experienced different macro shocks (e.g., one region hit by natural disaster, another not), the parallel trends assumption breaks and DiD results are unreliable.

---

## Pattern 6: Regression Discontinuity (Score Cutoff Analysis)

**Use when:** A score cutoff determines treatment (approved vs. declined) and you want to estimate the causal effect of approval, or understand what happens just above vs. just below the cutoff.

**Design:**
- Identify the cutoff score
- Compare outcomes for applicants just above (approved) vs. just below (declined)
- The comparison is valid only in a narrow bandwidth around the cutoff
- Use local linear regression on both sides of the cutoff

**Banking applications:**
- Estimate true default rate for marginally approved borrowers (just above cutoff)
- Evaluate whether the current cutoff is optimal (profit maximization)
- Detect model manipulation (spike in applications just above cutoff → applicant gaming the process)
- Estimate the "reject inference" correction for borderline applicants

**Bandwidth selection:** Use Imbens-Kalyanaraman optimal bandwidth or cross-validation. Too narrow → noisy; too wide → includes applicants far from cutoff where RDD is no longer valid.

**Limitation:** RDD estimates the local average treatment effect (LATE) — only valid for applicants near the cutoff. Cannot generalize to the full population.

---

## Pattern 7: Propensity Score Matching (Observational Causal Analysis)

**Use when:** No randomization was possible and groups differ on many confounders, but you need a causal estimate from observational data.

**Design:**
- Estimate propensity score: P(treatment | covariates) using logistic regression or tree model
- Match treated units to control units with similar propensity score
- Compare outcomes on matched sample
- Check covariate balance after matching (standardized mean differences < 0.1)

**Banking applications:**
- Estimate effect of debt restructuring on long-run default probability
- Compare outcome of customers who voluntarily closed accounts vs. those retained
- Evaluate effect of credit counseling program on delinquency rates

**Pitfalls:**
- Unmeasured confounders (hidden bias) — PSM removes observed confounding only; run sensitivity analysis (Rosenbaum bounds)
- Poor overlap (common support) — if treated and control populations are very different, no good matches exist; report this clearly

---

## Pattern 8: Vintage Segmentation Analysis

**Use when:** Investigating model performance degradation or PSI spikes across origination cohorts.

**Design:**
- Group originations by month or quarter of origination (vintage)
- Compute model metrics (KS, AUC, calibration) separately per vintage
- Plot metrics over vintage time axis
- Look for: when did degradation start? Which vintages are affected? Is it gradual or step-change?

**What the pattern reveals:**

| Pattern | Likely cause |
|---|---|
| Gradual degradation over 6–12 months | Population drift, macro environment change |
| Step-change at specific vintage (e.g., Oct 2024) | Policy change, new channel launch, data source change |
| Degradation in one segment only | Segment-specific event (product launch, channel mix change) |
| Degradation in recent vintages, stable in older | Model trained on older patterns, concept drift |
| Stable KS but degraded calibration | Model rank-order still valid but predicted PDs are miscalibrated |

**Key output:** Vintage heatmap (x-axis: origination month; y-axis: performance window month; cell value: KS or 30+ DPD rate). This is the single most informative diagnostic for credit model performance.

---

## Pattern 9: Monte Carlo Simulation / Stress Test

**Use when:** Testing how model outputs or business metrics behave under hypothetical adverse scenarios.

**Design:**
- Define stress scenarios (e.g., unemployment +5pp, GDP -3%, rate +200bps)
- Apply scenario to input feature distributions
- Run model with stressed inputs
- Compute output distribution (PD, expected loss, approval rate)

**Banking applications:**
- IFRS 9 ECL calculation under base/adverse/downturn scenarios
- Credit limit stress test (what happens to portfolio EL if income drops 20%?)
- Model sensitivity to feature shocks (how much does PD change per 1pp income drop?)

**Key output:** Sensitivity table (feature name, stress magnitude, PD change, EL change). This feeds directly into model risk assessment sections of validation reports.

---

## Design Trade-off Summary

| Design | Internal data only | Causality | Speed | Production risk | Regulatory complexity |
|---|---|---|---|---|---|
| Offline ablation | ✓ | Correlation only | Fast | None | Low |
| Backtesting | ✓ | Correlation only | Fast | None | Low |
| Champion-challenger | ✓ | Quasi-causal | Slow | Medium | High |
| A/B test | ✓ | Causal | Medium | Medium | High |
| Diff-in-Diff | ✓ | Quasi-causal | Medium | None | Medium |
| Regression discontinuity | ✓ | Causal (local) | Medium | None | Medium |
| Propensity matching | ✓ | Quasi-causal | Medium | None | Low |
| Vintage segmentation | ✓ | Descriptive | Fast | None | Low |
| Monte Carlo | ✓ | Hypothetical | Fast | None | Medium |

**Default progression:** Offline ablation → Backtesting → Shadow mode → Champion-challenger. Each stage gates the next. Do not skip stages.
