#!/usr/bin/env node
/**
 * PreToolUse gate on Task (D2-FR-030, D2-FR-031).
 *
 * Answers one question: is this spawn one the armed plan called for, and is
 * there room for it? Everything that is judgment rather than capacity — role
 * diversity, task independence, the quality of a member's question — is the
 * chair's job and lives in commands/council.md (SRS-D2 §6).
 *
 * Allow is expressed by staying silent, so the user's own permission settings
 * still apply. Only a denial speaks.
 *
 * Nothing here exits the process while the lock is held: process.exit skips
 * finally blocks, which would leave the lockfile behind. The lock computes a
 * decision; the decision is acted on afterwards.
 */

import { normalizeRole, readState, readStdinJson, withLock, writeState } from "./state.mjs";

const ALLOW = { allow: true };
const denial = (reason) => ({ allow: false, reason });

function emit(decision) {
  if (decision.allow) process.exit(0); // no output: defer to the normal permission flow
  process.stdout.write(
    `${JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: decision.reason,
      },
    })}\n`,
  );
  process.exit(0);
}

function decide() {
  let input;
  try {
    input = readStdinJson();
  } catch {
    return ALLOW; // cannot read the event; not this council's business
  }

  if (input.tool_name !== "Task") return ALLOW;

  const cwd = input.cwd || process.cwd();
  const sessionId = input.session_id || "";
  const role = normalizeRole(input.tool_input?.subagent_type);

  try {
    if (readState(cwd) === null) return ALLOW; // no council here; ordinary work
  } catch {
    // A state file exists but is unreadable. Fail closed (D2-FR-033): we cannot
    // tell whether this spawn is within the ceiling, so we do not permit it.
    return denial(
      "Council state is unreadable, so this spawn cannot be checked against the plan. " +
        "Clear the run with `council-state.mjs end` and start again.",
    );
  }

  return withLock(cwd, () => {
    const state = readState(cwd);
    if (state === null) return ALLOW;

    // A file bound to another session belongs to another session's council.
    // Not ours to gate — denying here would break unrelated work in a second
    // session open on the same directory.
    if (state.sessionId && state.sessionId !== sessionId) return ALLOW;
    if (!state.sessionId) state.sessionId = sessionId;

    const refuse = (reason) => {
      state.denied.push({ at: new Date().toISOString(), role, round: state.currentRound, reason });
      writeState(cwd, state);
      return denial(reason);
    };

    if (!state.armed) {
      return refuse(
        "No plan has been armed for this council. Write the plan and run " +
          "`council-state.mjs arm` before spawning any member.",
      );
    }

    if (state.currentRound > state.ceilings.rounds) {
      return refuse(
        `Round ceiling reached (${state.ceilings.rounds}). Synthesize from the results you have.`,
      );
    }

    if (state.approved.length >= state.ceilings.members) {
      return refuse(
        `Member ceiling reached (${state.ceilings.members} members already approved this run).`,
      );
    }

    const planned = state.plan.filter(
      (m) => m.round === state.currentRound && normalizeRole(m.role) === role,
    );
    if (planned.length === 0) {
      return refuse(
        `"${role || "(no subagent_type)"}" is not in the armed plan for round ` +
          `${state.currentRound}. Members come from the plan; amend the plan and re-arm if the ` +
          "roster needs to change.",
      );
    }

    const alreadyApproved = state.approved.filter(
      (a) => a.round === state.currentRound && a.role === role,
    ).length;
    if (alreadyApproved >= planned.length) {
      return refuse(
        `The plan calls for ${planned.length} "${role}" member(s) in round ${state.currentRound}; ` +
          `${alreadyApproved} have already been spawned.`,
      );
    }

    state.approved.push({
      role,
      round: state.currentRound,
      approvedAt: new Date().toISOString(),
      agentId: null,
      startedAt: null,
      stoppedAt: null,
      outcome: null,
    });
    writeState(cwd, state);
    return ALLOW;
  });
}

let decision;
try {
  decision = decide();
} catch (err) {
  decision = denial(`Council gate could not record this spawn (${err.message}), so it was refused.`);
}
emit(decision);
