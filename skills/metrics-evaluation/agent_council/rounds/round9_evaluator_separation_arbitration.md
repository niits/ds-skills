# Round 9: Comparator, Metric, and Evaluator Separation

## Question

Does the normative corpus clearly separate hard-decision comparators, score/ranking
comparators, and implementation-dependent metric behavior so that an agent cannot apply
one as though it were another?

## Roster

| Member | Role |
|---|---|
| M1 | Classification baseline and statistical-validity reviewer |
| M2 | Ranking and information-retrieval reviewer |
| M3 | Metric implementation and reproducibility reviewer |
| M4 | Skill information-architecture reviewer |
| Chair | Scope arbitration and final decision |

All members reviewed independently and communicated in English. They had read-only access;
the primary agent retained responsibility for edits and verification.

## Consensus

The existing material mixed three concerns:

1. Comparator construction: what labels, scores, rankings, forecasts, or alerts a baseline
   emits.
2. Metric interpretation: what the resulting number means and which claim it supports.
3. Evaluator semantics: how representation, ties, interpolation, candidates, undefined
   cases, and software conventions produce that number.

The council unanimously rejected splitting baselines into classification and ranking files.
A binary-label task may require both hard decisions and score rankings, so emitted output
is the stable boundary.

## Confirmed Defects

| Defect | Consequence | Ruling |
|---|---|---|
| All-negative was called majority unconditionally | Wrong when positives are the majority | Rename and qualify |
| AP was attached to a hard all-negative predictor | Hard labels do not define AP without scores | Separate score representation |
| Every ranking metric was required to have `k` | Full-list AP, MAP, and AUC need no artificial cutoff | Require `k` only when applicable |
| Finite-sample random-order AP was treated as prevalence | Can be materially wrong for small lists | Use exact or frozen-evaluator permutations |
| Isotonic ties were said to preserve AP/AUC | Non-decreasing maps can change both | Recompute after calibration |
| Point-adjustment inflation was called unbounded | Absolute change of a `[0,1]` metric is bounded | Distinguish absolute and relative inflation |
| Popularity was a universal ranking bar | Irrelevant or exposure-confounded in many tasks | Make it conditional |
| Ranking evaluator contracts were incomplete | MAP/NDCG values could be incomparable | Freeze candidates, ties, gains, zero cases, and aggregation |
| Generic retrieval routed to representation learning | Implied an encoder claim that may not exist | Route generic retrieval to core files |

## Chair's Arbitration

- Keep one comparator-oriented `topics/core/baselines.md` organized by emitted output.
- Add conditional `topics/core/evaluator_semantics.md` as the sole primary owner of
  implementation-dependent behavior.
- Keep metric meaning in `topics/core/metric_interpretation.md`.
- Keep population, split, uncertainty, and comparison validity in
  `topics/core/evaluation_protocol.md`.
- Tighten `SKILL.md` routing by concern and preserve selective domain loading.
- Move content rather than retain duplicate definitions.

## Rejected Alternatives

- Separate hard-classification and ranking baseline files: rejected because output uses
  overlap within the same task.
- Universal popularity comparator: rejected because relevance is domain- and policy-specific.
- Universal `k`: rejected because not all ranking metrics are truncated.
- Generic retrieval domain expansion: deferred; core semantics are sufficient for this fix.
- Executable evaluator fixtures and library matrix: useful future work, but outside this
  documentation-boundary remediation.

## Verification Contract

Acceptance requires all normative paths to resolve, every normative file to be routed,
valid frontmatter, no council file in normal routing, no superseded factual claims, and no
more than five percent normative line growth from the 1,905-line Round 8 baseline.

## Verdict

The architecture and required factual corrections were accepted for implementation. Final
acceptance depends on post-edit verification recorded in the debate log.
