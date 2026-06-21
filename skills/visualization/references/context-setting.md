# Context Setting

## The Big Idea Framework

The Big Idea is a single sentence that:
1. Articulates your point of view
2. Conveys what is at stake
3. Is a complete sentence (subject + verb + so what)

**Template:**
> [Insight about the data] because [evidence], therefore [recommended action].

**Examples:**

| Weak (description) | Strong (Big Idea) |
|---|---|
| "This report covers Q3 sales performance." | "We must expand the Northeast sales team because Q3 revenue grew 40% with only 2 reps." |
| "Customer satisfaction data from the survey." | "Onboarding friction is driving churn — 68% of churned users never completed setup." |
| "Model accuracy comparison across methods." | "The lightweight model is production-ready: 94% accuracy at 10x lower latency than the baseline." |

---

## Audience Analysis Worksheet

Answer these before building any visual:

```
PRIMARY AUDIENCE
  Name / role: ____________________
  Domain expertise level (1-5): ____
  What they already know: ____________________
  What they DON'T know: ____________________
  What they care most about: ____________________

COMMUNICATION GOAL
  After seeing this, they should BELIEVE: ____________________
  After seeing this, they should DO: ____________________
  The ONE thing they must remember: ____________________

BIG IDEA (one sentence):
  ____________________

COMMUNICATION MODE
  [ ] Live presentation — minimize text, maximize visuals, you carry the narration
  [ ] Standalone document — visuals must make sense without you present
  [ ] Dashboard — exploratory, no single narrative, audience self-serves
```

---

## Communication Mode Guide

### Live Presentation
- Keep text on slides minimal — you are the narrator
- Each slide = one idea
- Use builds (reveal elements progressively) to control pace
- Title of every slide = the takeaway, not the topic

### Standalone Document / Report
- Visuals must be fully self-explanatory
- Every chart needs: title (insight), axis labels with units, data source
- Add a "so what" paragraph after each chart
- Executive summary = the Big Idea + 3 supporting points

### Dashboard
- No single narrative — audience explores
- Prioritize layout: most important metric top-left
- Use consistent color encoding across all charts
- Provide filters for audience to ask their own questions
- Do NOT use dashboards when you need to drive a specific decision

---

## The Newspaper Test

After drafting your visual, ask: "If a journalist wrote a headline about this chart, what would it say?"

That headline should match your title. If it doesn't, revise your title.

---

## The 3-Minute Story

Force yourself to explain the entire message in 3 minutes. Anything you can't cover is either:
- Not essential (cut it), or
- Needs a separate communication (create it)

Structure:
1. **Hook** (30 sec): The one thing that matters most
2. **Evidence** (90 sec): 2-3 data points that prove it
3. **Action** (60 sec): What you need from them, specifically

---

## Tone Calibration

| Audience | Tone | What to Emphasize |
|---|---|---|
| C-suite executive | Concise, strategic | Business impact, $ numbers, risk |
| Data science team | Technical, precise | Methodology, uncertainty, reproducibility |
| Operations team | Practical, specific | Process steps, timelines, ownership |
| External client | Professional, narrative | Story, outcomes, their benefit |
| General public | Accessible, visual | Analogy, relative scale, human impact |
