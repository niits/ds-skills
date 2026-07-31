# Multi-Metric Pattern Diagnosis

## How to Use This File

When you have results from multiple metrics, match them against the patterns below.
Each pattern specifies:
- **Signal**: what you observe (qualitative relationship between metrics)
- **Diagnosis**: what the combination reveals
- **Root causes**: ordered by likelihood — check top ones first
- **Actions**: specific steps to take next

Patterns are grouped by the primary symptom observed.

---

## Group 1: AUC-ROC and AP Diverge

### Pattern 1.1 — AUC-ROC high, AP modest relative to prevalence
```
AUC-ROC materially exceeds its baseline
AP lift and top-of-list precision miss the operating requirement
```
**Diagnosis hypothesis**: AUC is the probability that a random positive outranks a
random negative across the full score range. AP depends on prevalence and top-ranked
false discoveries. Inspect prevalence, score distributions, partial ROC, and the PR
operating region before assigning a cause.

**Root causes** (check in order):
1. Wrong primary metric — AUC-ROC is not appropriate when positive-class ranking is what matters
2. Poor positive-negative separation in the decision-critical ranking region; assess calibration separately
3. Evaluation set too small on the positive side — AP estimate is noisy

**Actions**:
- Switch primary metric to AP / AUC-PR for all further evaluation
- Plot the PR curve: if precision collapses immediately at low recall, the model has no useful signal at any practical operating point
- Count true positives in top `k` versus random expectation (`positive_rate × k`) — is the model concentrating positives at the top?

---

### Pattern 1.2 — AUC-ROC modest, AP useful at the operating region
```
AUC-ROC is modest
AP / positive_rate shows reproducible lift
```
**Diagnosis hypothesis**: the model may still be useful for a selective top-k policy.
The metric pair does not identify a "negative-side" failure.

**Actions**:
- Focus on PR curve, not ROC — the model may be usable at a selective operating point
- Inspect score distributions and decision-critical segments at the intended operating point

---

## Group 2: Train vs. Eval vs. Production Diverge

### Pattern 2.1 — Train AP >> Val AP >> Test AP (monotonically degrading)
```
AP_train = 0.60
AP_val   = 0.35
AP_test  = 0.18
```
**Diagnosis hypothesis**: train-to-validation gaps support overfitting; later-test decline
also requires explicit temporal, population, and label-shift checks.

**Root causes**:
1. Model too complex relative to training data size (especially positives)
2. No regularization or insufficient regularization
3. Hyperparameters tuned on test set (leakage of test information into model selection)

**Actions**:
- Reduce model complexity: fewer trees, higher min_child_weight, lower max_depth
- Perform model selection/CV within training/development data; preserve a final untouched test set
- Use learning curves and clustered/temporal uncertainty to assess effective support

---

### Pattern 2.2 — Train AP ≈ Val AP >> Test AP (cliff at test)
```
AP_train = 0.45
AP_val   = 0.42
AP_test  = 0.15
```
**Diagnosis hypothesis**: distribution shift is plausible, but validation contamination,
test noise, label maturation, and protocol differences can produce the same cliff.

**Root causes**:
1. Time-based split not used — random split leaks future into training
2. Test set covers a different time period, segment, or population
3. Label definition changed between periods

**Actions**:
- Confirm split method: must be time-ordered if data is temporal
- Plot feature distributions and calibrate drift alerts from stable historical periods,
  sample size, multiplicity, and business loss; no fixed JS value proves harmful shift
- Check positive rate: train vs test. If different → population shift, not just model issue
- Re-train with a time-based split and re-evaluate

---

### Pattern 2.3 — Val AP good, A/B test shows no improvement
```
AP_val = 0.40 (strong, 15x lift)
A/B CTR lift = 0% (not significant)
```
**Diagnosis hypothesis**: compare the online effect estimate and confidence interval
with the minimum practical effect. A non-significant result may be underpowered rather
than evidence of zero effect.

