# Hypothesis Quality Criteria — Banking Domain

## Framework for Evaluating Hypotheses in Banking DS

Use these criteria to assess each hypothesis before committing sprint resources to testing it. A weak hypothesis that passes evaluation will waste investigation time and potentially lead to wrong production decisions.

**How to use:** Score each hypothesis on all 7 criteria. No hypothesis needs to be perfect, but any hypothesis scoring "weak" on Testability or Falsifiability should be rewritten before proceeding.

---

## Core Criteria

### 1. Testability

**Definition:** The hypothesis can be evaluated with available banking data and tooling within the sprint timeline.

**Evaluation questions:**
- Is there a holdout set, backtesting window, or champion-challenger split available?
- Is the outcome observable within the sprint (or do we need to wait 12+ months for defaults to emerge)?
- Can the test be run in Databricks with available features and labels?
- Is there enough sample size in the target segment for statistical significance?

**Strong testability — banking examples:**
- "Adding transaction velocity features improves precision@100 on the holdout fraud dataset" → test offline in hours
- "PSI drops below 0.10 when mortgage scorecard is segmented by LTV band" → test with monitoring data in days
- "Removing CB_INQUIRY_6M does not change KS on new-to-credit applicants" → ablation test on existing holdout

**Weak testability — banking examples:**
- "This feature will improve long-run default prediction" — 'long-run' is undefined; no data to test within sprint
- "Customers with high CLV will respond better to this offer" — CLV not calculated, no outcome label available
- "The model is biased against small businesses" — 'biased' is vague; specify metric and threshold first

**Proxy testability:** When direct outcomes are unavailable (e.g., defaults need 12+ months), test on a proxy:
- Use early delinquency (30+ DPD at 3 months) as proxy for 12-month default
- Use click-through rate as proxy for offer acceptance in absence of revenue data
- Document proxy and its known limitations in the hypothesis block

---

### 2. Falsifiability

**Definition:** Clear metric thresholds or observable outcomes would disprove the hypothesis. Avoid built-in escape clauses.

**Evaluation questions:**
- What specific metric outcome rejects this hypothesis? (state the number)
- Is the falsification condition stated before running the test, not after seeing results?
- Would a null result meaningfully close this investigation path?

**Strong falsifiability — banking examples:**
- "KS improves by ≥3 points on 6-month holdout. If KS improvement < 1 point, H1 is rejected."
- "PSI drops below 0.10 after LTV segmentation. If PSI remains ≥0.15 in all bands, population drift is not the explanation."
- "Bureau field missing rate exceeds 30% in failing vintages. If missing rate is below 15%, data quality is not the cause."

**Weak falsifiability — banking examples:**
- "The model may perform better with more features" — no threshold; cannot be rejected
- "Population shift could be contributing to the issue" — 'could be' is unfalsifiable
- "Feature X might be important in some segments" — no prediction to test against

**The pre-registration rule:** Write the falsification condition before running any test. If you define "success" after seeing results, you are post-hoc rationalizing, not testing.

---

### 3. Parsimony

**Definition:** Prefer the simplest mechanism that explains the observation. In banking DS, this means following the investigation priority order.

**Banking investigation priority order (simplest first):**

1. **Data quality / upstream system issue** — missing values, imputation change, source field definition change, ETL bug
2. **Population composition shift** — new channel, policy change, macro event changing applicant mix
3. **Label/outcome definition change** — DPD threshold moved, write-off policy changed, observation window shifted
4. **Feature distribution shift** — input feature drifting without model change (check CSI before PSI)
5. **Model overfitting / generalization failure** — training vintage not representative of current population
6. **Fundamental behavioral change** — genuine change in how customers behave (require macro evidence)

**Parsimony rule:** Do not propose model redesign (step 5–6) before ruling out steps 1–3. A data quality issue masquerading as model degradation is the most common root cause.

**Over-complex hypotheses to avoid:**
- "The model needs retraining because customer behavior has fundamentally changed due to post-pandemic spending normalization and rate sensitivity" → check data quality first
- "We need a new deep learning architecture to capture non-linear interactions" → check if existing features are drifting first

---

### 4. Explanatory Power

**Definition:** The hypothesis accounts for the observed magnitude and pattern of the phenomenon, not just its direction.

**Evaluation questions:**
- If this mechanism is true, does it explain the full size of the observed change? (e.g., does it explain all 8 KS points of degradation, or only 3?)
- Does it explain why some segments are affected but others are not?
- Does it account for the timing? (Why did it start in October, not January?)

**Strong explanatory power — banking examples:**
- H: "CB_INQUIRY_6M is missing for 60% of new-to-bank applicants added in Q3 via new digital channel." This explains: (a) the timing (Q3 channel launch), (b) why the new-to-bank segment is affected but not existing customers, (c) why the magnitude is large (60% missingness → mean imputation → score compression).
- H: "Regulatory rate cap implemented Sep 2024 reduced high-risk originations, shifting the score distribution left." Explains timing (Sep), direction (lower average score), and why PSI is elevated.

