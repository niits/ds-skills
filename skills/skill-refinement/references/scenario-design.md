# Scenario Design

Scenarios are lightweight behavioral tests for a skill. Write them before proposing edits so the
refinement is judged against outcomes rather than the rewritten text.

## Scenario Set

Use the smallest set that covers the skill's meaningful boundaries:

1. **Positive:** a core request that should activate the skill and complete its primary workflow.
2. **Negative:** a nearby request that should not activate the skill or should route elsewhere.
3. **Ambiguous:** missing information that should trigger one focused question or a scoped default.
4. **Failure or safety:** invalid evidence, unavailable tooling, dangerous input, or a hard stop.
5. **Verification:** a completed task where the agent must prove the result rather than assert it.

Add domain or implementation variants only when they exercise materially different behavior.

## Scenario Format

```markdown
### S1: Short name

- User request: Realistic request in the user's language
- Preconditions: Files, state, permissions, or evidence available
- Expected activation: Load | Do not load | Route to another skill
- Expected behavior: Observable decisions and actions in order
- Files to load: Minimum supporting material needed
- Must not: Specific overreach, unsafe action, or unsupported claim
- Pass signal: Output or command result that demonstrates success
```

## Evaluation Rules

- Use realistic requests, not wording copied from the skill description.
- Test decisions and outputs; do not require exact prose.
- Include at least one boundary where over-triggering would be plausible.
- Include one scenario that exercises progressive disclosure when the skill has supporting files.
- Preserve the pre-refinement result as the baseline: pass, partial, fail, or cannot determine.
- A proposed change must name the scenarios it improves and any scenario it risks regressing.

When direct execution is unavailable, perform a trace: follow the routing and instructions exactly,
record the files that would load, and identify the first ambiguous or unsupported decision. Label a
trace as simulated; do not present it as a runtime test.

Activation behavior must be tested in a fresh session where only skill discovery metadata is
initially visible. Run positive and negative prompts separately in each claimed client when those
clients are available; otherwise mark client activation as unverified.