**Root causes** (in recommendation/ranking context):
1. **Feedback loop bias**: training data reflects historical policy, not ground truth preferences
2. **Position bias not corrected**: model trained on click data where top items get more clicks regardless of quality
3. **Metric mismatch**: optimizing NDCG but business cares about revenue, dwell time, or session depth
4. **Exploration deficit**: model recommends safe/popular items, users see no novelty, don't engage differently

**Actions**:
- Investigate the training data: are positive labels (clicks) from a biased exposure policy?
- Try debiasing: inverse propensity scoring or use unbiased data from a randomized experiment
- Check: does the model improve on the items the A/B treatment group sees, or only on historical items?
- Change the offline metric to match what the A/B test measures (e.g., revenue@k instead of NDCG@k)

---

## Group 3: Precision and Recall Are Both Low

### Pattern 3.1 — No threshold provides an acceptable precision-recall trade-off
```
At threshold T1 (high): Precision = 0.60, Recall = 0.05
At threshold T2 (low): Precision = 0.04, Recall = 0.80
AP = 0.08 (barely above baseline of 0.022)
```
**Diagnosis hypothesis**: no acceptable operating point has been demonstrated for the
stated business requirement. The example can still serve a selective policy; stronger
conclusions require economics and paired uncertainty.

**Root causes**:
1. Features have very low correlation with target — check univariate feature AUCs
2. Label noise is high — actual positives look like negatives in feature space
3. Model undertrained or wrong objective (e.g., using accuracy loss on imbalanced data)
4. Fundamental problem difficulty: the positive class may not be predictable from available features

**Actions**:
- Compare regularized multivariate baselines and ablations under nested/chronological validation.
- Review label definition: are "positives" actually meaningfully different from negatives in feature space?
- Use learning curves, permutation tests, or confidence intervals to determine whether
  held-out lift is distinguishable from noise; visualization is not a performance bound.

---

### Pattern 3.2 — Precision very high, recall very low (operating point issue)
```
Precision@threshold = 0.85
Recall@threshold = 0.04
AP = 0.35 (adequate lift)
```
**Diagnosis hypothesis**: this may be an intentional selective operating point or a
cost/capacity mismatch; high precision and low recall alone is not a defect.

**Root causes**:
1. Default threshold (0.5) used — wrong for imbalanced data
2. Probability magnitudes are used in decisions and reliability diagnostics show miscalibration
3. Business chose threshold to maximize precision without checking business impact of missed positives

**Actions**:
- Plot the PR curve and identify the operating point that meets business requirements
- If probability values drive decisions, assess reliability, calibration intercept/slope,
  and Brier score on untouched data; calibration does not improve ranking
- Compute FN cost at current recall=0.04 — likely unacceptable

---

## Group 4: Good Metrics, Bad Business Outcome

### Pattern 4.1 — AP strong, business KPI not met
```
AP = 0.45 (20x lift over 2.2% baseline)
But: expected precision@review_capacity < break-even precision
```
**Diagnosis**: Model has real signal, but at the volume the business can act on (review capacity), the precision is still below break-even.

**Root causes**:
1. No feasible operating volume produces positive incremental value under the current cost/effect assumptions
2. Break-even precision is too high (intervention cost > value saved)
3. Model needs to be more selective — optimize Precision@k directly, not AP

**Actions**:
- Re-compute incremental economics using an identified action effect or explicit scenario bounds
- Simulate: at current model, what is precision at exactly the review capacity? Is it above break-even?
- If not: either increase capacity, reduce cost per action, or improve model Precision@k specifically
- Consider: is AP the right training objective? If business needs precision@200, optimize that directly.

---

### Pattern 4.2 — All metrics improving each sprint, but production degrading
```
AP val: 0.28 → 0.34 → 0.41 (improving)
Production CTR / conversion: flat or declining
```
**Diagnosis**: Evaluation set has leaked or is no longer representative of production. Metrics are improving on a corrupted or stale benchmark.

**Root causes**:
1. Eval set built from same time period as training, not held-out future
2. Eval set too small → metrics are noisy, "improvements" are within noise floor
3. Production distribution has drifted away from eval distribution
4. Model changes affect which users/items are scored — selection effect

