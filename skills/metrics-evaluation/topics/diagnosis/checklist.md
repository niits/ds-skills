# Diagnostic Checklist for Poor Model Performance

Steps are priority-ordered, not strictly serial — run cheap checks (Step 1 leakage flags, Step 4 distribution plots) in parallel while waiting on slower ones (Step 2 label lag, Step 3 feature audits). Each step can independently be the root cause — don't skip one just because an earlier one passed.

**Under time pressure (< 2 hours)**: do Step 1 in full, then a quick pass of Step 2
(label lag only) and Step 7's upper-bound sanity check. If baseline, support/uncertainty,
or operating point remain unverified, the only allowed conclusion is
`INSUFFICIENT EVIDENCE`. Economics is additionally required only for an economic,
operating-value, or controlled-test conclusion. Document Steps 3-6 as deferred.

## Step 1: Verify the Evaluation Setup

- [ ] Are train/val/test splits non-overlapping?
- [ ] Does the split represent deployment: future time, new entity, new scene/location,
  or exchangeable cases? Point-in-time validity is required regardless of split type.
- [ ] Does test prevalence represent the intended production population? Investigate legitimate temporal/population differences; equality with train is not required.
- [ ] Are there any features in the model that wouldn't exist at prediction time? (leakage)
- [ ] Was the metric reproduced under the frozen evaluator contract, including output
  representation, ties, interpolation, undefined cases, and candidate sets?

**Red flag**: If metrics are suspiciously high on val but low on test → leakage or distribution shift.

---

## Step 2: Check Label Quality

- [ ] How were labels generated? (human annotation, heuristic, downstream event)
- [ ] What is the label lag? (e.g., conversion or service resolution confirmed later — are test labels complete?)
- [ ] What fraction of positives might be mislabeled?
- [ ] Are there systematic labeling errors in certain segments?

**Heuristic signal**: label noise can materially distort AP, with magnitude and direction
depending on the noise process. Audit labels before tuning models.

---

## Step 3: Assess Feature Quality

- [ ] Check univariate AUC of each feature against target
- [ ] Do train-fitted multivariate baselines and ablations show reproducible held-out signal?
- [ ] Are features available at prediction time in production?
- [ ] Are features computed correctly (no future leakage in aggregations)?
- [ ] Are apparently strong univariate features temporally available and non-leaky?

**Diagnostic aid**: univariate models describe marginal signal only. Interactions can be
valuable with weak univariate AUC; use a regularized multivariate baseline and ablation
before concluding that feature signal is absent.

---

## Step 4: Check for Distribution Shift

- [ ] Plot feature distributions: train vs test. Are they similar?
- [ ] Compare train and test positive rates; investigate differences and verify test prevalence represents the intended deployment population.
- [ ] If temporal split: check if event rate changed over time
- [ ] Run model on train set — is AP on train >> AP on test? (overfitting)
- [ ] Run model on test set by time slice — does performance degrade over time?

**Red flag**: a train-to-test drop beyond dependence-aware uncertainty triggers separate
overfitting, temporal/population shift, and evaluation-contamination checks.

---

## Step 5: Model Capacity and Training

- [ ] Is the model underfitting? Compare appropriately regularized alternatives under the same validation protocol.
- [ ] Does any class weighting or resampling preserve the intended estimand and probability calibration?
- [ ] Was hyperparameter tuning done on validation set? (not test set)
- [ ] Does the training objective align with the evaluated estimand and operating region?
- [ ] Is effective support sufficient to distinguish the required improvement? Use learning curves and confidence intervals.

---

## Step 6: Operating Point Mismatch

- [ ] Is the threshold justified by calibrated costs, constraints, or a declared policy,
  rather than accepted as a default?
- [ ] Is the threshold selected on validation data to match cost/capacity constraints?
- [ ] Is the metric reported (AP) actually what the business optimizes?
- [ ] Could precision@top-k be more relevant than AP?

---

## Step 7: Fundamental Problem Difficulty

Sometimes the metric is low because the task is hard, not because the model is bad.

- [ ] Is there a theoretical upper bound? (e.g., human performance, oracle features)
- [ ] Is the positive class actually predictable from the available features?
- [ ] Have other teams/papers solved this problem? What did they achieve?
- [ ] Is the business requirement (e.g., AP > 0.6) actually achievable on this data?

Do not infer an upper performance bound from one feature's AUC. Use learning curves,
oracle inputs, human agreement, external evidence, or other defensible bounds, and mark
achievability unresolved when they are unavailable.

(Time-pressure fast path is defined at the top of this file — Step 7's upper-bound question is part of it. Do not let unanswered Step 7 questions block the verdict otherwise — flag them as known unknowns instead.)

---

## Representation and Retrieval Audit

- [ ] Are candidate set, gallery construction, and normalization identical across compared runs?
- [ ] Are near duplicates and shared identities kept in the intended split?
- [ ] Are intervals clustered at identity, session, or query-group level rather than per pair or per trial?
- [ ] Is the backbone truly frozen when a frozen probe is claimed, with equal search budgets across encoders?
- [ ] Does model ordering survive multiple seeds and at least one complementary task or protocol?

## Anomaly Evaluation Audit

- [ ] Are score ranking, hard point alerts, and event detection reported separately?
- [ ] Is point adjustment absent or explicitly declared and isolated from point-wise and
  event-wise comparisons?

---

## Multi-Class and Multi-Label Audit

- [ ] Is the averaging scheme stated for every reported precision, recall, and F1?
- [ ] Is per-class or per-label support reported next to any macro figure?
- [ ] Are compared models reported under the same averaging scheme?
- [ ] Is the zero-division convention declared for classes that receive no predictions?
- [ ] Multi-label: are thresholds per label, and is label correlation respected in resampling?
- [ ] Is the majority-class baseline computed as the majority class share, not `1 - positive_rate`?

---

## Probabilistic Forecasting Audit

- [ ] Are the evaluated quantile levels and their averaging stated?
- [ ] Is interval coverage reported together with interval width?
- [ ] Is coverage broken out by horizon rather than aggregated?
- [ ] Does the coverage figure carry its own uncertainty at the independent unit?
- [ ] Is a deployable baseline interval scored on the same rows?
