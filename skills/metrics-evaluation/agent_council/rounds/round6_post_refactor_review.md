# Round 6: Post-Refactor Review

## Passing Reviews

The vision reviewer passed structured fixtures, OCR structure semantics, open-set
detection, tracking deployment requirements, and grouped vision routes.

The representation reviewer passed routing, clustering, rare-operating-point support,
broad-claim breadth, contamination status, hierarchical variation, and report fields.

## Blocking Findings

The statistical reviewer found:

- An equality overlap in useful-margin interval rules.
- Economics still required unconditionally in the fast diagnostic path.
- Categorical causes remained in legacy domain tables.
- Recommendation retained ambiguous useful-margin wording.

The architecture reviewer found:

- A centralized domain-pattern file still loaded unrelated domains.
- Legacy domain tables contradicted the hypothesis-based contract.
- Generic KPI guidance duplicated domain-specific material.

## Remediation

- Made interval cases mutually exclusive.
- Made economics conditional on the requested conclusion.
- Rewrote domain failure tables as hypotheses and discriminating checks.
- Removed the centralized domain-pattern file; domain diagnostics now live in domain guides.
- Replaced domain-heavy KPI material with a generic mapping procedure.
- Clarified recommendation conclusions below versus spanning the useful margin.
