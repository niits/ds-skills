# Domain Guide: Recommendation Systems

## What Recommendation Is Actually Solving

Recommendation ranks items for a user to maximize a business objective.
The objective is almost never "predict what the user clicks" — it is usually
"maximize revenue, engagement, or retention" subject to business constraints.

**Offline metrics are proxies. A/B test results are ground truth.**

The most common mistake: optimizing NDCG offline and shipping a model
that doesn't move any business metric in production.

---

## Types of Recommendation Problems

| Type | Signal | Cold Start? | Primary Metric |
|---|---|---|---|
| Collaborative filtering | User-item interaction history | Severe for new users/items | NDCG@k, Hit Rate@k |
| Content-based | Item features (text, category, tags) | Mitigated for new items | Precision@k on test users |
| Session-based | Current session behavior | New users supported | MRR@k, Hit Rate@k |
| Context-aware | Time, location, device | Depends on context features | Online CTR / CVR |
| Hybrid | Combination | Depends on design | A/B test primary |

---

## Business KPIs

| KPI | Definition | Notes |
|---|---|---|
| CTR (Click-Through Rate) | Clicks / Impressions | Position-biased — normalize by position |
| CVR (Conversion Rate) | Purchases / Clicks | Downstream of CTR |
| Revenue per session | Total revenue / Sessions | Integrates CTR + CVR + AOV |
| AOV (Average Order Value) | Revenue / Orders | High CTR + low AOV = wrong items |
| Session depth | Pages/items viewed per session | Engagement proxy |
| Return visit rate | Sessions with return visit / Total sessions | Retention signal |
| Catalog coverage | Unique items recommended / Total catalog | Low = popularity bias |
| Incremental revenue | Revenue_treatment - Revenue_control (A/B) | Ground truth |

### Which KPI to Optimize For
- **Discovery product** (new users, cold start): prioritize coverage and diversity
- **High-frequency product** (daily users, streaming): prioritize engagement (session depth, return rate)
- **E-commerce**: prioritize revenue per session and CVR
- **Content platform**: prioritize session depth and return visit rate

---

## Offline ML Metrics

### NDCG@k (Normalized Discounted Cumulative Gain)
- Measures quality of ranking in top-k positions
- Higher-ranked relevant items contribute more
- **k must match actual visible positions** in the UI: @5 for mobile, @10 for desktop, @20 for scroll-heavy

```
NDCG@k = DCG@k / IDCG@k
DCG@k = Σ (rel_i / log2(i+1)) for i = 1..k
```

> Source: Järvelin & Kekäläinen (2002), ACM TOIS — original NDCG definition.

**Limitation**: NDCG treats all "relevant" items equally. Buying a $200 item ≠ buying a $10 item.
Use Revenue@k when purchase value matters.

### Hit Rate@k (HR@k)
- Fraction of users for whom the held-out item appears in top-k recommendations
- Simpler than NDCG, easier to explain to stakeholders
- Use when: binary relevance (bought/not bought), e-commerce

### MRR (Mean Reciprocal Rank)
- Average of 1/rank where rank = position of first relevant item
- Useful when only the first click/purchase matters (navigational intent)
- Heavily penalizes relevant items pushed below rank 3

### Precision@k and Recall@k
- Precision@k: of top-k recommendations, fraction that are relevant
- Recall@k: of all relevant items for this user, fraction appearing in top-k
- Recall@k useful when catalog is small and covering user preferences matters

### Coverage
```
Coverage = |unique items recommended to any user| / |total catalog|
```
No verified absolute thresholds. Compare coverage to:
- The current/previous model (is it higher or lower?)
- A popularity-only baseline (does the model recommend more of the long tail?)

Low coverage relative to baseline signals popularity bias. The right threshold depends on catalog size and business discovery goals.

### Diversity (Intra-List Diversity, ILD)
```
ILD = 1 - (average pairwise similarity among top-k items)
```
High NDCG + low ILD = the model recommends many items from the same category.
Users abandon recommendation feeds that feel repetitive.

---

## The Offline-Online Gap — Why It Exists and How to Diagnose It

### Why Offline Metrics Often Don't Translate

1. **Position bias in training data**: items shown at position 1 get clicked more regardless of quality.
   Model trained on click data learns "popular = relevant," not "quality = relevant."

2. **Feedback loop bias**: the training data reflects the old recommendation policy.
   Items never shown have zero clicks, but may be highly relevant.

3. **Metric mismatch**: NDCG optimizes rank of historically clicked items.
   But users may click differently on new recommendations.

4. **Diversity effect**: users engage more with diverse recommendations, but NDCG rewards
   concentrating the best items at the top regardless of diversity.

### Detecting the Gap Before A/B Test
- **Popularity overlap**: what fraction of top-k recommendations are in the top-10% most popular items?
  Compare to the popularity baseline — if similar, model learned nothing beyond popularity.
