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

### Pattern 1.1 — AUC-ROC high, AP low
```
AUC-ROC > 0.85
AP << positive_rate × 10  (lift < 5x)
```
**Diagnosis**: AUC-ROC and AP measure different things. AUC-ROC weights positive and negative class performance equally — when positives are rare, most of the weight goes to correct negative classification. AP measures only the precision-recall tradeoff on the positive class. The gap means the model ranks negatives well but does not rank positives well within the prediction list. (Note: AUC-ROC is not "inflated" — it accurately reflects performance on both classes. The problem is it measures the wrong thing for this use case.)

**Root causes** (check in order):
1. Wrong primary metric — AUC-ROC is not appropriate when positive-class ranking is what matters
2. Model predicts near-zero scores for almost everything — weak signal overall
3. Evaluation set too small on the positive side — AP estimate is noisy

**Actions**:
- Switch primary metric to AP / AUC-PR for all further evaluation
- Plot the PR curve: if precision collapses immediately at low recall, the model has no useful signal at any practical operating point
- Count true positives in top 1% of predictions vs random expectation (= positive_rate × total) — is the model concentrating positives at the top?

---

### Pattern 1.2 — AUC-ROC low, AP proportionally ok
```
AUC-ROC = 0.65–0.72
AP / positive_rate = 5x–10x lift
```
**Diagnosis**: Model has genuine predictive signal for positives but struggles with the negative side — possibly because negative class is heterogeneous or has overlapping features with positives.

**Actions**:
- Focus on PR curve, not ROC — the model may be usable at a selective operating point
- Investigate: are negatives homogeneous? Mixture of easy/hard negatives inflates ROC denominator
- Try: hard negative mining or cost-sensitive training to improve separation

---

## Group 2: Train vs. Eval vs. Production Diverge

### Pattern 2.1 — Train AP >> Val AP >> Test AP (monotonically degrading)
```
AP_train = 0.60
AP_val   = 0.35
AP_test  = 0.18
```
**Diagnosis**: Progressive overfitting. Model memorizes training data, generalizes poorly.

**Root causes**:
1. Model too complex relative to training data size (especially positives)
2. No regularization or insufficient regularization
3. Hyperparameters tuned on test set (leakage of test information into model selection)

**Actions**:
- Reduce model complexity: fewer trees, higher min_child_weight, lower max_depth
- Cross-validate on val set only — never touch test during tuning
- Check: n_positives in training set. If < 500, the model likely memorized them

---

### Pattern 2.2 — Train AP ≈ Val AP >> Test AP (cliff at test)
```
AP_train = 0.45
AP_val   = 0.42
AP_test  = 0.15
```
**Diagnosis**: Distribution shift between (train+val) and test. The model learned patterns that don't exist in the test period.

**Root causes**:
1. Time-based split not used — random split leaks future into training
2. Test set covers a different time period, segment, or population
3. Label definition changed between periods

**Actions**:
- Confirm split method: must be time-ordered if data is temporal
- Plot feature distributions: train vs test. Flag any features with Jensen-Shannon divergence > 0.1
- Check positive rate: train vs test. If different → population shift, not just model issue
- Re-train with a time-based split and re-evaluate

---

### Pattern 2.3 — Val AP good, A/B test shows no improvement
```
AP_val = 0.40 (strong, 15x lift)
A/B CTR lift = 0% (not significant)
```
**Diagnosis**: Offline-online gap. Model metrics don't translate to business outcome.

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

### Pattern 3.1 — Low precision AND low recall at all thresholds
```
At threshold T1 (high): Precision = 0.60, Recall = 0.05
At threshold T2 (low): Precision = 0.04, Recall = 0.80
AP = 0.08 (barely above baseline of 0.022)
```
**Diagnosis**: Model has almost no discrimination. The score is not useful as a ranking signal.

**Root causes**:
1. Features have very low correlation with target — check univariate feature AUCs
2. Label noise is high — actual positives look like negatives in feature space
3. Model undertrained or wrong objective (e.g., using accuracy loss on imbalanced data)
4. Fundamental problem difficulty: the positive class may not be predictable from available features

**Actions**:
- Run single-feature AUC for every feature. If max single-feature AUC < 0.60, the problem is data, not model.
- Review label definition: are "positives" actually meaningfully different from negatives in feature space?
- Try: t-SNE or UMAP on a sample — do positives cluster away from negatives? If not, prediction is fundamentally hard.
- Escalate to stakeholder: "The signal does not exist in the available features" is a valid conclusion.

---