**Partial explanatory power:** Acceptable if documented. State what the hypothesis explains and what remains unexplained.
- "H1 explains the direction of KS degradation but not the timing. A separate hypothesis is needed for why it started in October."

---

### 5. Scope

**Definition:** The range of products, segments, and time windows the hypothesis applies to.

**Evaluation questions:**
- Is this specific to one product, or does it generalize across the portfolio?
- Does it apply to all vintages or only recent ones?
- Is it a systemic issue (all scorecards affected) or isolated (one model)?

**Defining scope is mandatory in banking** because:
- Regulatory reports must state the affected population precisely
- Remediation cost depends on whether it's one model or all models
- A hypothesis with undefined scope cannot be acted on

**Scope calibration examples:**

| Scope statement | Assessment |
|---|---|
| "The model is performing poorly" | Undefined — which model, which metric, which population? |
| "The application scorecard KS degraded" | Partially defined — missing product, vintage window, market |
| "The mortgage application scorecard KS degraded by 8 points on Q3 2024 originations in the HCM/HN market" | Well-defined — testable and actionable |

---

### 6. Consistency with Banking Knowledge

**Definition:** The hypothesis aligns with established credit risk theory, regulatory frameworks, and empirical patterns in banking.

**Evaluation questions:**
- Is the proposed mechanism consistent with how credit risk behaves through the cycle?
- Does it align with regulatory guidance (NHNN, Basel III, IFRS 9)?
- If contradicting established practice, is there strong internal evidence justifying it?

**Consistency levels — banking:**

| Level | Example |
|---|---|
| **Fully consistent** | "Recency of bureau inquiry predicts PD — consistent with behavioral scoring literature and Basel IRB guidance on use of behavioral data" |
| **Mostly consistent** | "Adding social network features improves fraud detection" — plausible, some evidence, but not standard practice; requires validation against regulatory data use policies |
| **Inconsistent — requires evidence** | "Removing LTV from the mortgage PD model improves performance" — contradicts fundamental credit risk theory; only proceed with very strong holdout evidence and regulatory discussion |

**Regulatory consistency check:** Any hypothesis that leads to model changes must be checked against:
- NHNN Circular 41/2016/TT-NHNN (credit risk classification)
- Internal model risk policy (SR 11-7 equivalent)
- Fair lending / non-discrimination requirements (protected characteristics as features)

---

### 7. Novelty

**Definition:** In banking DS, novelty is the lowest-priority criterion. Correct and quickly testable beats novel.

**When novelty matters:**
- New data source not previously used in the bank (e.g., open banking transaction data, telco data)
- Novel methodology with demonstrated improvement in academic or industry literature

**When to explicitly deprioritize novelty:**
- Production incident investigation — get to root cause fast, not novel explanation
- Regulatory validation — validators want defensible, well-precedented methods
- Model retraining — use the same architecture unless there is strong evidence for change

---

## Comparative Evaluation

### Ranking Competing Hypotheses

After scoring each hypothesis, rank by:

1. **Eliminate first:** Hypotheses testable with existing data in < 1 day (PSI report, feature audit)
2. **Test second:** Hypotheses requiring offline model experiment (1–5 days)
3. **Test last:** Hypotheses requiring production champion-challenger (weeks to months)
4. **Park:** Hypotheses with weak testability or falsifiability — rewrite or discard

### Distinguishability Table

For each pair of competing hypotheses, identify the single experiment that best distinguishes them:

| Experiment | Distinguishes | Expected result if H1 true | Expected result if H2 true |
|---|---|---|---|
| PSI segmented by LTV band | H1 (drift) vs H2 (data quality) | PSI drops in high-LTV band | PSI stable across bands |
| Bureau field audit by vintage | H2 (data quality) vs H3 (model) | Missing rate spiked in Q3 2024 | Missing rate stable, performance degrades anyway |
| Retrain on recent 6-month window | H3 (overfitting) vs H1 (drift) | Performance recovers | Performance doesn't recover despite retraining |

---

## Common Pitfalls in Banking Hypothesis Work

### Untestable Hypotheses
- "The macroeconomic environment is affecting performance" — no test, no threshold, no action
- "Customer behavior has changed post-COVID" — too vague; specify metric, direction, and magnitude

### Unfalsifiable Hypotheses
- "The model might be biased" — define bias metric and threshold before testing
- "The features may not be capturing enough information" — state what 'enough' means quantitatively

### Skipping Parsimony
- Proposing model retraining before checking data quality — most expensive mistake in banking DS
- Attributing performance degradation to "concept drift" before checking upstream ETL

### Regulatory Risk
- Hypotheses that would lead to removing required risk factors (e.g., LTV, DTI from mortgage model) without strong evidence and regulatory discussion
- Using protected characteristics (age, gender, ethnicity) as features without a fair lending analysis

### Over-scoping
- Generating 6–8 hypotheses for a single production incident → investigation becomes unfocused
- Rule: maximum 4 hypotheses per investigation; narrow the phenomenon if you need more
