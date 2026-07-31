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
- **Dataset support**: train/val/test sizes, positive/relevant counts, and independent decision units
- **Business use case**: what decision does this model drive?
- **Operating constraints**: does business need high precision, high recall, or a specific threshold?
- **Current baseline**: heuristic, previous model, or random

Load exactly one matching `domains/<domain>.md` guide after identifying the domain; use
the generic workflow only when no guide applies.

Assume only non-critical descriptive context. If metric definition/implementation,
evaluation population, split validity, label maturity, support counts, operating
threshold or `k`, baseline, or required economics are unknown, stop with
`INSUFFICIENT EVIDENCE`. List the missing evidence and do not issue a shipping verdict.

---

### 2. Compute Honest Baselines

Always compute what a dumb baseline achieves. This is non-negotiable.

**For classification:**
- Expected no-skill PR/AP reference under random ranking = positive rate; estimate the
  finite-sample random AP under the exact tie/candidate protocol when it matters
- Always-positive classifier: precision = positive rate, recall = 1.0
- Majority class classifier: accuracy = 1 - positive rate (misleading — ignore accuracy on imbalanced data)

**For regression:**
- Fit the constant prediction on training data, then evaluate its RMSE/MAE on validation/test
- Predict previous value (for time series)

**For ranking:**
- Random NDCG depends on list length and relevance distribution
- State it explicitly

See `foundations/baselines.md` for exact calculations.

---

### 3. Evaluate Each Metric Honestly

Apply the framework from `foundations/metric_interpretation.md`.

**Key questions per metric:**

**Average Precision (AP):**
- Define the positive class, averaging, interpolation, and software implementation.
  AP, trapezoidal PR-AUC, classification mAP, and ranking MAP are not interchangeable.
- What is the expected random-ranking reference? (approximately positive rate for binary; not a floor)
- Compute Lift = AP_model / AP_random — compare against heuristic baseline and previous model
- Look at the PR curve shape — does precision collapse immediately at low recall?
- Very large lift increases leakage-review priority, but no fixed lift proves leakage

**AUC-ROC:**
- AUC = 0.5 is random `[Definitional]`. Thresholds from Hosmer & Lemeshow (2000): 0.7 acceptable, 0.8 good, 0.9 outstanding.
- AUC-ROC does NOT inflate for imbalanced data — but AP is preferred because it directly measures positive-class precision-recall trade-off (Saito & Rehmsmeier 2015).
- Prefer AP / AUC-PR when the positive class is rare.

**F1 / Precision / Recall:**
- Always state the threshold used.
- F1 at default threshold (0.5) is often meaningless — select the threshold on development data from costs, capacity, and constraints.
- No universal "good F1" exists — compare to baseline F1 at the same threshold.
- Report precision-recall at the operating threshold the business will actually use.

**RMSE / MAE:**
- Compare RMSE directly with the train-mean baseline; `RMSE/std(y_test) = 1` is not a general deployable-baseline identity.
- No verified thresholds below 1.0 — compare to previous model and task benchmarks.
- MAE is more interpretable in business units. Use it.

**NDCG / MAP:**
- State @k value used (NDCG@10 vs NDCG@100 are very different).
- Compare against: random, popularity baseline, previous model.

---

### 4. Diagnose Root Causes for Poor Metrics

If metrics are weak, don't just report it — investigate.

**Common causes (check in this order):**

1. **Evaluation validity and label maturity**: verify metric implementation, split, population, point-in-time inputs, complete outcomes, and entity overlap.
2. **Data leakage**: suspiciously high metrics make leakage a priority hypothesis; audit lineage and evaluation contamination.
3. **Distribution or label shift**: compare periods, segments, prevalence, and feature/score distributions with uncertainty.
4. **Label quality**: audit definition, censoring, noise, and segment-specific errors.
5. **Weak or missing signal**: use multivariate ablation and learning curves; low univariate AUC alone does not prove no signal.
6. **Model capacity/training**: compare appropriately regularized alternatives under the same validation protocol.
7. **Operating point or calibration**: select thresholds from costs/capacity on validation. Calibrate probabilities only when probability magnitude is used; calibration does not repair ranking.
8. **Wrong metric for the task**: are you optimizing AP while business acts on precision@100?

---

### 5. Map Business KPIs ↔ ML Metrics

Use `business/kpi_mapping.md` for domain-specific mappings.

**Step A — Identify the domain and business KPIs:**
- Fraud: fraud loss rate, FPR, review queue SLA → use KS stat, Precision@k
- Credit: default rate, Gini/KS → translate AUC to Gini (= 2×AUC - 1); any Gini quality cutoffs are industry conventions, not academically derived through that identity
- Churn: campaign ROI, LTV → compute break-even precision
- Recommendation: CTR, ROAS, revenue@k → NDCG@k where k = visible slots
- Forecasting: fill rate, stockout → MASE vs naive baseline, bias

