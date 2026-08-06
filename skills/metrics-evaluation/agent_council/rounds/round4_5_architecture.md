# Rounds 4 and 5: Architecture

## Round 4 Proposals

Three reviewers evaluated a domain/topic hierarchy.

Shared conclusions:

- Cross-domain methods belong under `topics/`.
- Specialized evaluation overlays belong under `domains/`.
- Provenance belongs under `references/`.
- Structured-output matching is reusable and should not be duplicated in each vision guide.
- Recommendation remains an application domain because candidate, exposure, cold-start,
  feedback-loop, and online semantics are product-specific.
- Representation learning requires specialized routing even though it spans modalities.
- Old paths should move atomically without compatibility copies unless an external
  consumer is known.

Main disagreement:

- One proposal added `task_families/`; the others rejected a third taxonomy.
- One proposal nested every domain deeply; another preferred flat domain files.
- Reviewers differed on whether structured matching belonged in vision or core.

## Round 5 Chair Decision

The chair selected `topics/`, `domains/`, and `references/` as the only normative root
taxonomies. Structured matching moved to core. Diagnostic material was split into general
and domain-specific ownership. The implementation used grouped `customer_analytics/`
and `vision/` directories for clearer domain navigation while preserving direct routes
from `SKILL.md`.

## Ownership Rule

Each concept has one canonical owner. Core defines universal rules; decision topics
define generic action/value translation; diagnosis defines investigation structure;
reporting defines conclusions; domains define specialized estimands and protocols.
