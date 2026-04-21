---
name: hypothesis-generation
description: Structured hypothesis formulation from observations. Use when you have experimental observations or data and need to formulate testable hypotheses with predictions, propose mechanisms, and design experiments to test them. Follows scientific method framework. For open-ended ideation use scientific-brainstorming; for automated LLM-driven hypothesis testing on datasets use hypogenic.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: K-Dense Inc.
    adapted-for: Databricks (no LaTeX output)
---

# Scientific Hypothesis Generation

## Overview

Hypothesis generation is a systematic process for developing testable explanations. Formulate evidence-based hypotheses from observations, design experiments, explore competing explanations, and develop predictions. Apply this skill for scientific inquiry across domains.

## When to Use This Skill

This skill should be used when:
- Developing hypotheses from observations or preliminary data
- Designing experiments to test scientific questions
- Exploring competing explanations for phenomena
- Formulating testable predictions for research
- Conducting literature-based hypothesis generation
- Planning mechanistic studies across scientific domains

---

## Workflow

Follow this systematic process to generate robust scientific hypotheses:

### 1. Understand the Phenomenon

Start by clarifying the observation, question, or phenomenon that requires explanation:

- Identify the core observation or pattern that needs explanation
- Define the scope and boundaries of the phenomenon
- Note any constraints or specific contexts
- Clarify what is already known vs. what is uncertain
- Identify the relevant scientific domain(s)

### 2. Conduct Comprehensive Literature Search

Search existing scientific literature to ground hypotheses in current evidence. Use both PubMed (for biomedical topics) and general web search (for broader scientific domains):

**For biomedical topics:**
- Use WebFetch with PubMed URLs to access relevant literature
- Search for recent reviews, meta-analyses, and primary research
- Look for similar phenomena, related mechanisms, or analogous systems

**For all scientific domains:**
- Use WebSearch to find recent papers, preprints, and reviews
- Search for established theories, mechanisms, or frameworks
- Identify gaps in current understanding

**If no public literature applies (proprietary data, internal product metrics):**
Skip external search. Use internal evidence as the evidence base:
- EDA summaries and exploratory notebooks
- Prior experiment logs and A/B test results
- Domain expert interviews and historical baselines
Proceed directly to Step 3 with these as inputs. "Literature-based" steps are optional, not required.

**Search strategy (when literature exists):**
- Begin with broad searches to understand the landscape
- Narrow to specific mechanisms, pathways, or theories
- Look for contradictory findings or unresolved debates
- Consult `references/literature_search_strategies.md` for detailed search techniques

### 3. Synthesize Existing Evidence

Analyze and integrate findings from literature search:

- Summarize current understanding of the phenomenon
- Identify established mechanisms or theories that may apply
- Note conflicting evidence or alternative viewpoints
- Recognize gaps, limitations, or unanswered questions
- Identify analogies from related systems or domains

### 3b. Prioritize Before Generating (When Resources Are Limited)

If you have limited time or experiment budget, rank hypotheses by:
1. **Lift potential** — if true, how much does it move the primary metric?
2. **Test cost** — how much time/data does validation require?
3. **Existing signal** — can existing data partially eliminate this hypothesis before running an experiment?

Hypotheses that can be eliminated with existing data should be ruled out first. Do not design a full experiment for a hypothesis that historical data already answers.

**DS-native hypothesis template:**
> "If [feature/intervention X] then [metric Y] changes by [direction/magnitude Z] in [population/segment W] because [mechanism]."

Example: "If we add recency score as a feature, then AP on the holdout set increases by ≥ 0.03 in the high-value segment because recency captures intent signal currently missing from the model."

---

### 4. Generate Competing Hypotheses

Develop 3–5 distinct hypotheses for mechanistic studies; 1–2 for sprint/exploratory contexts (label scope explicitly). Each hypothesis should:

- Provide a mechanistic explanation (not just description)
- Be distinguishable from other hypotheses
- Draw on evidence from the literature synthesis
- Consider different levels of explanation (molecular, cellular, systemic, population, etc.)

**Strategies for generating hypotheses:**
- Apply known mechanisms from analogous systems
- Consider multiple causative pathways
- Explore different scales of explanation
- Question assumptions in existing explanations
- Combine mechanisms in novel ways

