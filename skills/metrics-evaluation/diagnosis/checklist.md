# Diagnostic Checklist for Poor Model Performance

Steps are priority-ordered, not strictly serial — run cheap checks (Step 1 leakage flags, Step 4 distribution plots) in parallel while waiting on slower ones (Step 2 label lag, Step 3 feature audits). Each step can independently be the root cause — don't skip one just because an earlier one passed.

**Under time pressure (< 2 hours)**: do Step 1 in full, then a quick pass of Step 2
(label lag only) and Step 7's upper-bound sanity check. If baseline, support/uncertainty,
operating point, or economics remain unverified, the only allowed verdict is
`INSUFFICIENT EVIDENCE`; document Steps 3–6 as deferred.

## Step 1: Verify the Evaluation Setup

- [ ] Are train/val/test splits non-overlapping?
- [ ] Is splitting done by time (if temporal data) — not random?
- [ ] Does test prevalence represent the intended production population? Investigate legitimate temporal/population differences; equality with train is not required.
- [ ] Are there any features in the model that wouldn't exist at prediction time? (leakage)
- [ ] Was the metric computed correctly? (check: sklearn AP vs manual calculation)

**Red flag**: If metrics are suspiciously high on val but low on test → leakage or distribution shift.

---

## Step 2: Check Label Quality

- [ ] How were labels generated? (human annotation, heuristic, downstream event)
- [ ] What is the label lag? (e.g., fraud confirmed 30 days later — are test labels complete?)
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
- [ ] Are you optimizing the right objective? (log loss ≠ AP — use AP-optimized training if available)
- [ ] Is effective support sufficient to distinguish the required improvement? Use learning curves and confidence intervals.

---

## Step 6: Operating Point Mismatch

- [ ] Is the default threshold (0.5) used for precision/recall? (almost always wrong)
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

**Honest answer**: If the best feature has AUC 0.6 and the business needs AP 0.5, it may not be achievable. Say so.

(Time-pressure fast path is defined at the top of this file — Step 7's upper-bound question is part of it. Do not let unanswered Step 7 questions block the verdict otherwise — flag them as known unknowns instead.)
