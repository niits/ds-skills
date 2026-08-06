#!/usr/bin/env node
/**
 * The chair's interface to the run state.
 *
 *   begin  <members> <rounds>   open a run; print where to write the plan
 *   arm                         validate plan.json and open the gate
 *   round  <n>                  advance to round n
 *   tree                        print the delegation record for the report
 *   end                         close the run and delete its state
 *
 * The plan arrives as a file the chair writes, not as a command-line argument.
 * A topic is user-controlled text that ends up inside member questions; it must
 * never be assembled into a shell command (SRS-common NFR-004).
 */

import { existsSync, readFileSync } from "node:fs";
import { randomUUID } from "node:crypto";
import {
  clearState,
  normalizeRole,
  planPath,
  readState,
  stateDir,
  withLock,
  writeState,
} from "./state.mjs";

const cwd = process.cwd();
const [command, ...args] = process.argv.slice(2);

function fail(message) {
  process.stderr.write(`${message}\n`);
  process.exit(1);
}

function requireRun() {
  let state;
  try {
    state = readState(cwd);
  } catch {
    fail("Council state is unreadable. Run `end` to clear it, then `begin` again.");
  }
  if (state === null) fail("No council is running here. Run `begin` first.");
  return state;
}

function positiveInt(value, name, fallback) {
  if (value === undefined) return fallback;
  const n = Number(value);
  if (!Number.isInteger(n) || n < 1) fail(`${name} must be a positive integer, got "${value}".`);
  return n;
}

switch (command) {
  case "begin": {
    const members = positiveInt(args[0], "members", 6);
    const rounds = positiveInt(args[1], "rounds", 2);
    clearState(cwd);
    writeState(cwd, {
      runId: randomUUID(),
      startedAt: new Date().toISOString(),
      sessionId: null,
      armed: false,
      currentRound: 1,
      ceilings: { members, rounds },
      plan: [],
      approved: [],
      denied: [],
    });
    process.stdout.write(
      [
        `Council run opened. Ceilings: ${members} members, ${rounds} rounds.`,
        `Write the plan to: ${planPath(cwd)}`,
        "Then run `arm`. Member spawns are refused until then.",
      ].join("\n") + "\n",
    );
    break;
  }

  case "arm": {
    const state = requireRun();
    const p = planPath(cwd);
    if (!existsSync(p)) fail(`No plan at ${p}. Write it there first.`);

    let plan;
    try {
      plan = JSON.parse(readFileSync(p, "utf8"));
    } catch (err) {
      fail(`The plan is not valid JSON: ${err.message}`);
    }
    if (!Array.isArray(plan) || plan.length === 0) {
      fail("The plan must be a non-empty JSON array of members.");
    }
    if (plan.length > state.ceilings.members) {
      fail(
        `The plan has ${plan.length} members; the ceiling is ${state.ceilings.members}. ` +
          "Cut the roster — the gate will refuse the excess anyway.",
      );
    }

    const seen = new Set();
    plan.forEach((member, i) => {
      const where = `plan[${i}]`;
      if (!member || typeof member !== "object") fail(`${where} is not an object.`);
      const role = normalizeRole(member.role);
      if (!role) fail(`${where}.role is missing.`);
      if (typeof member.question !== "string" || member.question.trim().length < 10) {
        fail(`${where}.question is missing or too short to be a real research question.`);
      }
      const round = positiveInt(member.round, `${where}.round`, 1);
      if (round > state.ceilings.rounds) {
        fail(`${where}.round is ${round}; the ceiling is ${state.ceilings.rounds}.`);
      }
      const key = `${round}:${role}:${member.question.trim().toLowerCase()}`;
      if (seen.has(key)) fail(`${where} duplicates an earlier member exactly.`);
      seen.add(key);
      member.role = role;
      member.round = round;
    });

    // Nothing inside a lock may call fail(): process.exit skips finally blocks
    // and would leave the lockfile behind.
    withLock(cwd, () => {
      const fresh = readState(cwd) ?? state;
      fresh.plan = plan;
      fresh.armed = true;
      writeState(cwd, fresh);
    });

    const roles = [...new Set(plan.map((m) => m.role))];
    process.stdout.write(
      `Plan armed: ${plan.length} member(s) across ${roles.length} role(s) — ${roles.join(", ")}.\n`,
    );
    break;
  }

  case "round": {
    const state = requireRun();
    const n = positiveInt(args[0], "round", undefined);
    if (n === undefined) fail("Usage: round <n>");
    if (n > state.ceilings.rounds) {
      fail(`Round ${n} exceeds the ceiling of ${state.ceilings.rounds}.`);
    }
    withLock(cwd, () => {
      const fresh = readState(cwd) ?? state;
      fresh.currentRound = n;
      writeState(cwd, fresh);
    });
    process.stdout.write(`Now in round ${n}.\n`);
    break;
  }

  case "tree": {
    const state = requireRun();
    const lines = [`Council ${state.runId} — round ${state.currentRound}`];
    for (const a of state.approved) {
      lines.push(
        `  round ${a.round}  ${a.role}  ${a.agentId ?? "(never started)"}  ` +
          `${a.outcome ?? "running"}`,
      );
    }
    if (state.denied.length) {
      lines.push("Refused spawns:");
      for (const d of state.denied) lines.push(`  round ${d.round}  ${d.role}  ${d.reason}`);
    }
    process.stdout.write(`${lines.join("\n")}\n`);
    break;
  }

  case "end": {
    clearState(cwd);
    process.stdout.write("Council run closed.\n");
    break;
  }

  default:
    process.stdout.write(
      [
        "Usage: council-state.mjs <begin|arm|round|tree|end>",
        `State directory: ${stateDir(cwd)}`,
      ].join("\n") + "\n",
    );
    process.exit(command ? 1 : 0);
}
