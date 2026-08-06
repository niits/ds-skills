# Baseline and Comparator Policies

## Comparator Selection

Select a comparator by the artifact it emits and the information available at prediction
time. A task with binary labels may need a hard-decision comparator, a score-ranking
comparator, or both. Do not assign ranking metrics to hard labels unless an explicit score
representation is defined; do not assign hard-decision metrics to scores without a
threshold, capacity rule, or other decision policy.

The current policy, prior model, or deployable heuristic is usually the primary operational
comparator. Random and constant policies are no-skill references, not business bars.

## Hard Class or Label-Set Outputs

### Binary Classification

Let `p` be positive prevalence in the declared evaluation population.

**Always positive**
- Precision = `p`
- Recall = `1` when positives exist; otherwise use the frozen undefined-case convention.
- F1 = `2p / (1 + p)`

**Always negative**
- Accuracy = `1 - p`; this is informative only under stated symmetric costs and
  representative prevalence.
- Recall = `0` when positives exist; otherwise use the frozen undefined-case convention.
- This is the binary majority-class comparator only when the negative class has at least
  as much support as the positive class.

These hard decisions do not intrinsically define AP or AUC. If they are deliberately
represented as tied score levels, declare that representation and use the evaluator
contract in `topics/core/evaluator_semantics.md`.

### Multi-Class Classification

Let `p_c` be evaluation prevalence and `q_c` be a prior estimated only from information
available at prediction time, over `C` classes.

**Majority class:** predict `m = argmax_c q_c`. Evaluation accuracy is `p_m`; it equals
`max_c p_c` only when the prediction-time and evaluation majorities match. Using the
evaluation majority to construct the predictor is an oracle descriptive reference. Macro
recall is `1 / C` when every class is represented.

**Uniform random class:** sample each class with probability `1 / C`. Expected accuracy
= `1 / C`, expected per-class recall = `1 / C`, and population precision for class `c`
is `p_c`; finite samples use the frozen undefined-case convention.

**Prior-matched random class:** sample class `c` with probability `q_c`. Expected evaluation
accuracy is `sum_c p_c q_c`, reducing to `sum_c p_c^2` only when `q_c = p_c`. This is one
stochastic reference, not the uniquely correct no-skill comparator.

### Multi-Label Classification

Each instance carries a subset of `L` labels with evaluation prevalence `p_l`; estimate
prediction-time priors `q_l` without evaluation labels.

- **All negative:** predict no labels. Subset accuracy is the share of instances with an
  empty true label set; per-label recall is zero where positives exist.
- **Label-power-set majority:** predict the most frequent development-set combination.
  Subset accuracy is that chosen combination's evaluation frequency.
- **Independent prior-matched labels:** sample label `l` as present with probability
  `q_l`. This stochastic hard-label policy is distinct from emitting the constant
  probability score `q_l` for every instance.
- **Current assignment policy:** reproduce its per-label rules and volume when it is
  deployable on the evaluation population.

Undefined precision or F1 components, averaging, empty sets, and label omission are
evaluator choices; freeze them with `topics/core/evaluator_semantics.md`.

### Fixed-Budget Alerts

For point- or item-level anomaly triage, a budget-matched random policy selects the same
number of eligible alerts uniformly at random. Compare it with the current alert policy
under the same population, budget, and point/item definition. This hard-alert comparator
does not itself define AP or AUC.

## Scores and Ordered Candidate Lists

### Binary Score References

- **Constant score:** assign the same score to every eligible case. Its AP and AUC are
  determined by the frozen evaluator's tie and undefined-case conventions.
- **Random score/order:** assign label-independent continuous random scores or uniformly
  permute the fixed eligible cases. Population-level no-skill PR precision is prevalence.
  For a finite list, expected AP under uniform random ordering is not generally equal to
  prevalence and depends on support and the AP convention. Use exact enumeration when
  feasible or seeded permutations evaluated by the frozen evaluator.
- **Prior model or heuristic:** score the same eligible population with the previous model
  or deployable rule. This is usually the primary score comparator.

Evaluate constant and random scores with the AUC and tie contract in
`topics/core/evaluator_semantics.md`.

### Multi-Class and Multi-Label Scores

A constant per-class or per-label prior emits probabilities, not hard labels. Evaluate it
with probability metrics, or with classwise ranking metrics only after declaring the
one-vs-rest decomposition, evaluated labels, and averaging. If probabilities are converted
to hard outputs, define the argmax, threshold, abstention, or capacity rule separately.

### Ranked Candidate Lists

For NDCG, ranking MAP, MRR, or cutoff metrics, generate random references by independently
permuting each query's frozen eligible candidate set. Preserve candidates, relevance,
query weights, and the no-relevant-query policy. Report the seed, replicate count, Monte
Carlo mean, and simulation error when simulation is used.

Popularity is a candidate comparator only when historical frequency is available at
prediction time and represents a plausible simple policy. It is not a universal ranking
baseline and may be exposure-confounded. Prefer the current ranker or a task-specific
heuristic when popularity is irrelevant.

For ranker isolation, use identical per-query candidates. For end-to-end systems,
candidate generation may differ, but evaluate against a common query population,
eligibility universe, catalog snapshot, and relevance policy; report candidate recall
separately from conditional ranking quality.

### Anomaly Scores

With verified point/item labels, use the binary score references above and report the
positive rate. With no verified labels, empirical precision, recall, AP, and AUC are not
available; compare alert volume and score behavior with the current policy without
inventing outcome quality. Event detection requires an event evaluator rather than a
point-wise binary reduction.

Use deployable domain or seasonal rules as additional comparators when available; do not
assume a universal standard-deviation cutoff.

## Numeric Point Predictions

### Regression

- Fit `c = mean(y_train)` and evaluate it on the same test rows as the model. Using
  `mean(y_test)` is an oracle test-set comparator, not a deployable predictor.
- Compare `RMSE_model / RMSE_train_mean_baseline` on the same rows; interpretation lives
  in `topics/core/metric_interpretation.md`.

### Point Forecasting

- Naive comparator: predict the previous value.
- For seasonal period `m`, use the seasonal-naive forecast and scale MASE by the mean
  in-sample training error `mean(|y_t - y_{t-m}|)`.
- Use the MASE/RMSSE definitions and zero-denominator behavior in
  `topics/core/evaluator_semantics.md`.

## Quantiles, Intervals, and Predictive Distributions

- **Empirical residual:** form intervals from in-sample residual quantiles of a naive or
  seasonal-naive point forecast.
- **Climatological/unconditional:** use quantiles of the training target distribution while
  ignoring covariates.
- Do not use Gaussian intervals derived from in-sample RMSE unless normality and
  homoscedasticity have been checked.

These sections define forecast comparators. Pinball loss, CRPS, coverage, interval
boundaries, and horizon aggregation belong to `topics/core/evaluator_semantics.md`; their
meaning belongs to `topics/core/metric_interpretation.md`.