**Actions**:
- Rebuild eval set: strictly future data, same sampling process as production
- Compare production and evaluation distributions with calibrated drift alerts and outcome performance
- Add shadow mode logging: score production traffic, compare predicted vs actual outcomes
- Use paired, dependence-aware uncertainty to distinguish improvement from noise

---

## Group 5: Regression and Forecasting Patterns

### Pattern 5.1 — Low scaled error, but high systematic bias
```
MASE = 0.72 (beats naive)
Mean bias = +25% (consistently over-predicts)
```
**Diagnosis hypothesis**: MASE is low relative to the training naive scale, but the
model is systematically biased. Directly score the seasonal-naive forecast on the same
test rows before claiming out-of-sample superiority.

**Root causes**:
1. Training data not representative of evaluation period (e.g., trained on high-demand period)
2. Model overweights recent trend — needs bias correction or drift adjustment
3. Target variable has a trend the model hasn't captured

**Actions**:
- Test any train/validation-fitted bias correction on untouched data; do not fit it on test
- Check: is bias consistent across segments or concentrated in specific groups? Segment-specific correction may be needed.
- For inventory planning: use quantile regression at appropriate quantile rather than mean prediction
- Report bias separately from MASE — these are independent failure modes

---

### Pattern 5.2 — MASE < 1 on aggregate, MASE > 1 on key segments
```
MASE_overall = 0.65
MASE_segment_A = 1.4 (above the training naive scale)
MASE_segment_B = 0.4 (strong)
Segment A = 60% of revenue
```
**Diagnosis**: Model averages out well, but fails on the most important segment. Aggregate metric hides the real problem.

**Root causes**:
1. Segment A has different dynamics not captured by shared features
2. Not enough training data for Segment A specifically
3. Model was tuned to minimize overall loss, which is dominated by Segment B volume

**Actions**:
- Always report MASE by segment, not just aggregate — this pattern is common and dangerous
- Train segment-specific models if Segment A dynamics are genuinely different
- Weight training loss by business/segment importance when justified, and report the
  trade-off against unweighted aggregate and segment metrics

---

## Group 6: Credit & Fraud-Specific Patterns

### Pattern 6.1 — Gini stable, default rate rising
```
Gini (validation): 0.55 → 0.54 → 0.53 (stable)
Portfolio default rate: 1.5% → 2.1% → 3.2% (rising)
```
**Diagnosis hypothesis**: rank discrimination is stable, but this does not establish
stable risk levels. Population mix, within-band calibration, policy, and concept drift
remain plausible.

**Root causes**:
1. Macroeconomic change — more risky borrowers applying due to economic stress
2. Origination channel changed — new marketing attracting different segment
3. Approval rate changed — different cutoff policy changing who gets scored

**Actions**:
- Check PSI: compare score distribution of recent applicants to training population
- Check approval rate: if rising → cutoff lowered → admitting riskier borrowers at same model threshold
- Distinguish: is default rate rising for the SAME score band, or because more applicants are in low-score bands?
- Check observed-to-expected default by score band, vintage, product, and channel. A
  changed score mix with stable within-band outcomes supports mix shift; rising
  within-band defaults indicate calibration or concept drift.

---

### Pattern 6.2 — KS drops, Gini stable
```
KS: 52 → 38
Gini: 0.62 → 0.60
```
Note: KS thresholds (e.g., KS < 40 = "acceptable") are industry convention without academic backing — see foundations/metric_interpretation.md. Interpret relative change, not absolute value.

**Diagnosis**: The maximum separation point (KS) has weakened while overall discrimination (Gini/AUC) is stable. This often means the score distribution shape has changed.

**Root causes**:
1. ROC-shape or segment-mixture change concentrated near the maximum separation
2. Label definition, sampling, or outcome-maturity change
3. Sampling uncertainty in the empirical CDFs

