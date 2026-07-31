---
name: feature-onboarding
description: Use when onboarding a new feature group into a supervised lead- or credit-scoring pipeline and gating it against leakage, tautology, redundancy, and out-of-time drift before production. Covers hypothesis-first design, predictive screening, incremental lift, stability, implementation, and release.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: ds-skills
    domain: lead scoring / credit scoring
    primary-label-type: binary classification
---

# Feature Onboarding for Supervised ML

## Purpose

Move a justified feature group from source investigation to production while preventing
leakage, label reconstruction, redundant signal, train/serve skew, and temporal decay.
This skill supports lead and credit scoring. `domains/recsys_extension.md` is an
unsupported design roadmap.

High univariate IV never validates a feature. A feature must be hypothesized before
computation, add incremental validation lift, remain point-in-time safe, and survive a
single untouched out-of-time (OOT) confirmation.

## Workflow

Select **scorecard** or **GBM** mode before Phase 1 and follow
`references/model_mode.md`. A later mode change invalidates all mode-dependent results.

1. **Understand sources.** Verify grain, formulas, units, null semantics, time range,
   coverage, and lineage. Do not infer meaning from column names.
2. **Create the feature decision ledger.** Before computing, record each formula,
   verified semantics, hypothesis, grain/population, event and availability times,
   cutoff convention, null meaning, model mode, predeclared criteria, owner, and versions.
3. **Prototype eligible features.** Use development data and train-fitted artifacts;
   keep Spark work distributed and derive multiple outputs from one heavy aggregation.
4. **Screen predictive power.** Use IV/WoE only as a binary-target filter; follow
   `references/predictive_power.md` for thresholds and alternatives.
5. **Test redundancy and lift.** Use mode-appropriate multivariate diagnostics and
   paired baseline-versus-candidate evaluation on identical chronological folds.
   Follow `references/redundancy_and_lift.md`.
6. **Audit leakage and tautology.** Verify event/effective and recorded/available-time
   predicates in implemented lineage. Reject realized-label reconstruction. Follow
   `references/leakage_and_tautology.md`.
7. **Select lag horizons.** Use exact calendar/business periods and measured coverage,
   redundancy, and stable lift. Follow `references/lag_horizon_analysis.md`.
8. **Assess stability and OOT once.** Investigate drift, freeze the complete pipeline,
   then evaluate one untouched later window using `references/stability_and_oot.md`.
9. **Record the decision.** Apply predeclared evidence standards and
   `references/decision_gate.md`; do not tune from the inspected OOT result.
10. **Implement and integrate.** Build deterministic, reusable feature computation,
    establish offline/online parity, validate keys/schema/values, and define monitoring
    with `references/implementation_and_integration.md`.
11. **Clean up.** Move experiments, remove diagnostics from production paths, fix links,
    and summarize the change. Commit only when explicitly authorized.

## Hard Stops

- `BLOCKED`: source values cannot be reconstructed as knowable at each scoring cutoff.
- `NO-GO`: a feature uses future/restated-unavailable data or reconstructs the label.
- `NO-GO`: the frozen pipeline fails its untouched OOT confirmation.
- `BLOCKED`: train/serve parity, primary-key uniqueness, or finite-value integrity fails.
- Never choose features from the OOT result; revision requires a new future holdout.
- Never brute-force transformations and rationalize them afterward.
- Never conflate structural absence, unknown values, and missing history.

## References

- `references/model_mode.md` - scorecard/GBM consequences.
- `references/source_and_prototyping.md` - source audit, hypothesis ledger, Spark prototype.
- `references/predictive_power.md` - IV/WoE and non-binary alternatives.
- `references/redundancy_and_lift.md` - multivariate redundancy and incremental lift.
- `references/leakage_and_tautology.md` - temporal safety and label reconstruction.
- `references/lag_horizon_analysis.md` - exact-period lag selection.
- `references/stability_and_oot.md` - PSI, period stability, and OOT protocol.
- `references/null_handling.md` - mode-dependent missing-value treatment.
- `references/decision_gate.md` - Go/No-Go criteria and scalable tiering.
- `references/implementation_and_integration.md` - module, Feature Store, parity, DQ,
  reproducibility, and monitoring.
- `domains/credit_scoring.md`, `domains/lead_scoring.md` - domain constraints.
