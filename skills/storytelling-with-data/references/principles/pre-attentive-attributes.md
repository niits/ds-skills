# Pre-Attentive Attributes

Pre-attentive attributes are visual properties that the human brain processes in under 250 milliseconds — before conscious attention is applied. They are the tools for directing the audience's eye to exactly what matters.

## The Core Principle

**Use one accent; gray everything else.**

The brain interprets difference as importance. If everything is colorful, nothing is important. If one thing is orange and everything else is gray, the eye goes directly to the orange.

---

## Attribute Reference

### Color (Hue)
The most powerful pre-attentive attribute for categorical distinction.

**Rules:**
- Use a maximum of 1 accent color for "the thing that matters"
- All supporting data: light gray (receding, present but not competing)
- Never use red for negative unless financial loss (red = danger in some cultures)
- Colorblind-safe: avoid red + green as the only differentiator

**How to apply:**
- Identify the one bar, line, or point that carries the message
- Give it the accent color; give everything else the same gray

---

### Color (Saturation / Intensity)
Darker or more saturated = more important.

**Use case:** Sequential data (heatmaps, choropleth maps, magnitude encoding).

**How to apply:**
- Use a light-to-dark colormap for sequential data (e.g. Blues, Oranges)
- Use a diverging colormap (e.g. RdBu) when data has a meaningful midpoint (e.g. above/below zero)

---

### Size
Larger = more important or bigger magnitude.

**Use cases:** Bubble charts, dot plots where a third dimension is encoded in size.

**Rule:** Size is hard to decode precisely. Use it for categorical importance, not for exact values.

---

### Bold / Weight
The fastest way to create emphasis in text-heavy visuals and annotations.

**How to apply:**
- Key finding or main number: bold, accent color, larger font
- Supporting context or comparison: regular weight, gray, smaller font
- Use weight contrast — not font family changes — for hierarchy

---

### Position
The brain reads left-to-right, top-to-bottom, and compares aligned baselines.

**Rules:**
- Always align bars to the same baseline (start at 0)
- The leftmost or topmost item is perceived as "first" or "most important"
- Use position to encode ranking: sort by value, not alphabetically

---

### Enclosure
A box, shaded region, or circle around elements groups them and draws attention.

**Use case:** Highlighting a specific time range, flagging an anomaly region.

**How to apply:**
- Shade a time range with a semi-transparent vertical band to signal an anomaly period
- Label the shaded region directly inside or above it
- A rectangular border drawn around a group of annotations implies they belong together

---

### Connection (Lines)
Lines imply a relationship or sequence between connected points.

**Rule:** Only connect data points with a line if the intermediate values exist (continuous data). Never use a line chart for categorical x-axes.

---

## The Gray Palette Strategy

The full SWD (Storytelling with Data) gray-to-accent system:

```
Background:     white
Grid / borders: near-invisible light gray
Context data:   light gray — present but receding
Secondary text: mid gray — readable but subordinate
Primary text:   near-black — all titles and axis labels
Accent 1:       one bold color — THE focus, use once per chart
Accent 2:       a second color — only for a direct comparison point
Negative:       red — financial loss, error states only
Positive:       green — goal achieved, up vs target only
```

---

## Pre-Attentive Attribute Selection Guide

| Goal | Use This Attribute |
|---|---|
| "Look at THIS bar/line/point" | Color (hue) — one accent |
| "This category is bigger" | Size or color intensity |
| "These items belong together" | Enclosure or proximity |
| "This is the critical range" | Enclosure (shaded band) |
| "This number is important" | Bold + larger font size |
| "These two things are related" | Connection (line) |
| "Rank these items" | Position (sorted order) |
