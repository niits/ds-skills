# Metrics Evaluation Council Debate Log

## Council Roles

- Statistical Validity Reviewer
- Computer Vision Evaluation Reviewer
- Representation Learning Reviewer
- Skill Architecture and Practitioner Usability Reviewer
- Council Chair

## Process

The council used independent review, cross-examination, scoped arbitration,
architecture challenge, post-refactor adversarial review, remediation, and final
verification. Reviewers did not edit files directly. The primary agent applied only
accepted changes and retained responsibility for validation.

## Round Summary

| Round | Purpose | Outcome |
|---|---|---|
| 1 | Independent specialist reviews | Found statistical decision ambiguity, routing conflicts, structured-output gaps, representation gaps, and progressive-disclosure issues |
| 2 | Cross-examination and rebuttal | Converged on a compact high-risk patch set and downgraded several expansive proposals |
| 3 | Scope arbitration | Accepted eight focused semantic changes; initially deferred structural decomposition |
| 4 | Architecture proposals after explicit refactor request | Compared domain/topic trees and ownership boundaries |
| 5 | Architecture chair decision | Selected `topics/`, `domains/`, and `references/`; required diagnostic decomposition |
| 6 | Post-refactor adversarial review | Vision and representation passed; statistical and architecture reviewers found four remaining blockers |
| 7 | Final verification after remediation | No blockers; unanimous acceptance |
| 8 | Adversarial correctness and effectiveness audit | Correctness confirmed strong; one binary-only baseline formula bug, three stale root-README paths, credit/fraud coverage regression, four citation-hygiene defects, five uncovered task families |

## Key Decisions

- `topics/core/evaluation_protocol.md` is the sole universal supporting route.
- Topic files own cross-domain methods; domain files own specialized estimands and protocols.
- Structured-output matching is a core topic because it is reusable across domains.
- Vision guides remain separate because OCR, detection, and tracking use different outputs and evaluator semantics.
- Economics, diagnosis, structured-output evidence, and representation evidence use conditional report profiles.
- Paired conclusions against zero and against a useful margin are reported separately.
- Diagnostic patterns state signals, compatible hypotheses, and discriminating checks rather than asserting causes.
- Domain-specific diagnostics remain in domain guides; the diagnosis topic contains only cross-domain patterns.
- Council records remain excluded from skill routing.

## Deferred or Rejected Expansion

- No third `task_families/` taxonomy was added because it would compete with domain/topic routing.
- No exhaustive algorithm survey or evaluator-fixture library was added; the skill defines contracts rather than project-specific implementations.
- No compatibility stubs were retained for old paths because no external path consumer was established.
- Domain guides were not split into many small files after selective routing became sufficient.

## Final Status

The chair accepted the refactored skill after Round 7. Residual risks are implementation
compliance with evaluator contracts and the length of several domain guides; neither was
considered release-blocking.

Round 8 reopened the skill for an adversarial correctness and effectiveness audit, then
applied user-authorized remediation. Vision (OCR, object detection, multi-object tracking)
and its orphaned `structured_output_matching.md` dependency were removed on user
instruction; credit and fraud stay deleted by user decision, with the root README updated
to state the gap rather than imply coverage. Multi-class, multi-label, probabilistic
forecasting, and the anomaly point-adjustment trap were added. All ten reported defects
were fixed. The audit
confirmed the statistical content is sound — including the paired-interval decision table
and all 16 citations — but found ten defects and five uncovered task families. It also
falsified a Round 3 premise: the decision to retain no compatibility stubs for old paths
assumed no external path consumer existed, but the root `README.md` is one and still
carries stale `foundations/` and `business/` references. See
`rounds/round8_correctness_and_effectiveness_audit.md`. No files outside `agent_council/`
were modified.
