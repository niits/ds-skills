# Domain: Lead Scoring

Lead scoring ranks prospects by likelihood to convert. The output is a
**prioritization list for sales**, not a yes/no decision — so it is fundamentally a
**ranking** problem. This is usually **GBM mode**. (For metric choice, see the
`metrics-evaluation` skill's `domains/lead_scoring.md`; this file is about *features*.)

---

## Ranking framing changes what "good feature" means

The model's job is to order leads so the top-k (k = sales capacity) is enriched with
converters. Therefore:
- A feature that improves **separation in the high-score region** matters more than one
  that improves average calibration. When measuring incremental lift (Phase 5), weight
  **Precision@k / lift@k** alongside Gini, where k is the realistic SDR capacity.
- Don't over-optimize IV on the full distribution if the gain is all in the bottom
  deciles sales will never call.

---

## Feature latency — a point-in-time trap specific to lead data

Lead/CRM data is full of fields that are **back-filled after the outcome**:
- `last_activity_date`, `meeting_booked`, `demo_completed`, `mql_to_sql_date` — many
  are populated *because* the lead engaged, i.e. they are early steps of the very
  conversion you predict.
- Enrichment vendors update firmographics asynchronously; the value you see *today*
  may not have existed at scoring time.

Apply the temporal audit in `references/leakage_and_tautology.md` rigorously: the
feature snapshot must reflect only what was known **at the moment the lead would be
scored** (typically lead-creation or MQL time), not the enriched present state.

> Classic leak: `number_of_sales_touches` as a feature. Sales touch the leads they
> *already* think are good (or that already engaged) → it encodes the outcome and the
> sales team's judgment, not the lead's intrinsic propensity. Tautology + selection.

---

## Selection bias on contacted leads

Your label ("converted") is observed only for leads that were **worked**. Leads sales
never called have no conversion outcome — they look like negatives but are really
**unknown**. This biases every IV/lift number toward the behavior of the
already-prioritized population.

- Be explicit about the label's denominator: contacted leads vs all leads.
- Features that correlate with *who sales chose to call* (territory, account size,
  inbound vs outbound) partly measure the existing prioritization, not lead quality.
  Decide whether you want to model intrinsic propensity (debias) or the current funnel.

---

## Label timing and the embargo

Conversions happen days-to-weeks after the lead is scored. Define:
- **Cutoff T** = scoring moment (lead creation / MQL).
- **Embargo** = none-to-short, but the **label window** must start at T and look
  *forward* (did this lead convert within H days?). Never let activity from after T
  leak into the features.

---

## Phase deltas summary

| Phase | Lead-scoring adjustment |
|---|---|
| 2 | Prefer intrinsic-behavior features; be wary of funnel-state features that encode sales' own choices |
| 5 | Measure lift with Precision@k / lift@k at realistic SDR capacity, not just Gini |
| 6 | Audit CRM/enrichment fields for back-fill; drop sales-touch and engagement-outcome proxies |
| 9 | Note label = contacted-lead population; flag selection-bias-laden features |
