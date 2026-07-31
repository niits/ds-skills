# Domain Guide: Fraud Detection

## What Fraud Detection Is Actually Solving

Fraud models rank transactions/accounts by risk so a review queue or auto-block rule can act.
KPIs, business-target formulas, and standard metrics (KS, dollar-weighted AP, Precision@k) are in
`business/kpi_mapping.md` — this file covers what that summary doesn't: label timing and adversarial dynamics.

---

## Label Maturation Lag — Read This First

Fraud outcomes (chargebacks, confirmed fraud reports) take **60–120 days** to post, depending on
card network and dispute window. A transaction from last week is not yet reliably labeled.

**Consequence**: any eval cohort younger than the maturation window has unresolved,
censored outcomes. Delayed positives lower confirmed prevalence, but metric bias can
move either way when delay depends on score, channel, amount, or model action. Do not
use immature-cohort precision/recall for a final comparison.

**Fix** (see Pattern 7.2 in `diagnosis/patterns.md`):
- Exclude transactions younger than the maturation window from evaluation, or
- Report a "confirmed-so-far rate" as a lower bound only with a fixed denominator and
  monotone, non-revocable positive labels; otherwise call it an immature partial rate, and
- Use vintage analysis (track a fixed cohort's confirmed-fraud rate over time) instead of a rolling snapshot

This is the fraud analog of churn's "immortal cohort" problem (`domains/churn_prediction.md`).

---

## Adversarial Drift — Different From Ordinary Distribution Shift

Churn and lead-scoring drift is organic (market/product changes). Fraud drift can be **adversarial**:
fraudsters actively probe the current model and adapt to what gets blocked.

- Standard PSI/retraining playbooks assume passive drift and will lag a moving adversary
- Segment PSI by channel/attack vector, not just aggregate — adversarial shift is usually concentrated, not uniform
- Consider a faster retraining cadence for fraud specifically than for organic-drift domains
- Before assuming "population changed" from a PSI spike, check whether loss is concentrated on a pattern absent from training (a new attack signature) — see Pattern 6.3 in `diagnosis/patterns.md`

---

## Evaluation Protocol

1. Time-based split — mandatory, same reasoning as churn/lead scoring
2. Exclude immature cohorts (see above) before computing any headline metric
3. Report count AP and define any weighted AP explicitly; sensitivity-test extreme amounts
4. Compute Precision@k at k = daily analyst review capacity
5. Compute expected net value@k using preventability/recovery, all review/action costs, and legitimate-customer friction
6. Segment by channel/merchant category with support and uncertainty

## Common Failure Modes

| Symptom | Diagnosis | Action |
|---|---|---|
| Metrics look strong, degrade every re-measurement | Immature labels (Pattern 7.2) | Exclude recent cohort, use vintage analysis |
| PSI rising, retrained model still losing ground | Adversarial adaptation is one hypothesis | Check attack vectors, matured outcomes, policy/logging changes, and alternative drift causes before attribution |
| High AUC-ROC, weak Precision@k | Wrong metric for < 1% positive rate | Switch to AP / dollar-weighted AP |
| Model flags concentrate on one merchant category | Feature captures merchant profile, not fraud behavior | Ablate merchant features, check lift within category |