**Actions**:
- Plot CDF of good/bad scores: where is the separation weakest? Has the crossing point moved?
- Re-evaluate the cutoff using calibrated expected loss/contribution, approval constraints,
  and segment outcomes. KS diagnoses separation; its maximum is not a policy threshold.

---

### Pattern 6.3 — Fraud drift attribution check
```
PSI on transaction features: 0.15–0.30 (moderate-significant shift)
Fraud loss rate: rising despite retraining
KS: declining faster than typical seasonal variation
```
**Diagnosis hypothesis**: fraud distribution shift can be adversarial, but PSI/KS cannot
identify the cause. Compare attack-vector concentration and matured outcomes against
label, policy/logging, seasonal, pipeline, and organic population explanations before
attribution or retraining changes.

**Root causes**:
1. Fraudsters iterating against your model — successful patterns get reused, blocked ones get mutated
2. Retraining cadence too slow relative to attacker iteration speed
3. Feature set is static — attackers have learned which signals you monitor

**Actions**:
- Segment PSI by channel/attack vector, not just aggregate — adversarial shift is usually concentrated, not uniform
- Shorten the retraining window for fraud specifically, relative to organic-drift domains
- Add features that are harder to game (velocity, network/graph) alongside static attributes
- Before assuming "population changed" from a PSI spike, check whether loss concentrates on a pattern absent from training (a new attack signature)

---

## Group 7: Evaluation Validity Patterns (Leakage & Label Immaturity)

### Pattern 7.1 — Metrics too good to be true
```
AP = 0.85 (positive rate = 2%)   → 42.5x lift
AUC-ROC = 0.98
Train AP ≈ Val AP ≈ Test AP (suspiciously stable)
```
**Diagnosis hypothesis**: leakage or evaluation contamination is high priority, but high
metrics alone do not prove either.

**Root causes**:
1. Target-derived features: a feature computed from or correlated with the outcome after the fact
2. Future information in aggregations: e.g., 30-day rolling average computed using data after the event
3. ID-level matching leak: test users/entities also appear in training with their outcome
4. Label leak: the label itself or a near-proxy exists as a feature

**Actions** (systematic leakage hunt):
1. Remove all features computed after the prediction timestamp, re-evaluate
2. Check feature importance — is one feature overwhelmingly dominant? Investigate it.
3. Use shuffled-target training as a pipeline sanity test. Above-random results suggest
   evaluation/pipeline contamination or random variation; a passing result does not clear temporal leakage.
4. Re-build with strict **point-in-time** feature construction — each feature uses only data at or before the prediction cutoff (the `feature-onboarding` skill, `references/leakage_and_tautology.md`, defines the cutoff/embargo/as-of timeline and the label-proxy tautology test).

---

### Pattern 7.2 — Recent-cohort labels are immature (label maturation lag)
```
Eval cohort: transactions/applications from the last 30 days
Confirmed-positive rate in this cohort: unusually low
Same cohort re-measured 90+ days later: rate roughly doubles
```
**Diagnosis**: Outcomes that take time to materialize are censored for cohorts too
recent to complete the window. Prevalence is undercounted, but metric bias can move
either way depending on score- and action-dependent delay. Do not use the cohort for a
final comparison.

**Root causes**:
1. Eval window doesn't respect the outcome lag — recent cohort included despite unresolved outcomes
2. No distinction made between "confirmed negative" and "not yet confirmed positive"
3. Monitoring recomputes on a rolling recent window without adjusting for lag

**Actions**:
- Exclude cohorts younger than the outcome maturation window from evaluation
- If recent data must be used, call it a lower bound only with a fixed denominator and
  monotone, non-revocable positive labels; otherwise report an immature partial rate
- Track the same cohort over time (vintage analysis) rather than a single snapshot
- See `domains/fraud.md` / `domains/credit.md` for domain-specific maturation windows

---

## Group 8: Lead Scoring Patterns

### Pattern 8.1 — AP adequate, but sales team reports low lead quality
```
AP = 0.35 (15x lift over 2.3% baseline)
Precision@SDR_capacity = 0.08 (barely above break-even)
Sales feedback: "these leads are not interested"
```
**Diagnosis**: AP is measured over the full ranked list, but sales only works the top-k. The model ranks well overall but precision collapses at the operating k that matters.

