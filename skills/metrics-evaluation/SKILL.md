---
name: metrics-evaluation
description: Use when you have model evaluation numbers (AP, AUC, F1, RMSE, NDCG, …) and need an honest, baseline-anchored verdict on whether the model is usable — not a spin. Computes dumb baselines, maps metrics to business KPIs, detects multi-metric failure patterns (leakage, distribution shift, miscalibration), and prescribes specific remediation. Primary focus on lead scoring, churn prediction, and recommendation; also covers general classification, regression, and ranking.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: ds-skills
---

# ML Metrics Evaluation

## Core Principle

**Never evaluate a metric in isolation.** Every number needs:
1. A baseline to compare against
2. A business context to interpret
3. An honest verdict — not a spin

If the metric is bad, say it's bad. Explain why and what to investigate.

---

## Workflow

### 1. Collect Context First

Before evaluating any metric, ask or infer:

- **Task type**: binary classification, multiclass, regression, ranking, anomaly detection
- **Class distribution**: positive rate, imbalance ratio
- **Dataset size**: train/val/test split sizes
- **Business use case**: what decision does this model drive?
- **Operating constraints**: does business need high precision, high recall, or a specific threshold?
- **Current baseline**: heuristic, previous model, or random

If context is missing, state assumptions explicitly before evaluating.

**If context is unavailable** (stakeholder offline, ticket ambiguous): proceed with documented assumptions, flag each one explicitly, and note in the verdict that assumptions require validation before shipping.

---

### 2. Compute Honest Baselines

Always compute what a dumb baseline achieves. This is non-negotiable.

**For classification:**
- Random classifier AP = positive rate (e.g., 2.2% positive → AP_random ≈ 0.022)
- Always-positive classifier: precision = positive rate, recall = 1.0
- Majority class classifier: accuracy = 1 - positive rate (misleading — ignore accuracy on imbalanced data)

**For regression:**
- Predict mean baseline: RMSE = std(y), MAE = mean(|y - mean(y)|)
- Predict previous value (for time series)

**For ranking:**
- Random NDCG depends on list length and relevance distribution
- State it explicitly

See `foundations/baselines.md` for exact calculations.

---

### 3. Evaluate Each Metric Honestly

Apply the framework from `foundations/metric_interpretation.md`.

**Key questions per metric:**

**Average Precision (AP / mAP):**
- What is AP_random? (= positive rate for binary) — this is the floor
- Compute Lift = AP_model / AP_random — compare against heuristic baseline and previous model
- Look at the PR curve shape — does precision collapse immediately at low recall?
- A lift > 20x is the trigger threshold for a mandatory leakage check (see Pattern 7.1)

**AUC-ROC:**
- AUC = 0.5 is random `[Definitional]`. Thresholds from Hosmer & Lemeshow (2000): 0.7 acceptable, 0.8 good, 0.9 outstanding.
- AUC-ROC does NOT inflate for imbalanced data — but AP is preferred because it directly measures positive-class precision-recall trade-off (Saito & Rehmsmeier 2015).
- Prefer AP / AUC-PR when the positive class is rare.

**F1 / Precision / Recall:**
- Always state the threshold used.
- F1 at default threshold (0.5) is often meaningless — threshold must be calibrated to the operating point.
- No universal "good F1" exists — compare to baseline F1 at the same threshold.
- Report precision-recall at the operating threshold the business will actually use.

**RMSE / MAE:**
- Report nRMSE = RMSE / std(y). nRMSE ≥ 1.0 means model is worse than or equal to predicting the mean `[Definitional]`.
- No verified thresholds below 1.0 — compare to previous model and task benchmarks.
- MAE is more interpretable in business units. Use it.

**NDCG / MAP:**
- State @k value used (NDCG@10 vs NDCG@100 are very different).
- Compare against: random, popularity baseline, previous model.

---

### 4. Diagnose Root Causes for Poor Metrics

If metrics are weak, don't just report it — investigate.

**Common causes (check in this order):**

1. **Weak features**: Are features actually predictive? Check feature importance, correlation with target.
2. **Label quality**: Label noise destroys AP. Check label definition and labeling process.
3. **Data leakage**: Suspiciously high metrics → leakage is a high-priority hypothesis, not the only one. Also check: overfitting, evaluation set contamination. Metrics collapse on time-based splits → leakage or distribution shift confirmed.
4. **Train/test distribution shift**: Model trained on one period, tested on another. Check feature distributions.
5. **Model underfitting**: Try a stronger model (LightGBM if using logistic regression). Check learning curves.
6. **Threshold / calibration**: Model may be well-ranked but poorly calibrated. Check calibration plot.
7. **Wrong metric for the task**: Are you optimizing AP but business cares about precision@100?

---

### 5. Map Business KPIs ↔ ML Metrics

Use `business/kpi_mapping.md` for domain-specific mappings.

