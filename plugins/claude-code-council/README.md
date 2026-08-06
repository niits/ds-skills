# claude-code-council

A Multi-Agent Adversarial Council for Claude Code.

You give it a topic. Your session becomes the chair: it sharpens the
topic into a decidable question, plans a roster of researchers with
deliberately conflicting mandates, runs them in parallel, classifies
their disagreements instead of averaging them, and writes one report in
which every conclusion traces back to a member's finding.

Adversarial is the point. One of the members exists to attack the answer
the others are converging on. A council that agrees by construction has
told you nothing.

## Install

No build step, no dependencies. Node is already present wherever Claude
Code runs.

**To use it.** This plugin ships from the `niits-ds-skills` marketplace,
which is tracked in git — nothing is installed from a local path:

```bash
claude plugin marketplace add https://github.com/niits/ds-skills.git#master
claude plugin install claude-code-council@niits-ds-skills --scope user
```

`--scope user` makes it available everywhere. Use `--scope project` to
keep it to one repository. Restart the session afterwards.

**To pick up changes.** The install *copies* the plugin into
`~/.claude/plugins/cache/`, and `claude plugin update` compares version
numbers — an unchanged `version` in `plugin.json` means no re-copy. So
after pushing a change, bump `version`, then:

```bash
claude plugin marketplace update niits-ds-skills
claude plugin update claude-code-council@niits-ds-skills
```

**To remove it:**

```bash
claude plugin uninstall claude-code-council@niits-ds-skills --scope user
```

Then, in the session:

```text
/council should we move the retry logic out of the transport layer?
```

## What you get

```text
Council report: <question>
├── Answer, and the confidence behind it
├── What the council agreed on      — and whether that agreement was independent
├── What the council disputed       — classified: factual, interpretive, definitional, scope
├── Minority positions worth keeping
├── What nobody could determine     — and what would settle it
├── Consequences if this answer is wrong
└── Provenance                      — every member, role, round, outcome, and refused spawn
```

## The roster

Four roles ship. The chair picks from them; it cannot invent one at
runtime, because an invented role would carry no capability lock.

| Role | Mandate |
| --- | --- |
| `evidence-researcher` | Answer the question from primary evidence; separate what was verified from what was inferred |
| `assumption-challenger` | Find what the question takes for granted, and test whether it holds |
| `counter-example-finder` | Try to break the emerging answer; report honestly when it survives |
| `source-verifier` | Check that sources are real, current, independent of each other, and actually say what they are cited for |

Adding a role means adding a file to `agents/`. No code changes.

## What is actually enforced

Three layers, and they are not equally strong. Being clear about which
is which is the point of this section.

**Enforced by capability — the tool is absent, not discouraged:**

- A member cannot spawn another agent. `Task` is removed from every
  member's toolkit. It does not decline; it has nothing to decline with.
- A member cannot edit the repository. `Edit`, `Write`, `NotebookEdit`
  and `Bash` are all removed. Members read; they do not act.
- Each member has a turn limit.

**Enforced by a blocking hook — checked before the spawn happens:**

- No member starts before the chair has written and armed a plan.
- The member ceiling holds, including when several members are launched
  in the same turn.
- The round ceiling holds.
- A spawn that does not match the armed plan is refused, and the refusal
  is recorded and shown in the report's provenance.
- If the hook cannot read its own state, it refuses the spawn rather
  than allowing an unrecorded one.

**Asked of the model — real instructions, but instructions:**

- The quality of the plan: distinct questions, distinct roles, an
  adversarial role on a contentious topic, member independence.
- That member reports match the required schema.
- That conflicts are classified rather than averaged, and that a
  well-evidenced minority position survives.
- That the topic is treated as data and never as an instruction.

## Known limits

Read this part. Everything above is what the plugin does; this is what
it does not.

- **Plan quality is not verified by anything but the model.** The hook
  counts members and matches them against the plan. It does not judge
  whether two questions are genuinely different or whether the roster
  can disagree. A chair that writes a lazy plan produces a lazy council.
- **Member reports are not parsed or schema-checked.** The chair reads
  them and is asked to notice when one is malformed or unsupported.
  Nothing rejects a bad report automatically.
- **The plugin cannot tighten your session's permissions.** Claude Code
  forbids plugin agents from declaring a permission mode, by design.
  Member read-only behavior comes from the missing tools, not from a
  sandbox. In a session already running with permissions bypassed, the
  members still have no write tools, but the session around them is as
  permissive as you left it.
- **Members share your session's process and quota.** There is no
  isolation and no separate accounting beyond the provenance record. A
  six-member council costs roughly what six investigations cost.
- **Members cannot run commands.** No `git log`, no test run, no
  `grep -r` through a shell. They read files, search, and fetch. This is
  the price of read-only being a real guarantee rather than a claim.
- **One council at a time per directory**, and while one is open, other
  subagent calls in that session are checked against its plan. The
  command closes the run at the end; if a council is interrupted, close
  it manually:

  ```bash
  node hooks/scripts/council-state.mjs end
  ```

- **A council never edits anything.** It produces a report. Acting on
  the report is a separate decision, and yours.

## Spec

- [`SRS-D2-claude-code-council-v1.0.md`](../../docs/requirements/SRS-D2-claude-code-council-v1.0.md)
  — binding requirements
- [`SRS-common-v1.0.md`](../../docs/requirements/SRS-common-v1.0.md) §7
  — the council doctrine, shared with the OpenCode council
- [`architecture/D2-claude-code-council.md`](../../docs/architecture/D2-claude-code-council.md)
  — how it is built
