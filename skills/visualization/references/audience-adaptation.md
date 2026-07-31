# Audience Adaptation: One Analysis → Multiple Deliverables

When the same model result, analysis, or finding must be communicated to different audience tiers,
do not duplicate the work — adapt the framing, depth, and chart type from a single source.

---

## The Core Rule

**Data is the same. Story, depth, and chart type change per audience.**

Never prepare two independent analyses. Prepare one rigorous analysis (Practitioner level),
then derive the other tiers from it by stripping, reframing, and re-titling.

---

## Adaptation Workflow

### Step 1 — Start at Practitioner level
Build the full technical version first:
- All relevant metrics with baselines
- Diagnostic charts (KS curve, calibration, SHAP, PSI)
- Honest limitations and caveats

### Step 2 — Derive Risk Committee version
From the Practitioner version:
- Keep: discrimination chart (KS or ROC), stability chart (PSI), headline metrics
- Add: business KPI translation (Gini → expected default rate at current cutoff)
- Remove: SHAP waterfall, confusion matrix, raw feature lists
- Title: state the validation conclusion ("Model discrimination adequate; PSI stable at 0.08")

### Step 3 — Derive Executive version
From the Risk Committee version:
- Keep: one chart maximum (KPI vs. target, or single headline metric)
- Convert: all ML metrics → business numbers ($ saved, % reduction, approval rate impact)
- Remove: all ML metric names — replace with business language
- Title: state the business action ("Model approved for production — expected 12% reduction in loss rate")

Simplify terminology, not evidence. Every tier retains the decision threshold,
uncertainty/range, material limitations, affected populations, and adverse subgroup
effects. Translate ML metrics to business outcomes only through an explicit, documented
impact model; do not imply that Gini or NDCG directly causes a business result.

---

## Domain Examples: Same KS = 0.42 Result

| Audience | Chart | Title |
|---|---|---|
| Practitioner | KS curve + score distribution overlay | "KS = 0.42 — acceptable discrimination; top 2 deciles capture 58% of bads" |
| Risk Committee | KS summary + PSI bar | "Model meets validation threshold (KS > 0.35); score distribution stable over 6 months" |
| Executive | Bullet chart: approval rate vs. default rate | "Credit model maintains 2.1% default rate at 68% approval — within risk appetite" |

---

## Common Mistakes

| Mistake | Problem | Fix |
|---|---|---|
| Sending Practitioner output to Executive | Confuses, loses credibility | Use one decision-focused chart while retaining uncertainty and limitations |
| Sending Executive output to Risk Committee | Insufficient — will be sent back | Always include discrimination + stability charts |
| Different data in different tier decks | Auditability failure in regulated context | Single source of truth; tiers share data, differ in framing only |
| Using ML metric names (AUC, NDCG) in Executive deck | Audience doesn't know what they mean | Translate every ML metric to a business outcome before the Executive slide |

---

## Quick Reference: What Each Tier Needs

| Tier | Max Charts | Metric Language | What They Decide |
|---|---|---|---|
| Executive | 1 | Business KPIs only | Go/no-go, budget, priority |
| Risk/Model Committee | 3–5 | ML metrics + business translation | Approve for production, set monitoring thresholds |
| Regulator/Auditor | As needed | Full methodology documentation | Compliance sign-off |
| Practitioner | No limit | Full technical detail | Root cause, next experiment, model changes |
