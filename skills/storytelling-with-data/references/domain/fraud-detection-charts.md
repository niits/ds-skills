# Fraud Detection Chart Patterns

Visualization patterns for fraud monitoring, anomaly detection, and transaction surveillance.

Key difference from credit risk: fraud analytics is often **real-time** or **near-real-time**,
and the audience alternates rapidly between operational analysts (alert triage) and
management (trend reporting). Charts must support both fast triage decisions and
periodic review.

---

## 1. Transaction Time Series with Anomaly Enclosure

**Use when:** Showing transaction volume or fraud rate over time with detected anomaly windows.
The enclosure (shaded region) directs the eye to the period under investigation.

**Audience:** Operations analysts, fraud managers

**Required inputs:**
- `dates` — ordered array of dates (daily or hourly)
- `values` — metric values at each date (e.g. transaction volume, fraud count)
- `anomaly_windows` *(optional)* — list of `(start_date, end_date, label)` tuples marking detected anomaly periods
- `metric_label` — y-axis label (e.g. "Transaction Volume", "Fraud Count")

**Key design decisions:**
- Plot the raw metric as a thin gray line; overlay a 7-day rolling average as the "expected" reference
- Shade anomaly windows with a semi-transparent enclosure; label each window with the anomaly description
- The shaded region is the primary pre-attentive cue — it replaces the need for the audience to hunt for the anomaly themselves

---

## 2. Fraud Rate Trend — Dual View (Volume + Rate)

**Use when:** Management needs to see both absolute fraud volume and the fraud rate
(% of transactions) simultaneously without a dual y-axis.
Solution: two separate panels stacked vertically, sharing the x-axis.

**Audience:** Fraud managers, operations head

**Required inputs:**
- `dates` — ordered date array
- `txn_volume` — total transaction count per period
- `fraud_count` — number of fraudulent transactions per period
- `fraud_rate` — fraud rate per period (fraud_count / txn_volume × 100)

**Key design decisions:**
- Top panel: fraud count as bars (absolute volume); accent the peak bar
- Bottom panel: fraud rate as a filled line chart (relative trend)
- Panels share the x-axis; no dual y-axis (dual y-axis makes the visual relationship between two arbitrary scales misleading)

---

## 3. Scatter: Amount vs Frequency — Outlier Labeling

**Use when:** Identifying suspicious accounts or merchants by transaction pattern.
High-amount or high-frequency outliers are the primary signal.

**Audience:** Fraud investigators, operations analysts

**Required inputs:**
- `amounts` — average transaction amount per entity (account or merchant)
- `frequencies` — transaction count per entity
- `labels` *(optional)* — entity identifiers (account ID, merchant name)
- `outlier_mask` — boolean array; `True` for entities to highlight as suspicious

**Key design decisions:**
- Plot all entities as gray points; overlay outliers in the accent color
- Label only the accented outlier points, not every point
- Gray the majority so that the outliers are immediately pre-attentive
- Annotate percentile reference lines (e.g. 95th percentile thresholds) if useful for context

---

## 4. Calendar Heatmap — Fraud by Day and Hour

**Use when:** Identifying when fraud concentrates (day of week × hour of day).
Reveals operational patterns: overnight spikes, weekend clusters, etc.

**Audience:** Operations analysts, fraud strategy team

**Required inputs:**
- `df_pivot` — pivot table with:
  - index = day of week (Mon–Sun), 7 rows
  - columns = hour of day (0–23), 24 columns
  - values = fraud rate (%) or fraud count per cell

**Key design decisions:**
- Use a perceptually-uniform sequential colormap (e.g. YlOrRd)
- 168 cells (7 × 24) is too many to annotate fully — annotate only cells above the 90th percentile value
- The color gradient reveals time-of-day and day-of-week patterns at a glance

---

## 5. Z-Score / Rolling Deviation — Real-Time Alert Context

**Use when:** Communicating to management why an alert was triggered.
Shows the metric, its expected range (rolling mean ± σ), and the deviation.

**Audience:** Fraud managers, operations head

**Required inputs:**
- `dates` — ordered date array
- `values` — daily metric values (e.g. fraud amount in VND)
- `window` — rolling window size for computing mean and std (e.g. 30 days)
- `z_threshold` — number of standard deviations that defines an alert (e.g. 2.5)
- `metric_label` — y-axis label

**Key design decisions:**
- Compute rolling mean and ± z_threshold × std band; shade the expected range
- Plot the raw metric line over the shaded band
- Mark alert-triggered points (where |z-score| > threshold) as accent-colored dots
- This chart contextualizes *why* the alert fired, not just that it fired

---

## Network Graphs

Transaction network analysis (graph of accounts, merchants, devices) is outside
the scope of standard notebook charts. Use:

- **Gephi** or **NetworkX + pyvis** for exploratory network viz
- **GraphFrames** (Databricks native) for large-scale graph queries
- In presentations: export a static snapshot and annotate the key cluster manually
  using PowerPoint or Figma rather than trying to render a live network in a notebook

---

## Audience Guide

| Chart | Analyst (triage) | Fraud Manager | Executive |
|---|---|---|---|
| Transaction time series + anomaly | required | required | for context only |
| Fraud dual panel (volume + rate) | — | required | ✓ |
| Scatter: amount vs frequency | required | for review | — |
| Calendar heatmap | ✓ | ✓ | — |
| Rolling z-score | required | required | — |
