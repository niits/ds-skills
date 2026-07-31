# Chart Selection Guide

## Decision Tree

```
What relationship are you showing?
│
├── Change over time?
│   ├── Few time points (< 6) → Bar chart (vertical)
│   ├── Many time points      → Line chart
│   ├── Exactly two points    → Slope chart
│   └── Cumulative change     → Area chart (filled)
│
├── Comparison between categories?
│   ├── Few categories (≤ 7) → Vertical bar chart
│   ├── Many categories      → Horizontal bar chart
│   ├── Ranked list          → Sorted horizontal bar
│   └── Two groups           → Back-to-back bar (diverging)
│
├── Part of a whole?
│   ├── Few parts (2–3)     → Stacked bar or 100% bar
│   ├── Many parts          → Stacked bar (sorted by size)
│   └── Never               → Pie chart (use bar instead)
│
├── Distribution?
│   ├── One variable        → Histogram or density plot
│   └── Multiple groups     → Box plot or violin plot
│
├── Relationship / correlation?
│   └── Two continuous vars → Scatter plot
│       └── + time          → Connected scatter
│
└── Single important number?
    └── Big number + sparkline or comparison text
```

---

## Chart-by-Chart Guide

### Line Chart — Change Over Time

**Use when:** Data is continuous over time; the trend or trajectory is the message.

**Required inputs:**
- One or more time series: `(x_values, y_values)` pairs per series
- Series names for direct labeling

**Rules:**
- Label lines directly at the end; remove legend
- Maximum 4–5 lines before it becomes spaghetti
- Gray all lines except the one that matters
- X-axis = time; do NOT use line charts for categorical x-axes

---

### Bar Chart (Vertical) — Categorical Comparison, Few Categories

**Use when:** Comparing a small number of discrete categories; values start at zero.

**Required inputs:**
- `categories` — list of category labels
- `values` — numeric value for each category

**Rules:**
- Always start y-axis at 0
- Sort bars by value (unless there is a natural order)
- Width: bars should be wider than the gaps between them (0.6–0.8 relative width)
- Add value labels directly on bars to eliminate the y-axis

---

### Horizontal Bar Chart — Many Categories or Long Labels

**Use when:** More than 7 categories, or category names are long text.

**Required inputs:**
- `categories` — list of category labels
- `values` — numeric value for each category

**Rules:**
- Sort by value (descending, so largest is at top)
- This also makes rotated axis labels unnecessary
- Direct value labels on the right side of each bar

---

### Scatter Plot — Correlation / Relationship

**Use when:** Showing the relationship between two continuous variables.

**Required inputs:**
- `x` — array of values for the x variable
- `y` — array of values for the y variable
- `labels` *(optional)* — entity labels for notable outliers
- `outlier_indices` *(optional)* — indices of points to highlight

**Rules:**
- Label notable outliers directly on the chart
- Add a trend line only when the trend is the message
- Use transparency (alpha) when points overlap
- Color-encode a third variable only if it is the message

---

### Slope Chart — Change Between Two Points

**Use when:** Showing change between exactly two time periods for multiple categories.
Better than grouped bar for showing directionality of change.

**Required inputs:**
- `data` — dictionary mapping category name → `(value_before, value_after)`
- `focus` — which category to accent

**Rules:**
- Label both endpoints directly; no legend needed
- Endpoint difference encodes change; steepness varies with aspect ratio and axis scale.
  Use common scales and directly label absolute or percentage change.
- Accent the category of interest; gray the others

---

### What to NEVER Use

| Chart | Why | Replace With |
|---|---|---|
| Pie chart | Cannot compare angles accurately | Bar chart |
| 3D bar / 3D pie | Depth distorts values | 2D bar |
| Dual y-axis | Scales are arbitrary; misleads | Two separate charts |
| Radar / spider | Overloaded; impossible to compare | Bar chart |
| Bubble chart (3 vars), when precise values matter | Size is decoded far less accurately than position/length (Cleveland & McGill 1984) | Scatter + color, or direct value labels on each bubble |
| Stacked area (many series) | Only bottom series is readable | Line chart per series |

Bubble charts are not banned outright: per Cleveland & McGill (1984), position along a common
scale and length are judged far more accurately than area/size, so size-encoded charts are the
wrong choice whenever the audience needs to read off precise values. They're still acceptable for
coarse/ordinal signal ("roughly bigger vs. smaller") — see the Size attribute in
`references/pre-attentive-attributes.md`. If you do use one, direct-label the values on the
bubbles by default; don't rely on the reader decoding size from a legend.
