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
| Fraud loss rate | Fraud amount / Total transaction value | Stakeholder/current-policy constraint |
| False positive rate (FPR) | Blocked legit txn / Total legit txn | Action- and harm-specific constraint |
| Review queue SLA | # flags / analyst capacity | Measured analyst capacity |
| Detection rate | Fraud caught / Total fraud | Value- and attack-specific target |
| Chargeback rate | Program-defined numerator / denominator | Current dated network/program threshold |

### Business KPI → Required ML Metric
```
If business needs FPR < 0.5% (auto-block):
  At an operating point with prevalence p, TPR r, and FPR f:
  Precision = p×r / (p×r + (1-p)×f)
  FPR alone does not determine precision.
  e.g., p=0.5%, r=50%, f=0.5% → Precision ≈ 33.4%

If business needs detection rate > 50% at FPR < 0.5%:
  Check AUC-ROC at these operating coordinates: ROC point (FPR=0.005, TPR=0.5)
  This is more useful than overall AUC
```

### Domain-Specific ML Metrics for Fraud
- **KS Statistic**: max separation between fraud/legit score distributions. Do not
  import credit-industry absolute KS labels into fraud; compare OOT change and policy utility.
- **Precision@k**: where k = daily review capacity (e.g., top 500 flagged)
- **Value-aware evaluation**: report count AP and Precision@capacity plus expected net
  value@capacity. If weighted AP is used, define weighting and sensitivity to extreme amounts.
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
| KS statistic | 100 × max(TPR - FPR) | Credit-industry descriptive bands only |

### Business KPI → Required ML Metric
```
If business sets approval rate target = 70%:
  State score direction first. For higher-is-riskier PD, approve the lowest-risk 70%;
  for higher-is-better credit score, approve the highest 70%.
  Report: default rate of approved (should be < target default rate)
  Do not report rejected-applicant default rate without identified outcomes or explicit assumptions.

If business sets loss rate target < 3%:
  Simulate the direction-correct policy and estimate interest/fee margin minus
  PD×LGD×EAD, funding, servicing, capital, acquisition, and policy costs.
  Compare Σ(PD×LGD×EAD) / portfolio exposure with the 3% loss-rate target;
  evaluate expected contribution separately.
```

### Domain-Specific ML Metrics for Credit
- **Gini = 2×AUC - 1** `[Industry]`: < 0.4 poor, 0.4–0.6 acceptable, > 0.6 good. Cutoffs are industry convention, not from Hosmer & Lemeshow — see `foundations/metric_interpretation.md`.
- **KS Statistic** `[Industry, no academic source for thresholds]`: < 20 weak, 20–40 acceptable, 40–60 good — banking practice, not textbook-derived.
- **PSI** `[Industry, not statistically justified]`: < 0.1 stable, > 0.25 major shift. Directional signal only, not a hard threshold — see `foundations/metric_interpretation.md`.
- **Approval rate vs default rate curve**: a policy-value view derived from ranked outcomes; it is not an ROC curve.
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
| Campaign ROI | (Incremental benefit - Campaign cost) / Campaign cost | > 0 profitable; > 1 is over 100% return |
| Intervention rate | Customers contacted / Total customers | Budget-constrained |

### Business KPI → Required ML Metric
```
Campaign budget = B contacts/month
LTV of saved customer = L
Intervention cost = C per contact
Conditional save probability among true at-risk customers = s

Break-even precision:
  P_breakeven = C / (L × s)
  e.g., L=$500, C=$10, s=30% → P_breakeven = $10/($500×0.3) = 6.7%
  Predictive precision alone does not establish ROI; without identified incremental
  retention, report scenario bounds rather than a profitability verdict.

Required incremental saves:
  Incremental saves / would-be churners must exceed X%.
  Only under a stated homogeneous conditional save rate s may this be approximated
  by predictive recall × s.
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
- A well-powered, correctly randomized online experiment is primary causal evidence for
  its specified horizon. Validate sample-ratio balance, logging, carryover, uncertainty,
  and guardrails before overriding offline evidence.

---

## Domain: Demand Forecasting / Operations

### Business KPIs
| Business KPI | Definition | Typical Target |
|---|---|---|
| Stockout rate | Stockouts / Total SKUs | < 2–5% |
| Overstock cost | Holding cost of excess inventory | Minimize |
| Fill rate | Orders fulfilled / Orders placed | > 95–99% |
| Forecast bias | Mean(predicted - actual), optionally scaled with a zero guard | Cost-appropriate target |

### Business KPI → Required ML Metric
```
Asymmetric cost: stockout cost ≠ overstock cost
  Choose quantile tau from the underage/overage cost ratio, not an arbitrary value.
  If costs are symmetric: use median regression (MAE-optimal)

Required MASE (Mean Absolute Scaled Error):
  MASE scales test error by an in-sample training naive scale.
  Directly evaluate the seasonal-naive forecast on the same test rows before claiming
  out-of-sample superiority; no verified threshold defines "good enough."
```

### Domain-Specific ML Metrics for Forecasting
- **MASE**: Compare to naive baseline, not absolute MAE
- **SMAPE**: bounded when only one value is zero, but requires an explicit both-zero convention and remains unstable near zero
- **Bias**: report systematic over/under-prediction; cost-optimal forecasts may be intentionally biased under asymmetric loss.
- **Quantile loss**: for intervals, estimate lower/upper quantiles and report empirical coverage and width.
- Never use: R² (misleading for time series), MAPE (explodes near zero)

---

## Quick Reference: Business KPI to ML Metric

| Business KPI | ML Metric to Report | Secondary Metric |
|---|---|---|
| Fraud loss reduction | Expected net value@capacity, count AP | Precision@review_capacity |
| Credit default rate | Gini (=2×AUC-1), KS stat | Default rate by score decile |
| Churn revenue retention | Precision@budget, Revenue-weighted recall | Uplift vs no-model |
| Campaign ROI | Precision@k where k=budget | Break-even precision |
| CTR / Conversion | NDCG@k (k=visible slots) | Valid randomized online experiment |
| Revenue per session | Revenue@k | Coverage, diversity |
| Inventory fill rate | MASE, Bias | Quantile accuracy |
| Queue SLA compliance | Precision@capacity | Throughput vs capacity |

---

## Red Flags in Business-ML Alignment

- **Model metric improving but business KPI flat**: model optimizes wrong thing — re-check objective alignment
- **Business KPI improving but model metric flat**: model may not be causal — check for confounders
- **High offline metric, failed A/B test**: distribution shift, feedback loop not modeled, or metric doesn't capture what matters
- **Business sets ML metric target directly** (e.g., "we need AUC > 0.85"): ask WHY — trace back to business KPI, the AUC target may be wrong