**Root causes**:
1. k is larger than the region where the model has good precision — AP is misleading here
2. Model selection optimized global AP while operating `k` or threshold was not selected from business constraints
3. Model catches "intent signals" that look good statistically but don't reflect genuine buying interest

**Actions**:
- Compute Precision@k explicitly where k = SDR team capacity per period
- Plot precision by score decile: does precision drop sharply after top 10%? If yes, reduce k
- Collect SDR call outcome data — did high-scored leads actually engage? If not, feature set is wrong

---

### Pattern 8.2 — Score strongly correlates with company size or job title, not with behavior
```
Feature importance: "company_size" = 0.45 (dominant)
AP good on holdout
But: Precision@k on small companies = near-baseline
```
**Diagnosis**: Model learned ICP (Ideal Customer Profile) firmographics, not actual buying intent. High scores = large enterprise companies, regardless of whether they're ready to buy.

**Root causes**:
1. Large company leads closed more historically → model learned company size as proxy for conversion
2. Behavioral features (website visits, email opens) have low coverage or high noise
3. Training data conflates "company fit" with "buying timing"

**Actions**:
- Use held-out conditional and within-segment ablations; no fixed AP drop proves proxy behavior
- Evaluate model separately for each company size tier — does the model add lift within a size tier?
- Enrich with intent data (G2 reviews, job postings, funding signals) for genuine buying intent

---

### Pattern 8.3 — Conversion rate drops sharply at old model's threshold (selection bias signal)
```
Lead score distribution: bimodal — few leads below threshold T
Conversion rate: 12% above T, 1% below T (large gap)
But: only 3% of leads were ever worked below T
```
**Diagnosis**: Selection bias from the previous scoring model. The conversion rate gap is at least partly because leads below T were rarely called — not because they're actually bad leads.

**Root causes**:
1. Sales team used old model's threshold as a hard gate → labels below T are from untreated leads
2. New model trained on this data will reproduce the old model's bias

**Actions**:
- Do not use the conversion rate gap across the old threshold as evidence of model quality
- Design approved randomized exploration from power, capacity, contact constraints, and
  customer impact; do not use a universal traffic percentage or duration

---

## Group 9: Churn Prediction Patterns

### Pattern 9.1 — Good AP, negative campaign ROI
```
AP = 0.28 (8x lift over 3.5% baseline)
Precision@budget = 0.22
Break-even precision = 0.06
But: campaign ROI = -15%
```
**Diagnosis hypothesis**: prediction quality does not establish treatment response.
Negative ROI may reflect heterogeneous treatment effects, costs, offer design, or
campaign execution; observational risk scores cannot identify the causal class.

**Root causes**:
1. Model targets "sure churners" — customers who are already decided to leave
2. Model targets "safe customers" who scored high due to temporary inactivity, not real churn risk
3. Intervention type is wrong — discount offer to price-insensitive churners

**Actions**:
- Build uplift model if A/B holdout data exists: who responds to intervention, not who churns
- Audit post-outcome leakage and intervention timing; do not infer causal response types from risk features
- Size an approved randomized holdout from power, costs, capacity, and governance constraints

---

### Pattern 9.2 — Model catches most churners but misses high-MRR segment
```
Count-based recall@budget = 0.65 (good)
MRR-weighted recall@budget = 0.28 (poor)
High-MRR customers (top 20% of revenue) are in bottom 40% of churn scores
```
**Diagnosis**: Model is optimized for count-based loss. High-value customers are few in number so they have low weight in training. Model learns patterns from high-volume, low-value churners.

**Root causes**:
1. Training loss treats all customers equally regardless of MRR
2. High-MRR customers may churn for different reasons (not captured by features designed for mass market)
3. Eval metric was count-based AP, not MRR-weighted AP

