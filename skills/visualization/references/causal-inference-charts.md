# Causal Inference Chart Patterns

Visualization patterns for communicating causal estimates and their assumptions.

## Core Principle: Assumptions are as important as estimates

Causal inference charts serve two distinct purposes:
1. **Communicating the estimate** — the treatment effect and its uncertainty
2. **Communicating the assumptions** — whether the identification strategy is credible

A chart that shows only the point estimate without uncertainty, or that presents
a DiD result without showing the parallel trends check, is incomplete regardless
of how statistically correct the underlying analysis is.

**The audience question is always:** "Should I believe this number?"
The chart must help them answer that question, not just show the number.

---

## 1. Coefficient Plot — Treatment Effect with Confidence Interval

**Use when:** Reporting a single treatment effect or comparing effects across
multiple specifications, subgroups, or model variants.
This is the standard output chart for any regression-based causal estimate.

**Audience:** Practitioners, management, committee

**Required inputs:**
- `estimates` — list of point estimates (one per row)
- `cis_95` — list of `(lower, upper)` tuples for 95% confidence intervals
- `cis_90` *(optional)* — list of `(lower, upper)` tuples for 90% CI (inner bar)
- `labels` — list of row label strings (specification name, subgroup name, etc.)
- `null_value` — reference line value (0 for difference estimates, 1 for ratio estimates)

**Key design decisions:**
- Forest plot convention: wider (lighter) bar = 95% CI; narrower (darker) bar = 90% CI
- Use neutral color for all estimates; reserve accent for a prespecified focal estimand,
  not whether an interval crosses the null. State multiplicity handling when relevant.
- Annotate each point estimate value to the right of its CI bar
- Add a vertical dashed reference line at the null value

---

## 2. Parallel Trends Check — DiD Pre-Treatment Overlay

**Use when:** Validating the parallel trends assumption for a
Difference-in-Differences (DiD) design. This is an assumption diagnostic,
not a result chart. Show it *before* the DiD estimate.

**Rule:** Never present a DiD result without first showing this chart.
The audience cannot evaluate credibility without seeing the pre-treatment trends.

**Audience:** Practitioners, committee, anyone evaluating the DiD methodology

**Required inputs:**
- `periods` — list of time periods (int or datetime)
- `treated_means` — outcome means for the treated group at each period
- `control_means` — outcome means for the control group at each period
- `treatment_period` — the period when treatment begins (used as the vertical divider)
- `treated_label`, `control_label` — group names for the legend
- group-period counts, weights, composition diagnostics, and uncertainty intervals

**Key design decisions:**
- Both lines in equal weight before the treatment divider (assumption check window)
- Accent the treated line post-treatment; mute the control line (dashed, lighter) to emphasize divergence
- Add a vertical divider at `treatment_period` with a label ("Treatment starts")
- Label the pre-treatment window as the assumption check region

**Reading the pre-treatment window:**
- Similar pre-trends are consistent with, but do not prove, parallel counterfactual trends
- Divergence is a warning that requires composition, specification, and design checks;
  visual pre-trends alone do not quantify bias
- A level difference is not itself fatal, but it does not establish parallel
  counterfactual trends; check composition stability and precision

---

## 3. DiD Event Study — Dynamic Treatment Effects

**Use when:** Estimating treatment effects for each period relative to treatment,
rather than a single post-treatment average. This is the modern standard for DiD.
Pre-period coefficients are diagnostics with limited power, not a formal proof of parallel trends.

**Audience:** Practitioners, committee

**Required inputs:**
- `periods_relative` — list of integers representing periods relative to treatment
  (e.g. `[-4, -3, -2, -1, 0, 1, 2, 3, 4]`; period −1 is typically the omitted reference period)
- `estimates` — DiD coefficient at each relative period
- `cis` — list of `(lower, upper)` 95% CI tuples for each period
- estimator valid for treatment-timing heterogeneity and a clustered/dependence-aware interval method

Exclude the omitted reference period from estimate/CI arrays, or plot it explicitly at
zero without a CI. Use simultaneous bands or a joint pre-trend test alongside pointwise intervals.

**Key design decisions:**
- Pre-period (t < 0): gray color with shaded CI band — these should be ≈ 0 if the parallel trends assumption holds
- Post-period (t ≥ 0): accent color with shaded CI band — these show the dynamic treatment effect
- Add a horizontal reference line at y = 0 and a vertical divider between pre and post
- Label the pre-treatment window ("should be ≈ 0") and post-treatment window ("treatment effect") directly on the chart

---

## 4. RDD Binned Scatter — Regression Discontinuity

**Use when:** Visualizing a Regression Discontinuity Design result.
Shows the relationship between the running variable and outcome near the cutoff. The
visual is a diagnostic companion to a design-based estimate, not the causal estimate itself.

**Why bin:** Raw scatter plots are noisy and obscure the discontinuity.
Binning choices affect appearance and must be reported with sensitivity checks.