### 5. Evaluate Hypothesis Quality

Assess each hypothesis against established quality criteria from `references/hypothesis_quality_criteria.md`:

**Testability:** Can the hypothesis be empirically tested? *(DS: is there a holdout set or A/B experiment that could confirm/reject it?)*
**Falsifiability:** What observations would disprove it? *(DS: define the metric threshold that rejects the hypothesis, e.g. "AP improvement < 0.02 on holdout")*
**Parsimony:** Is it the simplest explanation that fits the evidence? *(DS: prefer fewer features / simpler mechanisms over complex multi-factor explanations)*
**Explanatory Power:** How much of the phenomenon does it explain?
**Scope:** What range of observations does it cover?
**Consistency:** Does it align with established principles?
**Novelty:** Does it offer new insights beyond existing explanations? *(Lower priority in business contexts — correctness and testability matter more than novelty)*

Explicitly note the strengths and weaknesses of each hypothesis.

### 6. Design Experimental Tests

For each viable hypothesis, propose specific experiments or studies to test it. Consult `references/experimental_design_patterns.md` for common approaches:

**Experimental design elements:**
- What would be measured or observed?
- What comparisons or controls are needed?
- What methods or techniques would be used?
- What sample sizes or statistical approaches are appropriate?
- What are potential confounds and how to address them?

**Consider multiple approaches:**
- Data science experiments (A/B test, holdout group, simulation, champion-challenger)
- Observational studies (cross-sectional, longitudinal, case-control)
- Laboratory experiments (in vitro, in vivo) — for biomedical/scientific domains only
- Natural experiments or quasi-experimental designs

### 7. Formulate Testable Predictions

For each hypothesis, generate specific, quantitative predictions:

- State what should be observed if the hypothesis is correct
- Specify expected direction and magnitude of effects when possible
- Identify conditions under which predictions should hold
- Distinguish predictions between competing hypotheses
- Note predictions that would falsify the hypothesis

### 8. Present Structured Output (Databricks Notebook)

Write all output as Markdown in `%md` cells. Do NOT use `displayHTML()` or generate LaTeX or PDFs.

**Report structure:**

1. **Executive Summary** — brief overview of the phenomenon and top hypothesis
2. **Competing Hypotheses** — one `%md` section per hypothesis (template below)
3. **Testable Predictions** — table format
4. **Critical Comparisons** — which experiments best distinguish hypotheses
5. **References** — inline citations with author/year/title

**Hypothesis block template (`%md` cell):**

```markdown
### Hypothesis 1: [Title]

**Mechanism:** ...

**Key Evidence:**
- ...
- ...

**Core Assumptions:** ...

**Falsification condition:** If [observable outcome], this hypothesis is rejected.
```

**Predictions table template:**

```markdown
### Testable Predictions

| Hypothesis | If true, we expect | Falsified if |
|---|---|---|
| H1: [Title] | [direction + metric + magnitude] | [threshold not met] |
| H2: [Title] | ... | ... |
```

**Critical comparisons template:**

```markdown
### Critical Comparisons

| Experiment | Distinguishes | Expected outcome per hypothesis |
|---|---|---|
| [Experiment name] | H1 vs H2 | H1: ..., H2: ... |
```

**Citation format:** Inline author-year: `(Smith et al., 2023)`. Full references in a final `%md` cell.

**Citation targets:**
- Main body: 5–10 key citations for DS/business contexts; 10–15 for scientific/mechanistic studies
- Reference list: include all cited sources

---

## Quality Standards

Ensure all generated hypotheses meet these standards:

- **Evidence-based:** Grounded in existing literature with citations
- **Testable:** Include specific, measurable predictions
- **Mechanistic:** Explain how/why, not just what
- **Comprehensive:** Consider alternative explanations
- **Rigorous:** Include experimental designs to test predictions

---

## Resources

### references/

- `hypothesis_quality_criteria.md` — Framework for evaluating hypothesis quality (testability, falsifiability, parsimony, explanatory power, scope, consistency)
- `experimental_design_patterns.md` — Common experimental approaches across domains (RCTs, observational studies, lab experiments, computational models)
- `literature_search_strategies.md` — Effective search techniques for PubMed and general scientific sources