**Step A — Identify the domain and business KPIs:**
- Fraud: fraud loss rate, FPR, review queue SLA → use KS stat, Precision@k
- Credit: default rate, Gini/KS → translate AUC to Gini (= 2×AUC - 1) `[Industry convention — thresholds not from academic source, derived from Hosmer & Lemeshow via identity; see metric_interpretation.md]`
- Churn: campaign ROI, LTV → compute break-even precision
- Recommendation: CTR, ROAS, revenue@k → NDCG@k where k = visible slots
- Forecasting: fill rate, stockout → MASE vs naive baseline, bias

**Step B — Derive required ML metric from business target:**
```
Break-even precision (churn/fraud flagging):
  P_breakeven = cost_per_contact / (value_saved × conversion_rate)

Required operating point (fraud auto-block):
  At FPR < X%, what is precision? Does recall meet detection target?
```

**Step C — Translate model results to business numbers:**
- Use `business/impact_translation.md` for TP/FP/FN daily counts
- Compute cost of FP vs cost of FN
- State whether current metrics meet the business threshold

**Critical check**: If business stakeholder set the ML metric target directly (e.g., "AUC > 0.85"),
trace it back to a business KPI. The ML target may be wrong.

---

### 6. Cross-Metric Synthesis and Pattern Matching

After evaluating individual metrics, look across all results for diagnostic patterns.
Use `diagnosis/patterns.md` — match observations to named patterns.

**Required comparisons:**
- AUC-ROC vs AP: do they tell the same story? If not → Pattern 1.x
- Train vs Val vs Test: monotonic drop or cliff? → Pattern 2.x
- Val metrics vs A/B outcome (if available): gap? → Pattern 2.3
- Aggregate vs segment metrics: do key segments underperform? → Pattern 5.2 / 6.x
- Metrics suspiciously good? → Pattern 7.1 (leakage) first

**Synthesis output must state:**
1. Which pattern(s) match the observed results
2. The most likely root cause (from the pattern's ranked list)
3. The single most important next action

Do not report a verdict without completing this synthesis step. A single metric can mislead;
the combination of signals is the diagnosis.

---

### 7. Give a Verdict

Be direct. Use one of:

- **Not usable**: Metric barely beats baseline. Do not ship. Investigate data/features.
- **Weak, conditional**: Acceptable only at a very specific operating point. High risk in production.
- **Adequate**: Meaningful lift over baseline, meets business threshold at some operating point.
- **Good**: Strong lift, stable across thresholds, ready for A/B test.
- **Strong**: Significant improvement over baseline and prior model. Ship with monitoring.

Verdict must reference:
- At least two metrics (not just one)
- The pattern matched in Step 6
- The specific action required before next step

Justify the verdict with numbers. No hedging.

---

### 8. Output Format (Databricks Notebook)

Write all output as Markdown in `%md` cells. Do NOT use `displayHTML()`.

**Verdict block (`%md` cell):**

```markdown
## Verdict: NOT USABLE

| | |
|---|---|
| **Metric** | AP = 0.20 |
| **Baseline** | AP_random = 0.022 |
| **Lift** | 9x |
| **Pattern matched** | Pattern 7.1 — probable leakage |
| **Reason** | ... |
| **Required action** | Run leakage hunt before any other step |
```

Verdict prefix convention (copy-paste into title):
| Verdict | Prefix |
|---|---|
| Not usable | `## ❌ Verdict: NOT USABLE` |
| Weak/conditional | `## ⚠️ Verdict: WEAK — CONDITIONAL` |
| Adequate | `## ✔ Verdict: ADEQUATE` |
| Good | `## ✅ Verdict: GOOD` |
| Strong | `## 🚀 Verdict: STRONG` |

**Metrics summary block (`%md` cell):**

```markdown
## Metrics Summary

| Metric | Model | Baseline | Lift | Assessment |
|---|---|---|---|---|
| AP | 0.20 | 0.022 (random) | 9x | Adequate — investigate leakage |
| AUC-ROC | 0.88 | 0.50 | — | Good discrimination |
```

---

## Quality Standards

- **Always state the baseline** — or explicitly explain why a universal baseline doesn't apply for this metric
- **State dataset size and positive rate** before any metric
- **No vague language**: "decent", "promising", "not bad" are banned. Use numbers.
- **State the threshold** when reporting precision/recall/F1
- **Diagnose, don't just describe**: if the metric is poor, say why and what to fix

---

## Resources

### foundations/
- `baselines.md` — formulas for computing baselines per task type (all sourced)
- `metric_interpretation.md` — metric thresholds with academic citations; what is and isn't verified

### diagnosis/
- `patterns.md` — multi-metric patterns → diagnosis → root causes → actions; domain decision tree
- `checklist.md` — ordered single-metric diagnostic checklist

### business/
- `kpi_mapping.md` — domain KPIs ↔ ML metrics (lead scoring, churn, recommendation, fraud, credit)
- `impact_translation.md` — TP/FP/FN → business impact numbers, break-even precision formula

### domains/
- `lead_scoring.md` — label bias, SDR capacity, selection bias, feature latency
- `churn_prediction.md` — uplift vs prediction, immortal cohort, MRR-weighted metrics
- `recommendation.md` — NDCG, coverage, cold start, position bias, offline-online gap
