---
name: banking-hypothesis-generation
description: Structured hypothesis formulation for banking data science. Use when you have experimental observations, model results, or business data and need to formulate testable hypotheses with predictions, propose mechanisms, and design experiments. Covers credit risk, fraud detection, customer analytics, AML, and regulatory model validation contexts. Follows scientific method adapted for banking DS constraints (internal data, regulatory oversight, champion-challenger testing).
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: ds-skills
    domain: banking
    adapted-for: Databricks (no LaTeX output; %md cells for narrative, display(fig) for figures)
---

# Hypothesis Generation — Banking Domain

## Overview

A hypothesis is a specific, testable, falsifiable statement of a mechanism. In banking DS, hypotheses arise from:
- Model performance gaps (why is KS dropping in Q3?)
- Feature investigation (would adding bureau data improve PD model discrimination?)
- Business anomalies (why did early-delinquency rate spike in the Feb vintage?)
- Regulatory findings (validator says model is unstable — what is the root cause?)
- Product decisions (would a lower credit limit reduce first-year default without hurting approval rate?)

A hypothesis is not a question. It is a directional claim with a mechanism: **"If [intervention/change X] then [metric Y] changes by [direction/magnitude Z] in [population/segment W] because [mechanism M]."**

> **Scope vs `feature-onboarding`:** this skill is for **model- and phenomenon-level**
> investigation hypotheses (why did KS drop? would this intervention move the metric?).
> The per-*feature* design hypothesis ("this column measures X, should relate to the
> label because…") lives in the `feature-onboarding` skill, Phase 2. Same `If…then…because`
> shape, different unit of analysis — use this skill to investigate a result, that one to
> justify a candidate feature before computing it.

## When to Use This Skill

- Investigating a model performance regression or unexpected metric
- Generating candidates for a feature engineering sprint
- Designing a champion-challenger or A/B test before committing to production
- Diagnosing model stability failure (PSI spike, KS degradation)
- Preparing a hypothesis-driven model validation section for Risk Committee
- Prioritizing which segments or products to investigate before an audit

---

## Workflow

### 1. Understand the Phenomenon

Before writing any hypothesis, anchor the work in a concrete observation.

**Define the observation precisely:**
- What metric changed, and by how much? (KS dropped from 0.42 to 0.35 on Oct vintage)
- What population is affected? (new-to-bank applicants, SME segment, card revolvers)
- What time window covers the observation? (origination Jan–Jun 2024, performance window 12 months)
- What is already known vs. uncertain?

**Scope boundaries for banking:**
- Is the phenomenon in origination (application scorecard) or behavioral (collection, account management)?
- Is it systemic (all products) or product-specific?
- Is it a data issue, feature issue, or genuine population shift?

**Before proceeding, confirm:**
```
[ ] Metric name, value before and after change
[ ] Population definition (product, segment, origination window)
[ ] Performance window (how long after origination is outcome measured?)
[ ] Data as-of date (what vintage is the test set drawn from?)
[ ] Available data sources for investigation
```

---

### 2. Gather Internal Evidence

For banking DS, the primary evidence base is internal. External literature supplements it, not the reverse.

**Internal sources — check in this order:**

| Source | What to look for |
|---|---|
| Model monitoring reports (PSI, CSI) | Score distribution shift, population drift |
| Vintage performance reports | Divergence between recent and historical vintages |
| Feature importance / SHAP logs | Which features are driving score changes |
| Data quality reports | Missing rates, imputation rate changes, source system changes |
| Origination strategy changes | Cutoff moves, channel mix shifts, bureau product changes |
| Model inventory / prior validation reports | Known weaknesses, conditions from last validation |
| Economic/macro data | GDP, unemployment, rate environment (for systematic risk) |

**External sources for banking:**

| Source | Use case |
|---|---|
| BIS working papers (bis.org/research) | Credit cycle, PD estimation methodology, model risk |
| Basel Committee publications (bcbs.bis.org) | IFRS 9 ECL, IRB, stress testing methodology |
| NHNN/SBV circulars (sbv.gov.vn) | Vietnamese regulatory requirements |
| SSRN — Finance / Econometrics networks | Academic preprints on credit risk, fraud, ML in banking |
| Journal of Credit Risk, Journal of Banking & Finance | Peer-reviewed empirical methods |
| Moody's Analytics, Oliver Wyman, McKinsey Global Banking | Industry methodology reports |

**If no external literature is needed** (internal product, proprietary data, model behavior): skip external search. Use internal evidence as the sole evidence base and document this explicitly.

Consult `references/literature_search_strategies.md` for detailed banking search techniques.

---

### 3. Synthesize Existing Evidence

From the evidence gathered, produce a structured summary:

- What is the most likely proximate cause? (e.g., new bureau field introduced Jan 2024, missing for 40% of applicants)
- What mechanisms could produce the observed pattern?
- What does the data NOT explain? (residual unexplained variance, segments behaving differently)
- What analogies exist from prior incidents? (check model inventory for similar findings in other products)

---

### 3b. Prioritize Before Generating

If sprint capacity is limited (typical: 1-2 week investigation sprint), rank hypotheses before generating them using:

**Prioritization matrix:**

| Criterion | Question | How to score |
|---|---|---|
| **Lift potential** | If true, how much does it move the primary metric? | Estimate expected KS/AP improvement or default rate impact |
| **Test cost** | How much data/compute/time does validation require? | Days to test: <1 day = low cost, >1 week = high cost |
| **Existing signal** | Can existing data already partially confirm or eliminate this? | Check if monitoring reports already answer this |
| **Reversibility** | If we act on this hypothesis and it's wrong, how bad is the error? | High for production model changes, low for offline experiments |

**Rule:** Hypotheses that existing data can already eliminate should be ruled out first — do not run a full experiment on a question that last quarter's PSI report already answers.

**Banking hypothesis template:**
> "If [feature/intervention/policy X] then [metric Y] changes by [direction + magnitude] in [product/segment/population W] because [mechanism M]."

**Examples of well-formed banking hypotheses:**

- "If we add transaction velocity (# of transactions in last 7 days) to the fraud detection model, then precision@100 increases by ≥5pp at the current operating threshold, because velocity is a leading indicator of account takeover not currently captured in the feature set."
- "If we re-score revolving credit applicants using 6-month behavioral window instead of 12-month, then KS improves by ≥3 points on the 2023 origination cohort, because recent behavioral signals are more predictive of near-term default for revolving products."
- "If the PSI spike on the mortgage scorecard is explained by a change in LTV distribution (new high-LTV product launched Q2), then the PSI drops below 0.10 when we segment the analysis by LTV band."
- "If we remove the bureau field `CB_INQUIRY_6M` from the application scorecard, model performance on non-bureau applicants (new-to-credit) does not change, because this feature is missing for >60% of that segment and is imputed with the population mean."

---

### 4. Generate Competing Hypotheses

Develop **2–4 competing hypotheses** for investigation sprints; **1–2** for urgent production incidents. More than 4 is a sign of insufficient scope definition — narrow the phenomenon first.

Each hypothesis must have:
- A **mechanism** (not just "feature X is important" — explain why it should predict the outcome)
- A **falsification condition** (what data outcome rejects it)
- **Distinguishability** from the other hypotheses (different mechanism, different data source to test)

**Banking-specific hypothesis generation strategies:**

**Population drift hypotheses:**
- New origination channel changed applicant mix
- Credit policy change shifted risk profile
- Macro factor (rate rise, unemployment spike) changed default behavior

**Feature/data quality hypotheses:**
- Bureau field changed definition or coverage
- Imputation logic change upstream affected derived features
- New product launched creates population not well-represented in training data

**Model architecture hypotheses:**
- Score is well-ranked but miscalibrated (AUC good, calibration poor)
- Model overfits to a specific vintage pattern not generalizing to recent data
- A segment (e.g., young borrowers, SME) was under-represented in training

**Business/strategy hypotheses:**
- Credit limit changes altered behavioral patterns (self-fulfilling: lower limit → lower utilization → looks less risky)
- Collections strategy change altered the observed default definition
- Approval rate change at cutoff altered the observed population (selection bias)

---

### 5. Evaluate Hypothesis Quality

Apply criteria from `references/hypothesis_quality_criteria.md`.

**Banking-adapted quality criteria:**

| Criterion | Banking DS interpretation | Red flag |
|---|---|---|
| **Testability** | Is there a holdout set, A/B experiment, or backtesting window to test this? | "We'd need to wait 12 months for outcomes" is a high-cost, not untestable, hypothesis |
| **Falsifiability** | State the metric threshold that rejects the hypothesis ("AP improvement < 0.02 on holdout rejects H1") | "Performance may improve" is not falsifiable |
| **Parsimony** | Prefer data quality / population shift explanations before model architecture explanations | Don't invoke model redesign before ruling out upstream data issues |
| **Explanatory power** | Does this mechanism account for the full magnitude of the observed change? | Partial explanations are acceptable but must state what remains unexplained |
| **Consistency** | Does it align with what credit cycle / behavioral data theory predicts? | Contradicting established credit risk principles requires strong evidence |
| **Novelty** | Lower priority in banking — correctness and speed to test matter more than novelty | Don't chase novel explanations when mundane ones (data quality) haven't been eliminated |

---

### 6. Design Tests

For each hypothesis, specify the test. Use patterns from `references/experimental_design_patterns.md`.

**Banking test design elements:**
- What is the test dataset? (holdout, backtesting window, champion-challenger split)
- What is the comparison? (model with / without feature; before / after policy change)
- What is the primary metric? (KS, AP, PSI, precision@k, default rate at cutoff)
- What is the sample size and statistical power?
- What confounds need to be controlled? (vintage, macro environment, product mix)
- What is the decision rule? (if metric threshold met, proceed to champion-challenger in production)

---

### 7. Formulate Testable Predictions

For each hypothesis, write specific, quantitative predictions:

- Direction and magnitude of metric change
- Population / segment where effect should be observed
- Time window for evaluation
- What outcome falsifies the hypothesis

**Distinguish between competing hypotheses with different predictions:**

If H1 (population drift) is true → PSI drops when segmented by channel; model performance stable within each channel.
If H2 (feature data quality) is true → PSI stable across channels; performance degrades specifically on the affected feature quartile.
If H3 (model overfitting to vintage) is true → both PSI and model performance degrade on recent vintages only; historical vintages remain stable.

---

### 8. Output Format (Databricks Notebook)

Write all output as Markdown in `%md` cells. Do NOT use `displayHTML()`.

**Executive Summary (`%md` cell):**

```markdown
## Hypothesis Investigation: [Phenomenon Title]

**Observation:** KS dropped from 0.42 to 0.34 on Oct–Dec 2024 origination cohort (mortgage scorecard v3.1).
**Primary hypothesis:** Population drift via new high-LTV product (H1).
**Top recommendation:** Run PSI segmentation by LTV band before any model retraining.
**Decision required by:** [date]
```

**Hypothesis block template (`%md` cell — one per hypothesis):**

```markdown
### H1: [Title]

**Mechanism:** ...

**Key evidence:**
- [Internal evidence source + finding]
- [Supporting data point]

**Falsification condition:** If [observable metric outcome], H1 is rejected.

**Recommended test:** [test name, dataset, metric, decision threshold]
```

**Predictions table (`%md` cell):**

```markdown
### Testable Predictions

| Hypothesis | If true, we expect | Falsified if | Test dataset |
|---|---|---|---|
| H1: Population drift | PSI drops to <0.10 when segmented by LTV band | PSI remains ≥0.20 in all LTV bands | Oct–Dec 2024 origination |
| H2: Bureau data issue | CB_INQUIRY_6M missing rate >40% in failing vintages | Missing rate stable at historical level | Data quality report, Dec 2024 |
```

**Critical comparisons (`%md` cell):**

```markdown
### Distinguishing Experiments

| Test | Distinguishes | H1 expects | H2 expects |
|---|---|---|---|
| PSI by LTV band | H1 vs H2 | PSI drops in high-LTV segment | PSI stable across LTV bands |
| Bureau field audit | H1 vs H2 | Missing rate stable | Missing rate spiked in failing vintages |
```

**Citation format:** Inline author-year: `(Smith et al., 2023)`. For internal reports: `(Model Monitoring Report, Q4 2024)`.

---

## Quality Standards

- **Mechanism required:** "Feature X is important" is not a hypothesis. Explain why it predicts the outcome.
- **Quantitative falsification:** Every hypothesis must state a metric threshold that rejects it.
- **Parsimony first:** Rule out data quality and population shift before model architecture changes.
- **Regulatory defensibility:** Hypotheses in formal validation documents must cite evidence. "We believe..." is not acceptable.
- **No more than 4 hypotheses without narrowing scope:** More hypotheses = phenomenon is underdefined.

---

## Resources

### references/
- `hypothesis_quality_criteria.md` — Quality criteria adapted for banking DS (testability, falsifiability, parsimony) with banking examples
- `experimental_design_patterns.md` — Banking experiment design patterns: champion-challenger, holdout, backtesting, A/B test, quasi-experimental
- `literature_search_strategies.md` — How to find banking evidence: internal reports, BIS, NHNN, SSRN, industry research