### Pattern 3.2 — Precision very high, recall very low (operating point issue)
```
Precision@threshold = 0.85
Recall@threshold = 0.04
AP = 0.35 (adequate lift)
```
**Diagnosis**: Model has real signal but the operating threshold is set too conservatively. The model is only catching the most obvious positives.

**Root causes**:
1. Default threshold (0.5) used — wrong for imbalanced data
2. Score distribution skewed: predicted probabilities are all very low (calibration issue)
3. Business chose threshold to maximize precision without checking business impact of missed positives

**Actions**:
- Plot the PR curve and identify the operating point that meets business requirements
- Check calibration: what is the mean predicted score? If << positive_rate, model is miscalibrated
- Apply Platt scaling or isotonic regression, then re-examine score distributions
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
1. Review capacity is too small relative to the positive rate — economics don't work regardless of model quality
2. Break-even precision is too high (intervention cost > value saved)
3. Model needs to be more selective — optimize Precision@k directly, not AP

**Actions**:
- Re-compute break-even precision: cost_per_action / (value_saved × conversion_rate)
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
- Check PSI: compare score distribution in production to eval set. PSI > 0.25 → eval is stale.
- Add shadow mode logging: score production traffic, compare predicted vs actual outcomes
- Treat any AP improvement < 0.03 as noise unless n_positives_in_eval > 1000

---

## Group 5: Regression and Forecasting Patterns

### Pattern 5.1 — MASE < 1, but high systematic bias
```
MASE = 0.72 (beats naive)
Mean bias = +25% (consistently over-predicts)
```
**Diagnosis**: Model is better than naive in terms of error magnitude, but systematically biased. Usable for ranking/direction, not for absolute quantities.

**Root causes**:
1. Training data not representative of evaluation period (e.g., trained on high-demand period)
2. Model overweights recent trend — needs bias correction or drift adjustment
3. Target variable has a trend the model hasn't captured

**Actions**:
- Apply bias correction: subtract mean(predicted - actual) on val set from all predictions
- Check: is bias consistent across segments or concentrated in specific groups? Segment-specific correction may be needed.
- For inventory planning: use quantile regression at appropriate quantile rather than mean prediction
- Report bias separately from MASE — these are independent failure modes

---

