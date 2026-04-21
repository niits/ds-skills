# Business Metrics ↔ ML Metrics Mapping

## How to Use This File

Two directions:
1. **ML → Business**: Given AP/AUC/RMSE, what does it mean in business terms?
2. **Business → ML**: Given a business KPI target, what ML metric threshold do you need?

Always start from the business question, not the ML metric.

---

## Domain: Fraud Detection

### Business KPIs
| Business KPI | Definition | Typical Target |
|---|---|---|
| Fraud loss rate | Fraud amount / Total transaction value | < 0.1% |
| False positive rate (FPR) | Blocked legit txn / Total legit txn | < 0.5% (auto-block), < 2% (flag) |
| Review queue SLA | # flags / analyst capacity | < 200 flags/analyst/day |
| Detection rate | Fraud caught / Total fraud | > 50% for high-value fraud |
| Chargeback rate | Chargebacks / Transactions | < 1% (Visa/Mastercard threshold) |

### Business KPI → Required ML Metric
```
If business needs FPR < 0.5% (auto-block):
  At threshold T where FPR = 0.5%:
  Precision must be > p / (p + 0.005×(1-p))
  e.g., p = 0.5% → Precision > 0.5%/(0.5%+0.5%×99.5%) ≈ 50%

If business needs detection rate > 50% at FPR < 0.5%:
  Check AUC-ROC at these operating coordinates: ROC point (FPR=0.005, TPR=0.5)
  This is more useful than overall AUC
```

### Domain-Specific ML Metrics for Fraud
- **KS Statistic**: max separation between fraud/legit score distributions. KS > 40 is good, > 60 is strong.
- **Precision@k**: where k = daily review capacity (e.g., top 500 flagged)
- **Dollar-weighted AP**: weight each positive by fraud amount — catching $10k fraud > catching $10 fraud
- Avoid: AUC-ROC (misleading at 0.5% positive rate)

---

## Domain: Credit Risk / Lending

### Business KPIs
| Business KPI | Definition | Typical Target |
|---|---|---|
| Default rate | Defaults / Loans issued | Product-specific, usually 1–10% |
| Loss rate | Loss amount / Portfolio value | < 2–5% |
| Approval rate | Approvals / Applications | Depends on risk appetite |
| Portfolio yield | Interest earned / Portfolio value | Product-specific |
| Gini coefficient | 2×AUC - 1 | > 0.4 acceptable, > 0.6 good |
| KS statistic | Max TPR - FPR across thresholds | > 30 acceptable, > 50 good |

### Business KPI → Required ML Metric
```
If business sets approval rate target = 70%:
  Threshold = score at 30th percentile of application scores
  Report: default rate of approved (should be < target default rate)
  Report: default rate of rejected (sanity check — should be >> approved)

If business sets loss rate target < 3%:
  Simulate: approve top 70% by score → what is expected loss rate?
  If expected loss > 3%, model needs improvement or approval rate must drop
```

### Domain-Specific ML Metrics for Credit
- **Gini = 2×AUC - 1** `[Industry, derived from Hosmer & Lemeshow via identity]`: Gini < 0.4 is poor, 0.4–0.6 acceptable, > 0.6 good. See Siddiqi (2006), "Credit Risk Scorecards", Wiley.
- **KS Statistic** `[Industry convention — no academic source for thresholds]`: KS < 20 weak, 20–40 acceptable, 40–60 good. Thresholds are banking practice, not from textbook. See metric_interpretation.md for caveat.
- **PSI** `[Industry convention — statistically unjustified per Yurdakul 2018, J. Risk Model Validation]`: PSI < 0.1 stable, > 0.25 major shift. Treat as directional signal only, not a hard threshold.
- **Approval rate vs default rate curve**: Plot default rate at each approval rate level — equivalent to ROC but in business terms.
- **Score card points**: Sometimes scorecard-style integer scores required by regulation (Basel II/III model validation).

