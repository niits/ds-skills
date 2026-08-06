#!/usr/bin/env node
/**
 * SubagentStart: bind a real agent id to the approval the gate recorded
 * (D2-FR-032). Never blocks — this hook observes, it does not decide.
 */

import { normalizeRole, readState, readStdinJson, withLock, writeState } from "./state.mjs";

try {
  const input = readStdinJson();
  const cwd = input.cwd || process.cwd();
  const role = normalizeRole(input.agent_type);
  const agentId = input.agent_id || null;

  if (readState(cwd) !== null) {
    withLock(cwd, () => {
      const state = readState(cwd);
      if (state === null) return;
      if (state.sessionId && input.session_id && state.sessionId !== input.session_id) return;

      const slot =
        state.approved.find((a) => a.agentId === agentId) ??
        state.approved.find((a) => a.role === role && a.agentId === null);
      if (!slot) return; // a subagent this council did not approve; the gate has the record

      slot.agentId = agentId;
      slot.startedAt = new Date().toISOString();
      writeState(cwd, state);
    });
  }
} catch {
  // Observation only. A failure here must not disturb the run.
}

process.exit(0);
