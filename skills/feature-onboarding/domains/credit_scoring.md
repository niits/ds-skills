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
  the **population odds** the scorecard is calibrated to. **Calibrate to the actual
  portfolio odds** (full population, with an explicit treatment for indeterminates), not
  the fit-sample odds — document the adjustment, don't drop them silently.

Every leakage/tautology check (Phase 6) keys off this definition. A feature that
touches delinquency/collections/charge-off in or near the performance window is
tautological or leaky. See `references/leakage_and_tautology.md`.

---

## Scorecard mode consequences

- **Monotonic binning is required.** Features enter as WoE and regulators expect a
  monotone risk relationship. Non-monotone raw features must bin into a monotone WoE
  transform or be dropped. See the monotonic-binning section in
  `references/predictive_power.md`.
- **Low redundancy tolerance.** Multicollinearity destabilizes logistic coefficients
  and breaks reason codes. Be strict: VIF < 5, drop one of any high-`|r|` pair
  (`references/redundancy_and_lift.md`).
- **No native NaN.** Bin missing into its own WoE group; never silent mean-impute
  (`references/null_handling.md`).
- **Reason codes / adverse action.** Reg B requires the *specific principal reasons*
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

In lending this is a **legal requirement**, not a nicety. A feature may be a **proxy**
for a protected class (race, sex, age, national origin) even if the attribute itself
is never used.

- **You usually cannot collect the protected attribute.** In US non-mortgage credit,
  ECOA/Reg B generally **prohibits collecting** race/ethnicity, so you can't simply
  correlate features against it. Fair-lending analysis uses **proxy estimation**
  (e.g. **BISG** — Bayesian Improved Surname Geocoding) to impute group membership for
  testing. (Exceptions where demographics *are* collected: mortgage under HMDA, and
  small-business lending under the CFPB **1071** rule.) Correct the instinct to "just
  measure correlation with the protected attribute"; for most consumer credit you can't.
- **Disparate-impact testing is on outcomes/scores**, not just feature correlations,
  and the two standard artifacts measure *different* things: the **adverse-impact ratio
  / four-fifths (80%) rule** is computed on the **approve/decline decision at the chosen
  cutoff**, while **standardized mean differences (SMD)** are a *continuous-score*
  supplement (no cutoff). Don't conflate them. (BISG itself is contested for accuracy,
  so any LDA conclusion that rides on it inherits that uncertainty — caveat it.) This
  belongs in model validation, but **flag obvious proxies at feature design** —
  geography (ZIP is a classic redlining proxy), certain merchant categories,
  name/language-derived signals.
- **Less-discriminatory-alternative (LDA) search** is now an expectation, not a
  footnote: if a feature drives disparity, you must show no reasonably-available,
  similarly-predictive alternative exists. Document any proxy-risk feature with its
  business-necessity justification and the LDA analysis.

---

## Reject inference (note)

Models are trained on **booked** accounts (applicants who were approved and have a
performance outcome). Rejected applicants have no label → **selection bias**: your
feature signal is measured only on the approved population, which is non-random.

- The bias is not only in per-feature IV: **the entire scorecard** (bins, WoE,
  coefficients, *and the calibration to population odds*) is fit on the accepted book,
  so through-the-door performance is genuinely unknown. Under MRM, reject inference —
  **or an explicitly documented decision to skip it** — is a *development requirement*,
  not an afterthought, and the **booked-vs-through-the-door population-odds gap must be
  quantified**, not merely acknowledged.
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
| 4 | WoE is the native representation, not just a screen; enforce monotonic bins |
| 5 | Strict redundancy (VIF < 5); reason-code explainability is a hard filter |
| 6 | Anything touching delinquency in the performance window = leak/tautology |
| 8 | PSI is a regulatory monitoring artifact, not just a dev check |
| 9 | Add fairness/proxy screen and explainability to drop criteria |
