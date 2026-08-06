# Domain: Lead Scoring

Lead scoring ranks prospects by likelihood to convert. The output is a
**prioritization list for sales**, not a yes/no decision — so it is fundamentally a
**ranking** problem. This is usually **GBM mode**. (For metric choice, see the
`metrics-evaluation` skill's `domains/customer_analytics/lead_scoring.md`; this file is
about *features*.)

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

> Post-score sales touches are leakage. Strictly pre-score touches may be valid for a
> policy-specific conversion estimand, but they encode historical sales policy and
> require explicit selection-bias and deployment-policy review.

---

## Selection bias on contacted leads

First establish whether conversion is observed for all leads or only worked leads, and
whether contact merely reveals conversion or causally changes it. Unworked leads are
unknown/censored only when the data-generating process establishes that; they are not
universally negatives or unknowns.

- Be explicit about the target estimand, label denominator, historical contact policy,
  overlap/propensity information, and whether the full outcome horizon had matured at
  extraction. Prevent the same account/person/opportunity from crossing folds when
  repeated leads share outcomes or features.
- Features that correlate with *who sales chose to call* (territory, account size,
  inbound vs outbound) partly measure the existing prioritization, not lead quality.
  Decide whether you want policy-specific conversion, response under contact, or an
  untreated propensity. The latter is not identified from policy-selected observational
  data without defensible assumptions, overlap, instrumentation, or experimentation.

---

## Label timing and the embargo

Conversions happen days-to-weeks after the lead is scored. Define:
- **Cutoff T** = scoring moment (lead creation / MQL).
- **Gap** = optional and justified by the estimand or latency. Declare transaction
  ordering; absent a stable event-sequence key, use `(T, T+H]` for outcomes. Never let activity from after T
  leak into the features.

---

## Phase deltas summary

| Phase | Lead-scoring adjustment |
|---|---|
| 2 | Prefer intrinsic-behavior features; be wary of funnel-state features that encode sales' own choices |
| 5 | Measure lift with Precision@k / lift@k at realistic SDR capacity, not just Gini |
| 6 | Audit CRM/enrichment fields for back-fill; drop sales-touch and engagement-outcome proxies |
| 9 | Record the actual label-observation population and flag contact-policy selection where outcomes are observed or affected selectively |