**Audience:** Practitioners, committee

**Required inputs:**
- `running_var` — array of the running/forcing variable (e.g. credit score, income, age at cutoff)
- `outcome` — array of the outcome variable
- `cutoff` — the treatment threshold (scalar)
- transparent bin rule and sensitivity alternatives
- justified bandwidth for bias-corrected local-polynomial estimation on raw observations

**Key design decisions:**
- Show transparent bins for visualization and local-polynomial fits with robust 95% CIs
- Plot bin means as scatter points (control side = gray, treatment side = accent)
- Report bandwidth/functional-form sensitivity, density/manipulation checks, and
  predetermined-covariate continuity
- Add a vertical dashed line at the cutoff
- Annotate the estimated jump at the cutoff with an arrow and value

---

## 5. Propensity Score Overlap — Common Support Check

**Use when:** Validating that treated and control units share sufficient common support
before propensity score matching or IPW estimation.
Lack of overlap means the causal estimate relies on extrapolation, not comparison.

**Audience:** Practitioners, committee

**Required inputs:**
- `ps_treated` — array of propensity scores for treated units (values 0–1)
- `ps_control` — array of propensity scores for control units (values 0–1)

**Key design decisions:**
- Mirrored normalized/weighted densities with common bins; show raw group sizes separately
- Use the same bin edges (0 to 1 in equal steps) for both groups so the distributions are visually comparable
- Shade the common support region (overlap between the two distributions) in a distinct color
- Report target population, effective sample size, extreme weights, and trimming rules
- Good overlap = wide common support; poor overlap = one distribution concentrated at extremes with no counterpart
- Overlap is necessary for the stated population but does not establish no unmeasured confounding

---

## 6. IV First-Stage Diagnostic

**Use when:** Validating instrument strength/relevance before presenting a 2SLS or IV
estimate. This is an assumption diagnostic — show it before the main estimate, the same
way a DiD chart leads with parallel trends and an RDD chart leads with a density/continuity
check.

**Audience:** Practitioners, committee

**Required inputs:**
- `instrument` — array of the instrument variable
- `endogenous_regressor` — array of the endogenous regressor the instrument predicts
- `first_stage_f_stat` — the first-stage F-statistic (scalar)
- `first_stage_coefficient` — the first-stage coefficient estimate, with CI
- a stated weak-instrument threshold (e.g. the Staiger-Stock F > 10 rule-of-thumb, or the
  relevant Stock-Yogo critical value for the number of instruments/endogenous regressors) —
  state your policy's chosen value explicitly, the same caveat this skill uses elsewhere for
  PSI-style thresholds; there is no universal cutoff that fits every setting

**Key design decisions:**
- Bar or scatter of instrument vs. endogenous regressor, with the first-stage F-statistic
  annotated directly on the chart (not buried in a caption)
- Visually flag when F falls below the stated weak-instrument threshold (e.g. accent color
  or a reference line at the threshold)
- Report the first-stage coefficient with its CI alongside the F-statistic — a large F with
  a near-zero coefficient is still a weak/uninformative first stage in practice
- This chart can only speak to instrument relevance (the first-stage relationship). It
  cannot verify the exclusion restriction — state that as a caveat, since a strong first
  stage does not make the instrument valid

---

## Presentation Order for Causal Results

The order of charts matters. Audiences interpret results differently depending
on whether they see the assumptions first.

**Recommended sequence:**

```
1. Identify the causal question clearly (Big Idea + context)
   "Did [intervention X] cause [outcome Y] to change?"

2. Show the identification strategy
   "We use [DiD / RDD / PSM / IV] because [reason]"

3. Show the assumption check BEFORE the estimate
   DiD  → parallel trends chart (pre-treatment window)
   RDD  → binned scatter continuity + density test
   PSM  → propensity overlap chart
   IV   → first-stage F-statistic + relevance test

4. Show the main estimate with CI
   Coefficient plot: point estimate + 95% CI + 90% CI

5. Show robustness / heterogeneity
   Event study (DiD) or subgroup coefficient plot

6. State the conclusion as a Big Idea
   If identification assumptions are defensible: "The estimated effect is [X]
   (95% CI: [lo, hi]) under [design/assumptions]." Otherwise describe the association.
```

---

## Common Causal Inference Chart Mistakes

| Mistake | Problem | Fix |
|---|---|---|
| Point estimate without CI | Implies false precision | Always show confidence interval |
| DiD result without parallel trends check | Audience cannot assess credibility | Show pre-trends first |
| RDD shown only as arbitrary bins | Appearance can manufacture a jump | Pair transparent bins with robust local-polynomial inference and sensitivity checks |
| PSM result without overlap check | Estimate may rely on extrapolation | Show overlap before showing effect |
| "Significant at p < 0.05" as the main message | Conflates statistical and practical significance | State effect size + CI; let audience judge |
| Effect plot sorted by point estimate | Makes all estimates look real | Sort by theory or natural order; show CIs |
