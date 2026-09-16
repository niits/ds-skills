# Refinement Proposal Template

Keep the proposal proportional to the target skill. Omit empty sections, but always include the
behavioral contract, evidence-backed findings, exact scope, verification, and approval request.

```markdown
# Refinement Proposal: <skill-name>

## Behavioral Contract

- User and problem:
- Activate when:
- Owns:
- Does not own:
- Hard stops:
- Completion signal:

## Baseline Scenarios

| ID | Scenario | Current result | Intended result |
|---|---|---|---|
| S1 | ... | Pass / Partial / Fail / Unknown | ... |

## Findings

List findings by severity. For each one include status, `path:line` evidence, behavioral impact,
smallest correction, and affected scenarios.

## Proposed Changes

| File | Change | Reason | Scenarios |
|---|---|---|---|
| `path` | Exact edit, addition, move, or deletion | Finding resolved | S1, S3 |

## Validation Plan

- Exact deterministic repository commands to run
- Scenario traces or runtime evaluations to repeat
- Client-specific discovery or manifest validation
- Isolation, credential, and network boundaries for any target-bundled code execution

## Risks And Assumptions

- Assumptions still requiring confirmation
- Behavior that could regress
- Checks unavailable in the current environment

## Not Doing

- Plausible improvement intentionally excluded and why

## Approval

Approve the full proposal, approve selected rows, request changes, or reject it. No target files
will be edited until approval is explicit.
```

Do not hide uncertain scope inside implementation details. If approval depends on a product,
domain, licensing, or compatibility choice, ask that question before requesting approval.