- **Novelty score**: what fraction of recommendations has the user not seen before?
  If near 0%: model isn't surfacing new items.
- **ILD check**: compute intra-list diversity on recommendations. Compare to random baseline.

---

## Evaluation Protocol for Recommendation

### Step 1: Choose the Right Eval Strategy

**Temporal split (required for production-realistic evaluation)**:
- Train on interactions before time T
- Test on interactions after T
- Never random split — it leaks future behavior into training

**Leave-one-out split (common but optimistic)**:
- For each user, hold out their last interaction
- Faster but overestimates performance on returning users

**User-cold-start evaluation (critical, often skipped)**:
- Hold out users with no training history
- Evaluate separately — cold start performance is typically substantially worse than warm users; the exact gap is domain-dependent

### Step 2: Compute Metrics by User Segment
Never aggregate metrics across all users — decompose by:

| Segment | Why It Matters |
|---|---|
| New users (0 interactions) | Cold start problem — often fails completely |
| Returning users (1–5 interactions) | Partial cold start |
| Active users (> 20 interactions) | Core of collaborative filtering value |
| High-value users | Revenue impact concentration |
| Niche interest users | Diversity and coverage failure mode |

### Step 3: Compute the Full Metric Set

For each segment:
```
NDCG@k (k = visible positions in UI)
Hit Rate@k
Coverage@k (across all users)
Diversity (ILD@k)
Novelty (fraction of recommendations unseen by user)
Popularity bias score (mean popularity rank of recommended items)
```

### Step 4: Check Population Stability
- Compare user activity distribution in train vs test
- Check item popularity distribution — has the catalog changed?
- If new items were added after training: evaluate on new vs old items separately

### Step 5: Before Claiming Model is Ready for A/B
Checklist:
- [ ] NDCG improvement is meaningful relative to model variance (no universal threshold — validate on holdout, not just the point estimate)
- [ ] Coverage is not materially lower than current model without business justification
- [ ] Diversity (ILD) is not lower than current model
- [ ] Cold-start Hit Rate@k is documented (not just warm users)
- [ ] Popularity bias score is not significantly higher than current model
- [ ] Business constraint items (promoted, high-margin, out-of-stock) are handled correctly

---

## Common Failure Modes

| Symptom | Diagnosis | Action |
|---|---|---|
| NDCG improves, CTR flat in A/B | Offline-online gap: position bias or metric mismatch | Debias training data; change offline metric to match A/B KPI |
| High NDCG, low coverage | Popularity bias — recommending same items everywhere | Add coverage regularization; use long-tail re-ranking |
| New user performance much worse | Cold start not addressed | Train hybrid with content features; add onboarding flow |
| AP/NDCG perfect (> 0.9) | Evaluation leakage — future items in training | Verify temporal split strictly |
| User complaints about repetitive recommendations | Low ILD — diversity not optimized | Add diversity re-ranking post-model |
| Engagement drops for niche users | Model over-optimizes for majority preferences | Cluster users; train segment-specific models |
| Business items (promoted) being buried | Model ignores business constraints | Add constraint layer on top of ranking |
| NDCG stable but revenue per session flat | Model maximizes clicks, not purchases | Switch label to purchases; use revenue-weighted NDCG |

---

## Position Bias — The Most Underhandled Problem

Items recommended at position 1 receive far more clicks than position 5, regardless of quality.
If the training data is click logs, the model learns positional effects, not item quality.

**Detection**: Compare CTR by position across all items. If CTR drops by > 50% from position 1 to 5: strong position bias in data.

**Fixes**:
1. **Inverse Propensity Scoring (IPS)**: weight training samples by 1/P(shown at position),
   where P is estimated from the position CTR curve.
2. **Unbiased evaluation data**: run a small randomized experiment (show random items to 1% of traffic)
   to get unbiased click labels.
3. **Position-aware models**: include position as a feature during training, then fix position = 1
   during scoring (position debias trick).

> Reference: Joachims et al. (2017), "Unbiased Learning-to-Rank with Biased Feedback", WSDM.

---

## Cold Start Protocol

### New User Cold Start
When a user has 0–5 interactions:
1. Fall back to content-based (item features × user registration attributes)
2. Use popularity within relevant category (not global popularity)
3. Explicitly evaluate: what is Hit Rate@10 for users with 0, 1, 2, 3–5 interactions separately?

### New Item Cold Start
When an item has < 10 interactions:
1. Use item content features (title, description, category, price) to find similar items
2. Bootstrap from similar items' interaction history
3. Monitor: how many interactions before collaborative filtering works? Set threshold.

### Never Treat Cold Start as Edge Case
In many products, new users = 30–50% of daily active users.
A model that works well for returning users but fails on new users has a severe business problem.
Always report cold-start metrics separately. If they are not reported, they were probably not evaluated.