### Pattern 5.2 — MASE < 1 on aggregate, MASE > 1 on key segments
```
MASE_overall = 0.65
MASE_segment_A = 1.4 (worse than naive)
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
- Weight training loss by segment importance (e.g., by revenue) — reduces aggregate MASE but improves critical segments

---

## Group 6: Credit-Specific Patterns

### Pattern 6.1 — Gini stable, default rate rising
```
Gini (validation): 0.55 → 0.54 → 0.53 (stable)
Portfolio default rate: 1.5% → 2.1% → 3.2% (rising)
```
**Diagnosis**: The model's discrimination power hasn't changed, but the population applying for credit has shifted (riskier applicants). This is a volume/mix problem, not a model problem.

**Root causes**:
1. Macroeconomic change — more risky borrowers applying due to economic stress
2. Origination channel changed — new marketing attracting different segment
3. Approval rate changed — different cutoff policy changing who gets scored

**Actions**:
- Check PSI: compare score distribution of recent applicants to training population
- Check approval rate: if rising → cutoff lowered → admitting riskier borrowers at same model threshold
- Distinguish: is default rate rising for the SAME score band, or because more applicants are in low-score bands?
- If same score band shows rising defaults → model has degraded. If mix shift → tighten cutoff, not retrain.

---

### Pattern 6.2 — KS drops, Gini stable
```
KS: 52 → 38
Gini: 0.62 → 0.60
```
Note: KS thresholds (e.g., KS < 40 = "acceptable") are industry convention without academic backing — see foundations/metric_interpretation.md. Interpret relative change, not absolute value.

**Diagnosis**: The maximum separation point (KS) has weakened while overall discrimination (Gini/AUC) is stable. This often means the score distribution shape has changed.

**Root causes**:
1. Score distribution has become more uniform — less extreme scores at the tails
2. Cutoff point is now in a region of weaker separation
3. Population shift concentrated at the KS inflection point

**Actions**:
- Plot CDF of good/bad scores: where is the separation weakest? Has the crossing point moved?
- Check if current operating cutoff is still near the KS maximum — if not, re-evaluate cutoff
- Gini stable means overall ranking is ok — this may not require retraining, just cutoff adjustment

---

## Group 7: Leakage Suspicion Patterns

### Pattern 7.1 — Metrics too good to be true
```
AP = 0.85 (positive rate = 2%)   → 38x lift
AUC-ROC = 0.98
Train AP ≈ Val AP ≈ Test AP (suspiciously stable)
```
**Diagnosis**: Data leakage. Something in the features contains information that wouldn't exist at prediction time.

**Root causes**:
1. Target-derived features: a feature computed from or correlated with the outcome after the fact
2. Future information in aggregations: e.g., 30-day rolling average computed using data after the event
3. ID-level matching leak: test users/entities also appear in training with their outcome
4. Label leak: the label itself or a near-proxy exists as a feature

**Actions** (systematic leakage hunt):
1. Remove all features computed after the prediction timestamp, re-evaluate
2. Check feature importance — is one feature overwhelmingly dominant? Investigate it.
3. Shuffle the target on training set: retrain, evaluate on test. If AP >> positive_rate → leakage confirmed.
4. Re-build with strict **point-in-time** feature construction — each feature uses only data at or before the prediction cutoff (the `feature-onboarding` skill, `references/leakage_and_tautology.md`, defines the cutoff/embargo/as-of timeline and the label-proxy tautology test).

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
2. Score threshold is set to maximize AP, not Precision@actual_k
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
- Ablation test: remove firmographic features, retrain, check AP. If AP drops < 10% → firmographics were proxy, not signal
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
- Implement forced exploration: randomly work 5–10% of below-threshold leads, observe true conversion
- Retrain after 1–2 quarters of exploration data to get unbiased labels

---

## Group 9: Churn Prediction Patterns

### Pattern 9.1 — Good AP, negative campaign ROI
```
AP = 0.28 (8x lift over 3.5% baseline)
Precision@budget = 0.22
Break-even precision = 0.06
But: campaign ROI = -15%
```
**Diagnosis**: Model correctly identifies at-risk customers, but those customers would have churned regardless of the intervention — or would have stayed anyway. Contacting them is wasted spend.

**Root causes**:
1. Model targets "sure churners" — customers who are already decided to leave
2. Model targets "safe customers" who scored high due to temporary inactivity, not real churn risk
3. Intervention type is wrong — discount offer to price-insensitive churners

**Actions**:
- Build uplift model if A/B holdout data exists: who responds to intervention, not who churns
- Segment model output: identify and exclude "already churned" signals (e.g., cancelled subscription, support escalation in last 7 days)
- A/B test the intervention: run with 10% holdout control group to measure true incremental retention

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
**Diagnosis**: Model degrading due to distribution shift in behavioral features. Seasonality, product changes, or market conditions altered how customers behave.

**Root causes**:
1. Behavioral features (usage frequency, feature adoption) are sensitive to product changes or seasonality
2. Training window doesn't include enough temporal variation
3. Model not retrained frequently enough for a fast-moving product

**Actions**:
- Monitor PSI monthly on top 10 features — retraining trigger: any feature PSI > 0.2
- Shorten training window to last 6 months (vs 2 years) — recency > volume for behavioral models
- Implement rolling retraining: monthly retrain on a rolling window, track Precision@budget on holdout

---

## Group 10: Recommendation Patterns

### Pattern 10.1 — NDCG high, catalog coverage < 10%
```
NDCG@10 = 0.38 (strong, 40% above baseline)
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
NDCG@10 (users 0 interactions) = 0.08 (near-random)
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
Experiment 1: NDCG @10 +0.012 → A/B CTR: +0.1% (not significant)
Experiment 2: NDCG @10 +0.018 → A/B CTR: +0.2% (not significant)
Experiment 3: NDCG @10 +0.025 → A/B CTR: +0.1% (not significant)
```
**Diagnosis**: Systematic offline-online gap. NDCG is not measuring what drives online CTR.

**Root causes**:
1. **Position bias**: training data clicks are biased toward positions 1–3; model improves NDCG on those positions but doesn't change what users actually see differently
2. **Metric mismatch**: NDCG optimizes rank of historically clicked items; but users click differently on new rankings
3. **Feedback loop**: the items that generate clicks in A/B are not the same items that generated clicks in the training data

**Actions**:
- Run a small randomized experiment (1–2% traffic): show random items, collect unbiased click data
- Retrain using unbiased data with IPS (Inverse Propensity Scoring) to correct position bias
- Change offline metric: instead of NDCG on historical clicks, use precision@k on IPS-weighted clicks
- Check if NDCG improvement correlates with revenue@k or session depth — if not, switch the offline target

---

## Synthesis: Diagnostic Decision Tree

```
Start: Identify the domain first
│
├─ LEAD SCORING
│   ├─ AP adequate, SDR reports poor quality? → Pattern 8.1: Check Precision@SDR_k
│   ├─ Score dominated by firmographic features? → Pattern 8.2: ICP, not intent
│   └─ Big conversion gap at old threshold? → Pattern 8.3: Selection bias
│
├─ CHURN PREDICTION
│   ├─ Good AP, negative campaign ROI? → Pattern 9.1: Sure churners / uplift needed
│   ├─ Good count-recall, poor MRR-recall? → Pattern 9.2: Weight by revenue
│   └─ Rapid post-deployment decay? → Pattern 9.3: Distribution shift, retrain
│
├─ RECOMMENDATION
│   ├─ NDCG strong, coverage < 10%? → Pattern 10.1: Popularity bias
│   ├─ Warm user NDCG good, new user NDCG poor? → Pattern 10.2: Cold start gap
│   └─ NDCG improving but A/B never moves? → Pattern 10.3: Offline-online gap
│
└─ GENERIC (applies to all domains)
    ├─ AUC-ROC high, AP low? → Pattern 1.1: AUC inflated by imbalance
    ├─ Train >> Val >> Test progressively? → Pattern 2.1: Overfitting
    ├─ Good val, cliff at test? → Pattern 2.2: Distribution shift
    ├─ Precision AND recall both low? → Pattern 3.1: No signal in features
    ├─ Metrics suspiciously high? → Pattern 7.1: Check leakage first
    └─ Good metrics, bad business outcome? → Pattern 4.1: Economics / constraint mismatch