**Step B — Derive required ML metric from business target:**
```
Break-even precision (only with an independently supported incremental action effect):
  P_breakeven = action_cost / (incremental_value × incremental_success_probability)

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
- Recent cohort with an outcome window that hasn't fully elapsed? → Pattern 7.2 (label maturation lag) — check before trusting anything else
- Metrics suspiciously good? → Pattern 7.1 (leakage) first
- AUC-ROC vs AP: do they tell the same story? If not → Pattern 1.x
- Train vs Val vs Test: monotonic drop or cliff? → Pattern 2.x
- Val metrics vs A/B outcome (if available): gap? → Pattern 2.3
- Aggregate vs segment metrics: do key segments underperform? → Pattern 5.2 / 6.x

For every headline and decision-critical segment, report support and uncertainty:
evaluation `n`, positive/relevant count, policy volume, a confidence interval, and a
paired interval for model-minus-baseline. Resample the independent deployment unit
(customer/account/query), cluster repeated observations, and use temporal blocks or
rolling origins for time-dependent data. Predefine confirmatory segments; mark
low-support or exploratory comparisons inconclusive.

**First-ever evaluation (no prior model, no A/B history)**: not all comparison axes will have data. State explicitly which axes are unavailable ("no previous model to compare against", "no A/B data yet") rather than skipping the synthesis step silently — the remaining axes (baseline lift, train/val/test, segment breakdown) still apply.

**Synthesis output must state:**
1. Which pattern(s) match the observed results
2. The most likely root cause (from the pattern's ranked list)
3. The single most important next action

`INSUFFICIENT EVIDENCE` is exempt from matched-pattern, most-likely-cause, two-metric,
and economic-translation requirements that the missing evidence makes impossible.
Mark those sections unavailable and list the exact evidence needed to resume.

Do not report a verdict without completing this synthesis step. A single metric can mislead;
the combination of signals is the diagnosis.

---

### 7. Give a Verdict

Be direct. Use one of:

- **Insufficient evidence**: a validity gate or required context is missing; no shipping decision is allowed.
- **Not usable**: Metric barely beats baseline. Do not ship. Investigate data/features.
- **Weak, conditional**: Acceptable only at a very specific operating point. High risk in production.
- **Adequate**: Meaningful lift over baseline, meets business threshold at some operating point.
- **Good**: Strong lift, stable across thresholds, ready for A/B test.
- **Strong**: Significant improvement over baseline and prior model. Ship with monitoring.

Verdict must reference:
- At least two metrics (not just one)
- The pattern matched in Step 6
- The specific action required before next step

Justify the verdict with numbers and uncertainty. Do not hide uncertainty behind vague
language, but do not express certainty the evidence cannot support. `Good` or `Strong`
is unavailable when the interval includes the baseline or business threshold.

---

### 8. Required Evaluation Report

Produce a medium-neutral report containing: context and metric definitions; assumptions
and evidence gaps; split/label-maturity validity gate; baseline; point estimates with
support and uncertainty; operating threshold or `k`; segment results; economic
translation and counterfactual; diagnostic hypotheses and discriminating checks;
verdict; and one required next action. In Databricks, render it as Markdown in `%md`
cells and do not use `displayHTML()`.

**Verdict block (`%md` cell):**

```markdown
## Verdict: INSUFFICIENT EVIDENCE

| | |
|---|---|
| **Metric** | AP = 0.20 |
| **Baseline** | AP_random = 0.022 |
| **Lift** | 9x |
| **Pattern matched** | Unavailable until evaluation validity is established |
| **Reason** | Suspected leakage makes the reported metrics non-decision-grade |
| **Required action** | Run leakage hunt before any other step |
```

Verdict prefix convention (copy-paste into title):
| Verdict | Prefix |
|---|---|
| Insufficient evidence | `## Verdict: INSUFFICIENT EVIDENCE` |
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
- **State support and uncertainty** for headline and decision-critical segment comparisons
- **No vague language**: "decent", "promising", "not bad" are banned. Use numbers.
- **State the threshold** when reporting precision/recall/F1
- **Diagnose, don't just describe**: if the metric is poor, say why and what to fix
- **Stop on invalid evidence**: do not turn assumptions about split validity, label maturity, metric definition, or economics into a shipping verdict

---

## Resources

### foundations/
- `baselines.md` — formulas for computing baselines per task type
- `metric_interpretation.md` — metric thresholds; what is and isn't verified (`[Academic]`/`[Industry]`/`[Definitional]` tags)

(`foundations/citations.md` holds full source citations for provenance audits. It is intentionally not part of this workflow — skip it unless someone specifically asks where a threshold comes from.)

### diagnosis/
- `patterns.md` — multi-metric patterns → diagnosis → root causes → actions; domain decision tree
- `checklist.md` — priority-ordered single-metric diagnostic checklist

### business/
- `kpi_mapping.md` — domain KPIs ↔ ML metrics (lead scoring, churn, recommendation, fraud, credit)
- `impact_translation.md` — TP/FP/FN → business impact numbers, break-even precision formula

### domains/
- `lead_scoring.md` — label bias, SDR capacity, selection bias, feature latency
- `churn_prediction.md` — uplift vs prediction, immortal cohort, MRR-weighted metrics
- `recommendation.md` — NDCG, coverage, cold start, position bias, offline-online gap
- `fraud.md` — label maturation lag, adversarial drift, dollar-weighted metrics
- `credit.md` — vintage/maturation, reject inference, scorecard validation
