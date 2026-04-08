# Design Principles for Data Visualization

## Gestalt Principles Applied to Data Viz

Gestalt psychology describes how the brain groups and interprets visual elements. These principles are directly applicable to data visualization design.

### 1. Proximity
Elements close to each other are perceived as related.

**Application:**
- Place labels next to what they label (not in a distant legend)
- Group related charts close together on a dashboard
- Keep chart title immediately above the chart it describes
- Direct-label a line at its endpoint rather than using a color-matched legend entry

---

### 2. Similarity
Elements that look alike are perceived as belonging to the same group.

**Application:**
- Use the same color to represent the same category across all charts in a presentation
- Use the same line style (solid, dashed) consistently
- If "sales" is blue in chart 1, it must be blue in chart 2
- Define a shared color mapping for categories and apply it consistently throughout a presentation or report

---

### 3. Enclosure
Elements surrounded by a boundary are perceived as grouped.

**Application:**
- Shade a region of a time series to highlight a specific period (e.g. policy change, anomaly window)
- Draw a box around related annotations
- Use a table row highlight to draw attention to one row

---

### 4. Continuity
The eye follows lines and curves; it expects paths to continue smoothly.

**Application:**
- Use lines ONLY for continuous data (time series, trends)
- Never connect points with lines for categorical x-axes
- Order bar chart categories intentionally to tell a story (not alphabetically)

---

### 5. Connection
Explicitly connected elements are perceived as more strongly related than proximity alone.

**Application:**
- Lines in a slope chart connect the "before" and "after" states — the line IS the change
- Connecting lines in an arrow annotation guide the eye from label to data point

---

### 6. Figure-Ground
The eye distinguishes a foreground figure from a background ground.

**Application:**
- Accent color = figure (the thing that matters)
- Gray = ground (the context that recedes)
- White space is not wasted — it is the background that makes the figure pop

---

## Affordance

An affordance is a design property that makes the correct behavior obvious.

**For data visualization:**
- Axis labels tell the audience what unit they are looking at
- Chart titles tell them what conclusion to draw
- Annotations show them where to look
- Consistent color encoding tells them what each color means without re-reading a legend

**Rule:** If a viewer needs to study the chart for more than 5 seconds to understand what it is showing, the affordance has failed. Add a clearer title or annotation.

---

## Accessibility Checklist

### Colorblindness (affects ~8% of men, 0.5% of women)

- [ ] Is there a red + green color pairing as the sole differentiator? → Replace with blue + orange or use patterns
- [ ] Can the chart be understood in grayscale? → If not, add texture or direct labels
- [ ] Using the Okabe-Ito palette? → It is colorblind-safe by design: `#E69F00`, `#56B4E9`, `#009E73`, `#F0E442`, `#0072B2`, `#D55E00`, `#CC79A7`, `#000000`
- [ ] Test with a colorblind simulator: paste your screenshot into Coblis or Viz Palette

### Typography

- [ ] Minimum font size: **9pt** for data labels, **10pt** for axis labels, **11-12pt** for titles
- [ ] No rotated text (no 90° axis tick labels) — use horizontal bars instead
- [ ] Sentence case for all labels: "Revenue (USD)" not "REVENUE (USD)"
- [ ] Include units in parentheses on axis labels: "Time (weeks)", "Score (%)"
- [ ] One font family; vary weight (regular, bold) rather than switching fonts

### Legibility

- [ ] Sufficient contrast between text and background (minimum 4.5:1 ratio for normal text)
- [ ] Dark text on light background (not white on yellow)
- [ ] Avoid placing text over variable-color areas (heatmaps, images)

---

## Layout Principles

### White Space
Do not fill every pixel. White space is rest for the eye and separation between ideas.
- Leave margin around the chart area
- Padding around chart elements prevents visual cramping

### Alignment
Ragged layouts feel unprofessional. Align elements on an invisible grid.
- Align chart titles to the left edge of the plot area
- Align annotations to consistent x or y positions
- Left-aligned titles (not centered) are the SWD convention — they read as a header, not a decoration

### Sizing
- Single-focus chart (one message): roughly 6 × 3.5 to 7 × 4 inches equivalent
- Small multiples (side-by-side comparison): wider canvas with 2–3 columns
- Dashboard tile: compact, single metric with sparkline context

---

## Small Multiples

When the same comparison needs to be shown across many categories, use small multiples — the same chart repeated with one variable changing — rather than one overloaded chart.

**Required inputs for small multiples:**
- A consistent metric to show in each panel
- A categorical variable that defines which panel is which (e.g. region, product, cohort)
- Shared axes across panels so values are comparable without re-reading the scale

**Advantages:** Easy comparison across panels; consistent scale; each panel is simple.