**Actions**:
- Retrain with MRR-weighted sample weights in the loss function
- Evaluate with MRR-weighted precision@budget as the primary metric
- Build a separate model for high-MRR segment — their churn signals may be fundamentally different

---

### Pattern 9.3 — Churn model performance degrades quickly (2–3 months post-deployment)
```
Precision@budget at launch: 0.31
Precision@budget month 2: 0.24
Precision@budget month 3: 0.17
PSI on key behavioral features: 0.18–0.30
```
**Diagnosis hypothesis**: feature distribution shift is one possibility. Label maturity,
policy/logging changes, calibration failure, and concept drift require separate checks.

**Root causes**:
1. Behavioral features (usage frequency, feature adoption) are sensitive to product changes or seasonality
2. Training window doesn't include enough temporal variation
3. Model not retrained frequently enough for a fast-moving product

**Actions**:
- Calibrate drift and retraining triggers from stable historical periods, uncertainty,
  delayed-label performance, and business loss; choose window/cadence through validation

---

## Group 10: Recommendation Patterns

### Pattern 10.1 — NDCG high, catalog coverage < 10%
```
NDCG@10 = 0.38 (40% above the stated baseline, with uncertainty reported)
Coverage = 7% (only 7% of catalog is ever recommended)
Top 50 items account for 65% of all recommendations
```
**Diagnosis**: Popularity bias. Model is recommending the same popular items to everyone. Users with niche interests are not served. Revenue concentration risk.

**Root causes**:
1. Collaborative filtering overweights popular items because they have more interaction data
2. No diversity constraint in ranking
3. Training data itself is biased toward popular items (more clicks = more signal)

**Actions**:
- Add coverage as a monitored metric alongside NDCG — they trade off against each other
- Implement post-ranking diversity re-ranking: MMR (Maximal Marginal Relevance) or category diversification
- Evaluate NDCG separately for long-tail items vs head items — model likely performs much worse on long-tail

---

### Pattern 10.2 — NDCG strong on warm users, weak on new users (cold start gap)
```
NDCG@10 (users > 20 interactions) = 0.42
NDCG@10 (users 1–5 interactions) = 0.19
NDCG@10 (users 0 interactions) = 0.08 (compare with candidate-protocol-specific baselines)
New users = 35% of daily active users
```
**Diagnosis**: Collaborative filtering works for returning users but fails on cold start. 35% of users are getting near-random recommendations.

**Root causes**:
1. Pure collaborative filtering has no mechanism for users with sparse history
2. Item content features not used, so new items and new users can't be matched
3. Cold-start evaluation was never done — problem existed but wasn't visible in aggregate metrics

**Actions**:
- Build hybrid model: collaborative filtering + content-based fallback for sparse users
- Implement explicit cold-start protocol: for users with < 5 interactions, use content-based with popularity-within-category
- Measure and report NDCG separately by interaction count tier — never report only aggregate

---

### Pattern 10.3 — Offline NDCG improving each experiment, but A/B CTR never moves
```
Offline NDCG improves repeatedly while valid online confidence intervals exclude the
minimum practical CTR effect.
```
**Diagnosis**: Systematic offline-online gap. NDCG is not measuring what drives online CTR.

**Root causes**:
1. **Position bias**: training data clicks are biased toward positions 1–3; model improves NDCG on those positions but doesn't change what users actually see differently
2. **Metric mismatch**: NDCG optimizes rank of historically clicked items; but users click differently on new rankings
3. **Feedback loop**: the items that generate clicks in A/B are not the same items that generated clicks in the training data

**Actions**:
- Size approved exploration from power and harm constraints; log assignment/exposure propensities
- Require overlap and report weight clipping, effective sample size, variance, and uncertainty for IPS/SNIPS or doubly robust estimates
- Compare policy-aware offline estimates with a valid randomized benchmark
- Check if NDCG improvement correlates with revenue@k or session depth — if not, switch the offline target

---

## Synthesis: Diagnostic Decision Tree

