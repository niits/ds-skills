# Narrative Structure for Data Stories

## The Story Arc

Every data presentation — whether a single chart or a 20-slide deck — should follow a narrative arc:

```
SETUP                    CONFLICT                 RESOLUTION
"Here is the world       "Here is the problem     "Here is what we
as we expected it"       or unexpected finding"   should do about it"

Context + baseline   →   The data insight      →   Call to action
```

The tension between expectation (setup) and reality (conflict) is what makes data compelling. If you only present the resolution, the audience doesn't feel why it matters.

---

## The Big Idea as the Story Spine

Everything in the presentation should connect back to the Big Idea sentence:

> [Data insight] + [evidence] → therefore [action]

**Test every slide:** "Does this slide support the Big Idea?" If no → cut it or move it to an appendix.

---

## Presentation Structure

### The Inverted Pyramid (most common for business)

1. **Headline / Big Idea** — the most important thing, first
2. **Key supporting data** — 2–3 data points that prove it
3. **Detail / methodology** — for those who want to verify
4. **Appendix** — raw data, alternative analyses

This is the opposite of how analysts think (we build to the conclusion). Business audiences want the conclusion first.

### The Narrative Arc (for persuasive presentations)

1. **Setup** — shared context, what we all agreed was true
2. **Complication** — what the data reveals that challenges the setup
3. **Resolution** — the recommended action and expected outcome

---

## Slide / Section Title Rules

The title of every slide IS the takeaway, not the topic.

| Topic title (bad) | Insight title (good) |
|---|---|
| "Q3 Revenue by Region" | "Northeast fell 18% — only region below target" |
| "Model Accuracy Comparison" | "Our model matches GPT-4 at 1/10th the cost" |
| "User Retention Analysis" | "Day-7 retention dropped 12 pts after the UI redesign" |
| "Survey Results" | "Customers trust us — but don't recommend us" |

**How to write insight titles:**
- Include the direction of change (up, down, leads, lags, fell, grew)
- Include a number when possible
- State the implication, not just the observation

---

## Annotation as Narration

Annotations on the chart eliminate the gap between "what the data shows" and "what it means." They are mini-narrators built into the visual.

**When to annotate:**
- The moment the trend changes
- An outlier or anomaly
- When the target/benchmark is crossed
- The single most important data point

**What to include in an annotation:**
- The event or cause (e.g. "Supply disruption starts here")
- The threshold being crossed (e.g. "Target: 5.0%")
- The magnitude of the change if not obvious from the axis

---

## The 3-Minute Story Exercise

Before building any presentation:

1. Set a 3-minute timer
2. Talk through your entire message out loud — no slides
3. Note what you said:
   - What did you say first? (That is your headline)
   - What data did you cite? (Those are your key charts)
   - What did you ask for? (That is your call to action)
4. Build your slides to match this spoken structure, not the other way around

---

## Dealing with Mixed Messages (When Data is Complex)

Not every finding is a clean story. When data is complex or ambiguous:

**Option 1: Acknowledge the tension**
> "The revenue numbers look strong, but when we adjust for the one-time deal in November, the underlying trend is flat."

**Option 2: Lead with the implication, show the complexity after**
> "We need to invest in Q1 pipeline. [Big chart]. Here is why the Q4 numbers alone are misleading. [Smaller supporting chart]."

**Option 3: Use a two-part structure**
- Chart 1: "Here is what looks good" (setup)
- Chart 2: "Here is the problem underneath" (conflict)
- Call to action: Resolution

---

## The Appendix Strategy

Analysts worry about losing credibility if they leave data out. The appendix solves this:

- Main deck: only slides that support the Big Idea
- Appendix: all additional analyses, methodology, raw data, alternative cuts

**In practice:**
- In Databricks: put deep-dive cells in a collapsed section at the bottom
- In a presentation: have backup slides ready if asked

This lets you keep the main story crisp while being ready for detailed questions.

---

## Story Templates

### Template 1: Performance Review
```
1. [Team/product] met / missed the target this period
2. Key driver: [one root cause with data]
3. What we are doing about it: [specific action]
```

### Template 2: Recommendation
```
1. We face [problem] — [data showing magnitude]
2. We have evaluated [N] options — here is why [Option X] is best
3. If approved, we expect [specific outcome] by [date]
4. We need [specific resource/decision] by [date]
```

### Template 3: Experiment Results
```
1. We ran [experiment] to test [hypothesis]
2. The result was [finding] — [statistically significant / not]
3. This means we should [action] / [further test]
```

### Template 4: Trend Alert
```
1. [Metric] has been [declining/growing] for [N] periods
2. Root cause analysis suggests [driver]
3. If the trend continues: [projected impact]
4. Recommended intervention: [action]
```
