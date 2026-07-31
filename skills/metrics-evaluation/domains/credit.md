# Domain Guide: Credit Risk / Lending

## What Credit Scoring Is Actually Solving

Credit models rank applicants or accounts by default risk to drive an approve/decline or pricing
decision. KPIs, business-target formulas, and standard metrics (Gini, KS, PSI) are in
`business/kpi_mapping.md` — this file covers what that summary doesn't: label timing and selection bias.

Declare score direction: PD normally means higher is riskier; traditional credit points
often mean higher is better. Every cutoff and percentile statement must follow that direction.

---

## Label Maturation Lag

A loan isn't confirmed "good" or "bad" until it has had time to default — typically defined as
90+ days past due within a fixed observation window (e.g., 12 or 24 months on book). A recent
vintage (loans originated in the last few months) has not had that time.

**Consequence**: evaluating on a recent vintage understates the true default rate — accounts that
will eventually default are still counted as "good" because they haven't hit 90 DPD yet. This is the
credit analog of churn's "immortal cohort" problem and fraud's chargeback lag.

**Fix** (see Pattern 7.2 in `diagnosis/patterns.md`):
- Only evaluate vintages that have completed the full observation window
- Use vintage analysis (default rate by months-on-book, per origination cohort) instead of a single snapshot
- If a recent vintage must be reported, label it explicitly as "immature — rate will rise"

---

## Reject Inference — The Structural Selection Bias

Training data only contains outcomes for **approved** applicants. Declined applicants never get a
loan, so you never observe whether they would have defaulted. This is the credit analog of lead
scoring's label bias (`domains/lead_scoring.md`): a model trained only on approved accounts learns
the approved population, not the full applicant population, and may misestimate risk in
either direction if the approval policy changes.

- **Detection**: compare score distribution of approved applicants to the full applicant pool — if approval was score-gated, the training data is truncated
- Reject inference is assumption-dependent and does not recover declined outcomes by
  itself. Report approved-population performance and the policy support of observed data;
  state assumptions and sensitivity bounds for any parceling/augmentation.
- Any compliant exploration or external-outcome study requires affordability,
  fair-lending, consumer-harm, credit-policy, and governance approval.

---

## Evaluation Protocol

1. Time-based (vintage) split — mandatory
2. Exclude immature vintages before computing Gini/KS/default rate
3. Report Gini and KS, not raw AUC (stakeholders think in scorecard terms) — see `business/kpi_mapping.md`, "Never Report for Credit"
4. Validate matured OOT PD calibration by score band, vintage, product, and channel when probabilities drive decisions
5. At each policy, estimate expected contribution: interest/fee margin minus PD×LGD×EAD, funding, servicing, capital, acquisition, and policy costs
6. State reject-inference assumptions and support before extrapolating beyond the current approval policy

## Common Failure Modes

| Symptom | Diagnosis | Action |
|---|---|---|
| Gini/KS strong, real default rate rising | Mix shift, calibration drift, or concept drift | Check observed/expected default within score bands, vintages, products, and channels |
| Metrics good on recent vintage, worse historically | Immature vintage (Pattern 7.2) | Re-evaluate only on vintages with full observation window |
| Model very strong right at the old approval cutoff | Prior-policy selection may limit support | Report support and sensitivity; do not claim declined performance without identification |
| KS drops, Gini stable | Score distribution shape changed, not necessarily policy value | Re-evaluate calibrated expected contribution and constraints; do not move cutoff toward KS maximum |
