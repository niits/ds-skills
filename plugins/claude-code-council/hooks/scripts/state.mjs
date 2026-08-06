/**
 * Shared run-state access for the council hooks.
 *
 * One state file per working directory, outside the repository. The chair
 * writes the plan through council-state.mjs; the hooks own everything else,
 * so the delegation tree records what happened rather than what was intended
 * (SRS-common FR-340).
 *
 * Stock Node only — no dependencies (D2-FR-002).
 */

import { createHash } from "node:crypto";
import {
  closeSync,
  existsSync,
  mkdirSync,
  openSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const LOCK_RETRY_MS = 50;
const LOCK_TIMEOUT_MS = 3000;
const LOCK_STALE_MS = 30000;

export function stateDir(cwd) {
  const key = createHash("sha256").update(cwd).digest("hex").slice(0, 16);
  return join(tmpdir(), "claude-code-council", key);
}

export const statePath = (cwd) => join(stateDir(cwd), "state.json");
export const planPath = (cwd) => join(stateDir(cwd), "plan.json");
const lockPath = (cwd) => join(stateDir(cwd), "lock");

/** null when no council is running here; throws when the file is unreadable. */
export function readState(cwd) {
  const p = statePath(cwd);
  if (!existsSync(p)) return null;
  return JSON.parse(readFileSync(p, "utf8"));
}

export function writeState(cwd, state) {
  mkdirSync(stateDir(cwd), { recursive: true });
  writeFileSync(statePath(cwd), `${JSON.stringify(state, null, 2)}\n`);
}

export function clearState(cwd) {
  rmSync(stateDir(cwd), { recursive: true, force: true });
}

function sleepSync(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

/**
 * Several Task calls in one assistant turn mean several hook processes racing
 * for the same file. Without this the member ceiling would be advisory.
 */
export function withLock(cwd, fn) {
  mkdirSync(stateDir(cwd), { recursive: true });
  const lock = lockPath(cwd);
  const deadline = Date.now() + LOCK_TIMEOUT_MS;

  for (;;) {
    try {
      closeSync(openSync(lock, "wx"));
      break;
    } catch (err) {
      if (err.code !== "EEXIST") throw err;
      try {
        if (Date.now() - statSync(lock).mtimeMs > LOCK_STALE_MS) {
          rmSync(lock, { force: true });
          continue;
        }
      } catch {
        continue; // vanished between the two calls; retry the create
      }
      if (Date.now() >= deadline) {
        throw new Error("timed out waiting for the council state lock");
      }
      sleepSync(LOCK_RETRY_MS);
    }
  }

  try {
    return fn();
  } finally {
    rmSync(lock, { force: true });
  }
}

/**
 * Plugin agents arrive as "plugin-name:agent-name"; the same agent invoked by
 * bare name arrives without the prefix. Both mean the same role.
 */
export function normalizeRole(subagentType) {
  if (typeof subagentType !== "string") return "";
  const i = subagentType.lastIndexOf(":");
  return (i === -1 ? subagentType : subagentType.slice(i + 1)).trim();
}

export function readStdinJson() {
  let raw = "";
  try {
    raw = readFileSync(0, "utf8");
  } catch {
    return {};
  }
  if (!raw.trim()) return {};
  return JSON.parse(raw);
}
