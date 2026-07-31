# Domain: Credit Scoring

Credit scoring is usually **scorecard mode** (WoE + logistic), in a **regulated**
setting. That changes several phases relative to the generic backbone.

---

## Label definition is unusually load-bearing

Credit labels are defined by a **performance definition** that must be pinned down
*before* any feature work:
- **Bad definition**: e.g. "90+ days past due within 12 months of observation".
- **Performance/outcome window**: the horizon over which "bad" is observed — **derive
  it, don't assume it.** Justify the window with **roll-rate analysis** (how often
  early delinquency rolls forward to "bad") and **vintage / bad-rate maturation**
  (plot cumulative bad rate vs months-on-book; the window is where the curve flattens).
  A "12 months" stated without this analysis will be challenged in validation.
- **Class taxonomy**: define **good / bad / indeterminate / excluded** as distinct
  groups. Exclusions (inactive, fraud, deceased, policy declines) are not "good".
- **Indeterminate accounts** (e.g. 30–60 DPD, neither clearly good nor bad): typically
  **excluded from model *fitting*** but **still scored and monitored** in production.
  Excluding them inflates apparent separation and changes the bad-rate denominator and
  the **population odds** the scorecard is calibrated to. Define the calibration
  population and estimand explicitly; use sufficiently matured, observed outcomes and
  document any censoring/selection adjustment or sensitivity bounds. Do not manufacture
  full-population odds by assigning unresolved indeterminates to good or bad.

Every leakage/tautology check (Phase 6) keys off this definition. A feature that uses
realized delinquency, collections, or charge-off from the label window is tautological
or leaky; historically available pre-cutoff measurements can be valid predictors. See
`references/leakage_and_tautology.md`.

---

## Scorecard mode consequences

- **Monotonic binning is a common governance default, not a universal legal rule.**
  Apply it when institutional policy or domain reasoning requires it. Document approved
  exceptions for defensible non-monotonic relationships. See the binning section in
  `references/predictive_power.md`.
- **Low redundancy tolerance.** Multicollinearity can destabilize logistic coefficients
  and reason codes. Apply governance-selected diagnostics and thresholds to the
  train-fitted WoE matrix (`references/redundancy_and_lift.md`).
- **No native NaN.** Bin missing into its own WoE group; never silent mean-impute
  (`references/null_handling.md`).
- **Reason codes / adverse action (US credit subject to ECOA/Reg B).** Reg B requires the *specific principal reasons*
  for a denial. With a WoE scorecard these are derived mechanically from
  **points-below-max (points lost) per characteristic** — the characteristics where
  the applicant scored furthest below a defined reference point. **The reference point
  matters**: "points below *max attainable*" vs "points below *neutral/mean*" surface
  *different* reasons, and max-based methods have been challenged for citing
  characteristics where the applicant is actually near-typical. Pick and document the
  method. Plain-language explainability is necessary but **not sufficient**: every
  characteristic must map to a defensible, compliant adverse-action reason, or a
  monotone "explainable" feature can still produce misleading reason codes. A feature
  whose points-lost cannot be phrased as a lawful reason is unusable regardless of IV.

---

## Fairness / protected-attribute proxy check — mandatory

In lending this is a mandatory governance handoff, not a self-service legal conclusion.
A feature may be a **proxy**
for a protected class (race, sex, age, national origin) even if the attribute itself
is never used.

- Permitted demographic data, proxy methods, comparison groups, and tests depend on
  jurisdiction, product, purpose, and governance controls. Fair-lending analysis may
  use proxy estimation such as BISG, but proxy error and lawful-use constraints must be
  included in the review.
- Evaluate disparities in decisions, pricing/limits, scores/errors, and adverse-action
  reasons using methods approved by qualified compliance/model-risk owners, with
  uncertainty and proxy-error sensitivity. Do not treat the employment-derived
  four-fifths rule as a universal fair-lending test or safe harbor. During feature
  design, **flag obvious proxies** such as
  geography (ZIP is a classic redlining proxy), certain merchant categories,
  name/language-derived signals.
- Record any proxy-risk feature, permitted-data basis, business justification, required
  less-discriminatory-alternative review, named approver, and `PASS/NO-GO/BLOCKED`
  status. Unavailable lawful analysis cannot silently pass.

---

## Reject inference (note)

Models are trained on **booked** accounts (applicants who were approved and have a
performance outcome). Rejected applicants have no label → **selection bias**: your
feature signal is measured only on the approved population, which is non-random.

- The bias is not only in per-feature IV: **the entire scorecard** (bins, WoE,
  coefficients, *and the calibration to population odds*) is fit on the accepted book,
  so through-the-door performance is genuinely unknown. Reject inference, or an
  explicitly documented decision to skip it, may be required by local governance.
  Quantify observable booked-versus-applicant covariate and score shifts; do not claim
  through-the-door bad-rate identification without outcomes or additional assumptions.
- At feature-onboarding time, IV/lift are computed on an **already-filtered**
  population. This does not merely *bound* generalizability — for a feature affected by
  the prior approval policy, its signal **can in principle reverse sign** on the
  through-the-door population (a Simpson's-paradox-type effect when the prior cutoff
  conditioned strongly on a correlate of the feature). This is a conditional risk to
  check, not a routine outcome — but it means booked-only IV must be explicitly
  caveated, not treated as the population truth.
- Full reject inference (reweighting / fuzzy augmentation / bureau-score-based
  parceling) is a modeling-stage topic and is itself regarded with some regulatory
  skepticism for its instability — but you must **document that selection bias is
  present** and that every IV number reported here is conditional on the booked book.

---

## Phase deltas summary

| Phase | Credit-scoring adjustment |
|---|---|
| 1 | Pin down the performance definition + outcome window + indeterminate handling |
| 4 | WoE is the native representation; apply the declared monotonicity policy and approved exceptions |
| 5 | Apply governance-selected WoE-matrix redundancy criteria; reason-code explainability is a hard filter where applicable |
| 6 | Anything touching delinquency in the performance window = leak/tautology |
| 8 | PSI is a regulatory monitoring artifact, not just a dev check |
| 9 | Add fairness/proxy screen and explainability to drop criteria |
