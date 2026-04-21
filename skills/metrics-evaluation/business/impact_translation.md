# Business Impact Translation

## From Precision/Recall to Business Numbers

### Template Calculation

Given:
- N = cases per day (or week/month)
- p = positive rate
- Precision = P, Recall = R at operating threshold

```
True positives caught per day  = N × p × R
False positives triggered/day  = N × (1 - p) × (P / (1 - P)) × ... 

Simpler:
  TP/day = N × p × R
  FP/day = TP/day × (1 - P) / P   [from definition of precision]
  FN/day = N × p × (1 - R)
```

### Example: Fraud Detection
- N = 100,000 transactions/day
- p = 0.5% fraud rate → 500 frauds/day
- Model: Precision = 0.40, Recall = 0.30
- Average fraud value = $200

```
TP = 500 × 0.30 = 150 frauds caught/day → $30,000 saved
FP = 150 × (0.60/0.40) = 225 false alerts/day
FN = 500 × 0.70 = 350 frauds missed/day → $70,000 lost

Analyst cost: 225 FP × $5/review = $1,125/day
Net value: $30,000 - $1,125 = $28,875/day
```

---

## Cost of FP vs FN

Always ask: which is worse?

| Use Case | Cost of FP | Cost of FN | Implication |
|---|---|---|---|
| Fraud blocking | Customer friction, churn risk | Loss of fraud value | Balance — don't block good customers |
| Fraud flagging (soft alert) | Analyst time | Loss of fraud value | Can tolerate higher FP |
| Medical diagnosis | Unnecessary treatment | Missed disease | Usually: low FP more critical |
| Churn prediction | Marketing cost | Lost revenue | Depends on LTV vs campaign cost |
| Credit risk | Rejected good loan (lost revenue) | Bad loan (loss) | Depends on margin |
| Spam filter | Missed legitimate email (high cost) | Spam received | Very low FP required |

---

## Precision@k vs AP

When business only acts on top-k predictions (e.g., "flag top 200 accounts for review"):

- AP summarizes the full curve — irrelevant
- **Precision@k** is what matters: of the top 200 flagged, how many are actually positive?
- Report Precision@k where k = actual review capacity
- Also report: how does Precision@k compare to baseline (random = positive_rate)?

---

## When Metrics Don't Map to Business Value

Sometimes the model metric is fine but business impact is unclear. Dig deeper:

1. **Who acts on the model output?** (analyst, automated system, customer)
2. **What action do they take?** (block, flag, email, price change)
3. **What is the counterfactual?** (what happens without the model?)
4. **Is the action reversible?** (blocking a transaction vs sending an email)
5. **What is the feedback loop?** (does the action change future data distribution?)

---

## When to Say "The Metrics Don't Support Shipping"

Say it clearly when:
- Precision at any reasonable threshold is below the cost-effective threshold
- TP/day × value_per_TP < FP/day × cost_per_FP
- The model doesn't beat the current heuristic/rule-based system
- The required recall to be useful implies precision below acceptable level

Do not soften this. "The model is not ready for production at these metrics" is the correct statement.
