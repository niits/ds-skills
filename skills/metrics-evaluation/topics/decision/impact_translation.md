# Business Impact Translation

## From Precision/Recall to Business Numbers

### Template Calculation

Given:
- N = cases per day (or week/month)
- p = positive rate
- Precision = P, Recall = R at operating threshold

```
TP/day = N × p × R
FP/day = TP/day × (1 - P) / P   [from definition of precision]
FN/day = N × p × (1 - R)
```

### Example: Manual Quality Review
- N = 10,000 cases/day
- p = 4% true defect rate, or 400 defects/day
- Model: Precision = 0.50, Recall = 0.60

```
TP = 400 × 0.60 = 240 defects found/day
FP = 240 × (0.50/0.50) = 240 unnecessary reviews/day
FN = 400 × 0.40 = 160 defects missed/day

Review cost = (TP + FP) × cost_per_review
Incremental value = avoidable_cost_of_detected_defects - review_cost
                    - intervention_cost - false-action_cost
Compare with the current review policy. Report sensitivity bounds when avoidability,
action effectiveness, or unit costs are uncertain.
```

---

## Cost of FP vs FN

Always ask: which is worse?

| Use Case | Cost of FP | Cost of FN | Implication |
|---|---|---|---|
| Medical diagnosis | Unnecessary follow-up/treatment | Missed disease | Disease/workflow-specific; screening often prioritizes sensitivity before confirmation |
| Churn prediction | Marketing cost | Lost revenue | Depends on LTV vs campaign cost |
| Quality inspection | Unnecessary review/rework | Defect reaches downstream process | Depends on review and defect costs |
| Spam filter | Missed legitimate email (high cost) | Spam received | Very low FP required |

---

## Precision@k vs AP

When business only acts on top-k predictions (e.g., "flag top 200 accounts for review"):

- AP summarizes the full curve and remains useful for model comparison, but it is secondary to the operating decision
- **Precision@k** is what matters: of the top 200 flagged, how many are actually positive?
- Report Precision@k where k = actual review capacity
- Also report how Precision@k compares with the current policy and with uniform random
  selection from the same fixed candidate population, whose expected precision is that
  population's positive rate.

---

## When Metrics Don't Map to Business Value

Sometimes the model metric is fine but business impact is unclear. Dig deeper:

1. **Who acts on the model output?** (analyst, automated system, customer)
2. **What action do they take?** (review, route, notify, price change)
3. **What is the counterfactual?** (what happens without the model?)
4. **Is the action reversible?** (discarding an item vs sending a notification)
5. **What is the feedback loop?** (does the action change future data distribution?)

---

## When to Say "The Metrics Don't Support Shipping"

Say it clearly when:
- Precision at any reasonable threshold is below the cost-effective threshold
- Full incremental expected net value is negative versus the current policy after TP
  preventability/value, all action/review costs, FP friction, and FN opportunity cost
- The model doesn't beat the current heuristic/rule-based system
- The required recall to be useful implies precision below acceptable level

Do not soften this. "The model is not ready for production at these metrics" is the correct statement.
