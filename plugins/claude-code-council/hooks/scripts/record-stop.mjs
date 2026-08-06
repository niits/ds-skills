#!/usr/bin/env node
/**
 * SubagentStop: close out the member's entry in the delegation tree
 * (D2-FR-032). Never blocks the subagent from stopping.
 */

import { readState, readStdinJson, withLock, writeState } from "./state.mjs";

try {
  const input = readStdinJson();
  const cwd = input.cwd || process.cwd();
  const agentId = input.agent_id || null;

  if (agentId && readState(cwd) !== null) {
    withLock(cwd, () => {
      const state = readState(cwd);
      if (state === null) return;
      if (state.sessionId && input.session_id && state.sessionId !== input.session_id) return;

      const slot = state.approved.find((a) => a.agentId === agentId);
      if (!slot) return;

      slot.stoppedAt = new Date().toISOString();
      slot.outcome = input.stop_reason || "unknown";
      writeState(cwd, state);
    });
  }
} catch {
  // Observation only.
}

process.exit(0);
