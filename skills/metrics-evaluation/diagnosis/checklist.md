# Diagnostic Checklist for Poor Model Performance

Run in this order. Each step can be the root cause — don't skip ahead.

## Step 1: Verify the Evaluation Setup

- [ ] Are train/val/test splits non-overlapping?
- [ ] Is splitting done by time (if temporal data) — not random?
- [ ] Is the positive rate in test set the same as expected in production?
- [ ] Are there any features in the model that wouldn't exist at prediction time? (leakage)
- [ ] Was the metric computed correctly? (check: sklearn AP vs manual calculation)

**Red flag**: If metrics are suspiciously high on val but low on test → leakage or distribution shift.

---

## Step 2: Check Label Quality

- [ ] How were labels generated? (human annotation, heuristic, downstream event)
- [ ] What is the label lag? (e.g., fraud confirmed 30 days later — are test labels complete?)
- [ ] What fraction of positives might be mislabeled?
- [ ] Are there systematic labeling errors in certain segments?

**Rule**: Label noise of 20% can cut AP in half. Fix labels before tuning models.

---

## Step 3: Assess Feature Quality

- [ ] Check univariate AUC of each feature against target
- [ ] Are any features strongly correlated with target? (If not, the signal may not exist)
- [ ] Are features available at prediction time in production?
- [ ] Are features computed correctly (no future leakage in aggregations)?
- [ ] Is there a feature with AUC > 0.7 alone? If yes, start with that feature only.

**Diagnostic**: Train a single-feature logistic regression per feature. If no single feature has AUC > 0.6, the problem is feature quality, not model.

---

## Step 4: Check for Distribution Shift

- [ ] Plot feature distributions: train vs test. Are they similar?
- [ ] Check positive rate: train vs test. Should be close.
- [ ] If temporal split: check if event rate changed over time
- [ ] Run model on train set — is AP on train >> AP on test? (overfitting)
- [ ] Run model on test set by time slice — does performance degrade over time?

**Red flag**: AP drops > 50% from train to test → overfitting or distribution shift.

---

## Step 5: Model Capacity and Training

- [ ] Is the model underfitting? (Try: LightGBM if using logistic regression, deeper tree depth)
- [ ] Is class imbalance handled? (Try: scale_pos_weight, class_weight='balanced', oversampling)
- [ ] Was hyperparameter tuning done on validation set? (not test set)
- [ ] Are you optimizing the right objective? (log loss ≠ AP — use AP-optimized training if available)
- [ ] Enough training data? Positives < 1000 → model will struggle regardless

---

## Step 6: Operating Point Mismatch

- [ ] Is the default threshold (0.5) used for precision/recall? (almost always wrong)
- [ ] Is the threshold calibrated on validation set to match business operating point?
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

**Under time pressure (< 2 hours to verdict)**: Answer only the first two questions. Document the rest as "deferred — requires investigation before production decision." Do not let unanswered Step 7 questions block the verdict — flag them as known unknowns instead.