```
Start: Identify the domain first (if known)
│
├─ LEAD SCORING
│   ├─ AP adequate, SDR reports poor quality? → Pattern 8.1: Check Precision@SDR_k
│   ├─ Score dominated by firmographic features? → Pattern 8.2: ICP, not intent
│   └─ Big conversion gap at old threshold? → Pattern 8.3: Selection bias
│
├─ CHURN PREDICTION
│   ├─ Good AP, negative campaign ROI? → Pattern 9.1: Prediction does not identify treatment response
│   ├─ Good count-recall, poor MRR-recall? → Pattern 9.2: Weight by revenue
│   └─ Rapid post-deployment decay? → Pattern 9.3: Discriminate shift, labels, policy, and logging causes
│
├─ RECOMMENDATION
│   ├─ NDCG strong, coverage < 10%? → Pattern 10.1: Popularity bias
│   ├─ Warm user NDCG good, new user NDCG poor? → Pattern 10.2: Cold start gap
│   └─ NDCG improving but A/B never moves? → Pattern 10.3: Offline-online gap
│
├─ CREDIT / FRAUD
│   ├─ Gini stable, default rate rising? → Pattern 6.1: Check mix and within-band calibration
│   ├─ KS drops, Gini stable? → Pattern 6.2: Score distribution shape changed
│   └─ PSI/KS shifting on a fraud model? → Pattern 6.3: Rule out adversarial adaptation before retraining
│
├─ FORECASTING
│   ├─ MASE < 1 but high systematic bias? → Pattern 5.1: Apply bias correction
│   └─ MASE good overall, bad on a key segment? → Pattern 5.2: Segment-specific correction
│
└─ GENERIC (applies to all domains)
    ├─ Recent cohort, outcome window not fully elapsed? → Pattern 7.2: Labels immature — check before trusting anything else
    ├─ Metrics suspiciously high? → Pattern 7.1: Check leakage first
    ├─ AUC-ROC and AP diverge? → Pattern 1.x: Inspect prevalence and operating region
    ├─ Train >> Val >> Test progressively? → Pattern 2.1: Overfitting
    ├─ Good val, cliff at test? → Pattern 2.2: Distribution shift
    ├─ Val strong but A/B flat? → Pattern 2.3: Offline-online gap
    ├─ No acceptable PR operating point? → Pattern 3.1: Test signal and support
    ├─ Precision high, recall very low? → Pattern 3.2: Validate operating-policy intent
    ├─ Metrics improving sprint over sprint but production flat? → Pattern 4.2: Eval set stale or contaminated
    └─ Good metrics, bad business outcome? → Pattern 4.1: Economics / constraint mismatch
```

---

## When Multiple Patterns Match Simultaneously

If two or more patterns fire at once, use this priority hierarchy to determine the **primary investigation path**:

| Priority | Pattern type | Reason |
|---|---|---|
| 1 | **Pattern 7.1 — Leakage; Pattern 7.2 — Label immaturity** | If leakage exists or labels haven't matured, all other metrics are meaningless. Rule these out first. |
| 2 | **Pattern 2.x — Train/Val/Test divergence** | Evaluation setup must be valid before interpreting any result. |
| 3 | **Pattern 3.1 — Poor PR trade-off** | Test signal, support, and specification before model/threshold fixes. |
| 4 | **Pattern 1.1 — Wrong metric** | Metric choice distorts all other diagnoses. Fix the lens before reading it. |
| 5 | **Domain-specific patterns** (5.x, 6.x, 8.x, 9.x, 10.x) | Investigate after data/setup issues are ruled out. |
| 6 | **Pattern 4.x — Business mismatch** | Address last — only meaningful when model validity is confirmed. |

**Example**: AP too low + metrics collapse from val to test + leakage suspected.
→ Step 1: run leakage hunt (Pattern 7.1). If clean → investigate train/val/test split (Pattern 2.2). Don't diagnose root cause of low AP until the evaluation setup is confirmed valid.

**When patterns conflict** (e.g., 7.1 and 2.2 both explain the data equally): run the leakage hunt first — it takes 30 minutes and either closes the case or makes distribution-shift investigation meaningful.