### Never Report for Credit
- Raw AUC without converting to Gini (stakeholders don't think in AUC)
- F1 score (threshold-dependent, not how credit decisions work)
- AP (not standard in credit risk)

---

## Domain: Churn Prediction / Retention

### Business KPIs
| Business KPI | Definition | Typical Target |
|---|---|---|
| Monthly churn rate | Churned customers / Active customers | < 2–5% (SaaS) |
| Retained revenue | LTV of retained customers | Maximize |
| Campaign ROI | (Retained LTV - Campaign cost) / Campaign cost | > 1 (profitable) |
| Intervention rate | Customers contacted / Total customers | Budget-constrained |

### Business KPI → Required ML Metric
```
Campaign budget = B contacts/month
LTV of saved customer = L
Intervention cost = C per contact
Conversion rate of intervention = r (% who stay when contacted)

Break-even precision:
  P_breakeven = C / (L × r)
  e.g., L=$500, C=$10, r=30% → P_breakeven = $10/($500×0.3) = 6.7%
  Any precision > 6.7% → campaign is ROI-positive

Required recall:
  If business needs to save at least X% of churners:
  Recall must be > X% at precision > P_breakeven
```

### Domain-Specific Framing for Churn
- **Uplift modeling > prediction**: Don't predict who will churn — predict who will respond to intervention. Churners who would stay anyway are wasted contacts.
- **Precision@budget**: Budget = 1000 contacts/month → Precision@1000
- **Revenue-weighted recall**: Catching a high-LTV churner is more valuable than a low-LTV one
- Report segment breakdown: churn rate and model performance by customer segment

---

## Domain: Marketing / Recommendation / CTR

### Business KPIs
| Business KPI | Definition | Typical Target |
|---|---|---|
| CTR | Clicks / Impressions | Baseline-relative |
| Conversion rate | Conversions / Clicks | Baseline-relative |
| ROAS | Revenue / Ad spend | > 1 (often > 3–5 for healthy campaigns) |
| Revenue per session | Revenue / Sessions | Maximize |
| Incremental lift | Revenue with model - Revenue without | Must be positive |

### Business KPI → Required ML Metric
```
If business needs CTR lift > 20%:
  Ranking model must push high-CTR items to top positions
  NDCG@k where k = visible slots (e.g., @5 for mobile, @10 for desktop)
  Required NDCG improvement depends on current baseline CTR distribution

If business evaluates by A/B test:
  ML metric (NDCG) is a proxy — business will validate by CTR/revenue lift
  Set ML metric threshold such that past A/B tests with that NDCG delta showed significant lift
```

### Domain-Specific ML Metrics for Recommendation
- **NDCG@k**: Standard, but k must match real UX (# visible items, not arbitrary)
- **Revenue@k**: Weight items by actual transaction value, not binary relevance
- **Coverage**: % of catalog recommended — low coverage = popularity bias
- **Novelty / Serendipity**: Recommending only popular items → NDCG high but business value low
- **Online metrics always override offline**: NDCG improvement that doesn't translate to CTR/revenue lift = model doesn't work in practice

---

## Domain: Demand Forecasting / Operations

### Business KPIs
| Business KPI | Definition | Typical Target |
|---|---|---|
| Stockout rate | Stockouts / Total SKUs | < 2–5% |
| Overstock cost | Holding cost of excess inventory | Minimize |
| Fill rate | Orders fulfilled / Orders placed | > 95–99% |
| Forecast bias | Mean(predicted - actual) / Mean(actual) | Close to 0 |

### Business KPI → Required ML Metric
```
Asymmetric cost: stockout cost ≠ overstock cost
  If stockout_cost >> overstock_cost: use quantile regression at high quantile (e.g., 0.8)
  If costs are symmetric: use median regression (MAE-optimal)

Required MASE (Mean Absolute Scaled Error):
  MASE = 1.0 → same as naive lag-1 prediction [Definitional]
  MASE > 1.0 → model is worse than doing nothing [Definitional]
  MASE < 1.0 → better than naive; no verified threshold for "good enough" — compare to previous model
```

### Domain-Specific ML Metrics for Forecasting
- **MASE**: Compare to naive baseline, not absolute MAE
- **SMAPE**: Symmetric MAPE — handles zero/near-zero values better than MAPE
- **Bias**: Systematic over/under-prediction. Unbiased model required for inventory planning.
- **Quantile loss**: When you need prediction intervals (safety stock calculation)
- Never use: R² (misleading for time series), MAPE (explodes near zero)

---

## Quick Reference: Business KPI to ML Metric

| Business KPI | ML Metric to Report | Secondary Metric |
|---|---|---|
| Fraud loss reduction | Dollar-weighted AP, KS stat | Precision@review_capacity |
| Credit default rate | Gini (=2×AUC-1), KS stat | Default rate by score decile |
| Churn revenue retention | Precision@budget, Revenue-weighted recall | Uplift vs no-model |
| Campaign ROI | Precision@k where k=budget | Break-even precision |
| CTR / Conversion | NDCG@k (k=visible slots) | Online A/B test (ground truth) |
| Revenue per session | Revenue@k | Coverage, diversity |
| Inventory fill rate | MASE, Bias | Quantile accuracy |
| Queue SLA compliance | Precision@capacity | Throughput vs capacity |

---

## Red Flags in Business-ML Alignment

- **Model metric improving but business KPI flat**: model optimizes wrong thing — re-check objective alignment
- **Business KPI improving but model metric flat**: model may not be causal — check for confounders
- **High offline metric, failed A/B test**: distribution shift, feedback loop not modeled, or metric doesn't capture what matters
- **Business sets ML metric target directly** (e.g., "we need AUC > 0.85"): ask WHY — trace back to business KPI, the AUC target may be wrong
