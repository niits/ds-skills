# Narrative Structure for Data Stories

Use this reference for a multi-slide sequence or a chart that needs explicit decision framing.
The communication brief in `../workflows/slide-infographic.md` remains the operational starting point.

## Big Idea

Write one sentence with a point of view and stakes:

```text
<evidence-based insight>, therefore <decision or action>.
```

If the evidence is observational, use associative wording. Preserve material uncertainty,
counterevidence, and limitations rather than strengthening the headline.

## Choose a Structure

**Inverted pyramid:** Use for decision-makers who need the conclusion first.

1. Headline and requested decision.
2. Two or three supporting facts.
3. Method and limitations.
4. Appendix or adjacent data.

**Setup, complication, resolution:** Use when shared context is needed before the recommendation.

1. Expected or baseline state.
2. Evidence that changes the interpretation.
3. Recommended response and uncertainty.

Do not manufacture tension when evidence is mixed. State the tension directly, separate the
supporting and contradicting evidence, and identify what would resolve it.

## Slide Sequence

- Give each slide one job and a takeaway title.
- Include only slides that support the Big Idea; move useful verification detail to an appendix.
- Annotate a turning point, outlier, threshold, or focal value only when it advances the argument.
- Do not label a conjectured cause as an event explanation. Use “coincides with” unless causal
  evidence supports stronger wording.

## Three-Minute Test

Explain the message without slides in three minutes:

1. What did you say first? That is the headline.
2. Which evidence did you cite? Those are the essential charts.
3. What decision did you request? That is the close.

Build the sequence around those answers. If a point cannot fit, cut it or make it a separate
communication.

## Audience Adaptation

Derive every audience version from one audited analysis; do not create separate facts.

| Audience | Emphasize | Retain |
|---|---|---|
| Executive | Decision, business effect, risk | Threshold, range, limitation, affected population |
| Committee or governance | Evidence against policy, stability, assumptions | Definitions, support, uncertainty, exceptions |
| Practitioner | Diagnostics, methods, next checks | Full technical context and reproducibility |
| Public or client | Plain language, scale, relevance | Source, definitions, uncertainty, no hidden caveats |

Translate technical metrics into outcomes only through an explicit impact model. Model-chart
audience routing lives in `../domains/model-evaluation.md`.