```

```
Start: You have multiple metric results
│
├─ AUC-ROC high (> 0.85) but AP low (< 5x lift)?
│   └─ → Pattern 1.1: AUC inflated by imbalance. Switch to AP.
│
├─ Metrics collapse from train → val → test progressively?
│   └─ → Pattern 2.1: Overfitting. Regularize, reduce complexity.
│
├─ Metrics good on val but test is much worse (cliff)?
│   └─ → Pattern 2.2: Distribution shift. Check split method, feature drift.
│
├─ Val metrics strong but A/B flat?
│   └─ → Pattern 2.3: Offline-online gap. Check feedback loop, metric alignment.
│
├─ Precision AND recall both poor at all thresholds?
│   └─ → Pattern 3.1: No signal. Problem is data/labels, not model.
│
├─ Precision high, recall very low?
│   └─ → Pattern 3.2: Threshold too conservative. Recalibrate operating point.
│
├─ Metrics improving sprint over sprint but production flat?
│   └─ → Pattern 4.2: Eval set stale or contaminated. Rebuild eval.
│
├─ MASE < 1 but large systematic bias?
│   └─ → Pattern 5.1: Good rank, wrong absolute values. Apply bias correction.
│
├─ Metrics suspiciously high (AP > 20x lift, AUC > 0.97)?
│   └─ → Pattern 7.1: Probable leakage. Run leakage hunt before anything else.
│
└─ All metrics good but business KPI not met?
    └─ → Pattern 4.1: Economics don't work at current capacity/cost. Revisit constraints.
```

---

## When Multiple Patterns Match Simultaneously

If two or more patterns fire at once, use this priority hierarchy to determine the **primary investigation path**:

| Priority | Pattern type | Reason |
|---|---|---|
| 1 | **Pattern 7.1 — Leakage** | If leakage exists, all other metrics are meaningless. Rule it out first. |
| 2 | **Pattern 2.x — Train/Val/Test divergence** | Evaluation setup must be valid before interpreting any result. |
| 3 | **Pattern 3.1 — No signal in features** | If no feature has predictive power, model/threshold fixes won't help. |
| 4 | **Pattern 1.1 — Wrong metric** | Metric choice distorts all other diagnoses. Fix the lens before reading it. |
| 5 | **Domain-specific patterns** (8.x, 9.x, 10.x) | Investigate after data/setup issues are ruled out. |
| 6 | **Pattern 4.x — Business mismatch** | Address last — only meaningful when model validity is confirmed. |

**Example**: AP too low + metrics collapse from val to test + leakage suspected.
→ Step 1: run leakage hunt (Pattern 7.1). If clean → investigate train/val/test split (Pattern 2.2). Don't diagnose root cause of low AP until the evaluation setup is confirmed valid.

**When patterns conflict** (e.g., 7.1 and 2.2 both explain the data equally): run the leakage hunt first — it takes 30 minutes and either closes the case or makes distribution-shift investigation meaningful.
