# General Diagnostic Patterns

## How to Use These Patterns

Each pattern provides a signal, compatible hypotheses, and discriminating checks. A
metric pattern does not establish a root cause. Report a causal conclusion only after a
check rules out credible alternatives.

Use the relevant domain overlay only for domain-specific symptoms.

## Pattern 1: ROC AUC and Average Precision Diverge

**Signal:** ROC AUC improves, but average-precision lift or precision at the operating
point misses its requirement.

**Compatible hypotheses:** the gain lies outside the decision region, false-positive
burden dominates at deployment prevalence, positive support is small, or score ties and
candidate construction affect average precision.

**Discriminating checks:** report prevalence, paired intervals, partial ROC in the
decision region, precision-recall behavior, and precision/recall at the frozen policy.
Do not switch metrics solely because prevalence crosses a fixed cutoff.

## Pattern 2: Training, Validation, and Test Diverge

**Signal:** training performance exceeds validation performance, or validation
performance drops sharply on a later test set.

**Compatible hypotheses:** model-selection optimism, insufficient regularization,
population or temporal shift, duplicate/entity overlap, label maturation, preprocessing
differences, or sampling variation.

**Discriminating checks:** replay one frozen pipeline, audit split and point-in-time
semantics, compare population and label processes, use learning curves, and estimate
paired differences at the independent unit. Choose time, entity, scene, or random splits
from the deployment estimand rather than applying one split rule universally.

## Pattern 3: Offline Improvement, Online Effect Unresolved

**Signal:** offline ranking or classification improves while a valid online estimate is
flat or uncertain.

**Compatible hypotheses:** the online test is underpowered, the offline metric targets a
different estimand, historical exposure creates policy bias, implementation differs, or
the intervention does not change outcomes.

**Discriminating checks:** compare the online paired interval with zero and the
predeclared useful margin, validate experiment assignment and exposure, replay served
predictions, and test policy-aware offline estimates against randomized evidence.

## Pattern 4: No Acceptable Operating Point

**Signal:** no evaluated threshold or capacity produces the required precision-recall or
cost trade-off.

**Compatible hypotheses:** weak signal, noisy or mismatched labels, insufficient support,
an infeasible requirement, or a training objective that does not preserve the intended
estimand.

**Discriminating checks:** compare simple multivariate baselines, audit labels, inspect
learning curves and uncertainty, and evaluate the complete policy at the declared
capacity. Do not prescribe retraining until the checks distinguish these hypotheses.

## Pattern 5: High Precision, Low Recall

**Signal:** a selective threshold yields high precision and low recall.

**Compatible hypotheses:** intentional capacity control, asymmetric costs, an unjustified
default threshold, or calibration error when probability magnitudes drive decisions.

**Discriminating checks:** derive the policy from costs/capacity, evaluate missed-positive
impact, and assess calibration on untouched data. High precision and low recall is not a
defect by itself.

## Pattern 6: Statistical Gain, Decision Requirement Missed

**Signal:** the model beats a baseline statistically, but the frozen operating policy
does not meet capacity, harm, or value requirements.

**Compatible hypotheses:** improvement occurs outside the actionable region, action costs
or effects differ from assumptions, or the metric is not aligned with the decision.

**Discriminating checks:** evaluate the exact policy, propagate uncertainty in costs and
action effects, and separate predictive value from incremental causal value.

## Pattern 7: Aggregate and Critical Segments Disagree

**Signal:** aggregate performance improves while a predeclared critical segment degrades.

**Compatible hypotheses:** mixture weighting, support imbalance, heterogeneous dynamics,
or a changed segment definition.

**Discriminating checks:** report segment support and paired intervals, micro/macro or
deployment-weighted aggregation, and multiplicity treatment. A segment-specific model or
weighted loss is an option only after heterogeneity is demonstrated.

## Pattern 8: Metrics Are Suspiciously High

**Signal:** performance is implausibly high or unusually stable across development and
test data.

**Compatible hypotheses:** target-derived features, future information, duplicate/entity
overlap, label proxies, benchmark contamination, or genuinely strong signal.

**Discriminating checks:** rebuild point-in-time features, audit provenance and overlap,
remove suspect features, run shuffled-target pipeline tests, and repeat on an independent
cohort. The `feature-onboarding` skill can assist with feature admissibility; this skill
does not depend on its internal file layout.

## Pattern 9: Recent Labels Are Immature

**Signal:** recent cohorts have unusually low observed event rates that change as the
outcome window matures.

**Compatible hypotheses:** administrative censoring, action-dependent observation,
delayed confirmation, or changed denominators.

**Discriminating checks:** define the horizon and label cutoff, distinguish unresolved
from confirmed-negative outcomes, track fixed cohorts, and use survival or censoring
methods only when their assumptions are defensible.

## Investigation Priority

1. Validate metric implementation, split, point-in-time data, labels, and matching.
2. Validate comparable populations, policies, and support.
3. Evaluate the frozen operating policy and uncertainty.
4. Investigate domain-specific hypotheses.
5. Translate to economic or causal value only when the decision requires it.

When several patterns fit, report all credible hypotheses and choose the next check by
expected information gain and risk, not by an unsupported likelihood ranking.
