# Slide and Infographic Workflow

`../../SKILL.md` owns intent routing and Quick EDA. Use this reference only after the request has
been classified as a shared slide or infographic.

### Goal

Create a self-contained visual argument for a defined audience. A slide chart may occupy only
part of a slide; an infographic may combine several visual elements, but each chart still needs
one job and one main takeaway.

### 1. Write the Brief

Complete this before choosing a chart:

```text
Audience:
Decision or action:
Question:
One-sentence takeaway:
Metric definition and unit:
Population, filters, and period:
Source and update date:
Material uncertainty or limitation:
Output dimensions or placement:
```

If the artifact is already known to be a slide or infographic but the takeaway is not yet
supported, keep this workflow and mark the takeaway provisional. Audit or analyze the evidence
before turning it into an insight title.

### 2. Audit the Evidence

Apply the hard gate and detailed time, weighting, support, uncertainty, accessibility, caption,
and delivery checks in `../delivery/audit-and-delivery.md`.

### 3. Specify the Grammar Before Code

Describe the chart as a composition rather than by style name:

```text
Data and row grain:
x / y mappings:
color / fill / size / shape / group mappings:
mark(s) and layer order:
statistical transformation and position adjustment:
scales and coordinate transformation:
facets:
annotations and reference values:
```

This is the short form of the template in `../foundations/grammar-of-graphics.md`; complete it even
when matplotlib is the renderer.

### 4. Select and Prototype

Choose the most accurate familiar encoding that supports the takeaway. Start with the simplest
valid layer, then add uncertainty, a comparison, or a reference value only when it changes the
interpretation. Use `../foundations/chart-selection.md` when the choice is unclear.

Renderer choice:

- Use matplotlib by default for a static slide or infographic and for exact annotation control.
- Use plotnine when facets, grouped mappings, or multiple statistical layers make the grammar
  clearer and shorter than imperative code.
- Use neither library to simulate an infographic layout system. Compose charts and text in the
  user's requested slide, document, or design surface when one is available.

### 5. Direct Attention

- Write an insight title that states the takeaway, not merely the topic.
- Place the strongest comparison in position or length, not color or area alone.
- Sort ranked categories deliberately and use a natural order for time or ordinal categories.
- Keep context in neutral colors and reserve one accent for the evidence that supports the title.
- Prefer direct labels when they remain readable. Remove legends only after replacing the
  information they carry.
- Keep gridlines, annotations, and reference lines only when they help the reader estimate or
  interpret values.
- Use whitespace and alignment to establish reading order. Do not decorate empty space.

### 6. Validate and Deliver

Run the truth, accessibility, caption, and artifact checks in
`../delivery/audit-and-delivery.md`. Export at the dimensions and format requested by the
destination; do not invent venue requirements or claim checks that were not performed.

### Output Template

```text
Takeaway:
Chart choice: <form>, because <reason tied to question and variable types>.
Interpretation:
Limitation or likely misreading:
Alt text:
Source / period / unit note:
Validation performed / pending:
```

Specialist overlays and optional implementation references are routed from `../../SKILL.md`; they
do not create another workflow.
