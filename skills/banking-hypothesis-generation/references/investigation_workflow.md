# Banking Hypothesis Investigation Workflow

## Scope the Phenomenon

Record:

- Metric name and values before and after the change.
- Product, segment, channel, and affected population.
- Origination/observation window and outcome-performance window.
- Data as-of date and available investigation sources.
- Whether the issue appears systemic or product-specific, and whether data, features,
  population, policy, or model behavior could explain it.

Do not proceed until the observation is concrete enough to falsify an explanation.

## Gather and Synthesize Evidence

Check internal sources first:

| Source | Evidence sought |
|---|---|
| Model monitoring and PSI/CSI reports | Score and population drift |
| Vintage reports | Recent versus historical performance |
| Feature importance or SHAP logs | Inputs associated with score changes |
| Data-quality reports | Coverage, missingness, and source changes |
| Origination/collection strategy changes | Policy, cutoff, and channel shifts |
| Model inventory and validation reports | Known limitations and prior incidents |
| Macro data | Plausible systematic risk changes |

Summarize the proximate evidence, mechanisms that could produce it, unexplained
patterns, and comparable prior incidents. Internal evidence may be the sole evidence
base for proprietary behavior; document that choice.

## Prioritize Candidates

Rank candidates before spending experiment capacity:

| Criterion | Question |
|---|---|
| Expected impact | If true, how much could it move the decision metric? |
| Test cost | What data, compute, and elapsed time are required? |
| Existing signal | Can current monitoring already confirm or reject it? |
| Reversibility | What is the cost of acting if it is false? |

Reject candidates already contradicted by existing evidence. Prefer cheap,
discriminating checks before full experiments.

## Generate Competing Mechanisms

Use 2-4 hypotheses for a normal sprint and 1-2 for an urgent incident. Common families:

- **Population drift:** channel mix, policy shifts, product launches, macro changes.
- **Feature/data quality:** changed definitions, coverage, restatements, imputation.
- **Model behavior:** miscalibration, vintage overfit, underrepresented segments.
- **Business process:** collections or approval changes, selection effects, feedback loops.

Each hypothesis must state a mechanism, evidence, falsification condition, and a test
that separates it from alternatives.

## Form Predictions

For each hypothesis specify:

- Direction and expected magnitude.
- Population or segment where the effect should appear.
- Evaluation window.
- Outcome that rejects the hypothesis.

Example separation logic:

- Population drift predicts within-segment performance remains stable after segmenting.
- A feature-quality failure predicts degradation concentrated where that feature changed.
- Vintage overfit predicts degradation on newer vintages while historical vintages remain stable.
