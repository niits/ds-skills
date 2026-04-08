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

**Search strategy:**
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

### 4. Generate Competing Hypotheses

Develop 3-5 distinct hypotheses that could explain the phenomenon. Each hypothesis should:

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

**Testability:** Can the hypothesis be empirically tested?
**Falsifiability:** What observations would disprove it?
**Parsimony:** Is it the simplest explanation that fits the evidence?
**Explanatory Power:** How much of the phenomenon does it explain?
**Scope:** What range of observations does it cover?
**Consistency:** Does it align with established principles?
**Novelty:** Does it offer new insights beyond existing explanations?

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
- Laboratory experiments (in vitro, in vivo, computational)
- Observational studies (cross-sectional, longitudinal, case-control)
- Clinical trials (if applicable)
- Natural experiments or quasi-experimental designs

### 7. Formulate Testable Predictions

For each hypothesis, generate specific, quantitative predictions:

- State what should be observed if the hypothesis is correct
- Specify expected direction and magnitude of effects when possible
- Identify conditions under which predictions should hold
- Distinguish predictions between competing hypotheses
- Note predictions that would falsify the hypothesis

### 8. Present Structured Output (Databricks Notebook)

Generate output as a Databricks-compatible Markdown report. Use `displayHTML()` for colored visual sections or write Markdown cells using `%md`. Do NOT generate LaTeX or compile PDFs.

**Output format:**

Write the full report as a Python string passed to `displayHTML()`, or output clean Markdown that can be pasted into a `%md` cell.

**Report structure:**

1. **Executive Summary** — brief overview of the phenomenon and top hypothesis
2. **Competing Hypotheses** — each in a colored HTML block (see template below)
3. **Testable Predictions** — key predictions per hypothesis
4. **Critical Comparisons** — which experiments best distinguish hypotheses
5. **References** — inline citations with author/year/title

**HTML block template for each hypothesis:**

```python
displayHTML("""
<div style="background:#e8f4fd;border-left:5px solid #2196F3;padding:16px;margin:12px 0;border-radius:4px">
  <h3 style="color:#1565C0;margin:0 0 8px 0">Hypothesis 1: [Title]</h3>
  <p><b>Mechanism:</b> ...</p>
  <p><b>Key Evidence:</b></p>
  <ul>
    <li>...</li>
  </ul>
  <p><b>Core Assumptions:</b> ...</p>
</div>
""")
```

**Color palette for hypothesis blocks (use in order):**

| Hypothesis | Background | Border |
|---|---|---|
| H1 | `#e8f4fd` | `#2196F3` (blue) |
| H2 | `#e8f5e9` | `#4CAF50` (green) |
| H3 | `#f3e5f5` | `#9C27B0` (purple) |
| H4 | `#e0f2f1` | `#009688` (teal) |
| H5 | `#fff3e0` | `#FF9800` (orange) |

**Predictions block:**

```python
displayHTML("""
<div style="background:#fffde7;border-left:5px solid #FFC107;padding:16px;margin:12px 0;border-radius:4px">
  <h3 style="color:#F57F17;margin:0 0 8px 0">Testable Predictions</h3>
  <ul>
    <li><b>H1:</b> ...</li>
    <li><b>H2:</b> ...</li>
  </ul>
</div>
""")
```

**Comparison block:**

```python
displayHTML("""
<div style="background:#f5f5f5;border-left:5px solid #607D8B;padding:16px;margin:12px 0;border-radius:4px">
  <h3 style="color:#37474F;margin:0 0 8px 0">Critical Comparisons</h3>
  <p>...</p>
</div>
""")
```

**Citation format:** Use inline author-year style: `(Smith et al., 2023)`. List full references at the end of the notebook in a `%md` cell.

**Citation targets:**
- Main body: 10–15 key citations
- Reference list: 40–70+ covering all relevant literature

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
