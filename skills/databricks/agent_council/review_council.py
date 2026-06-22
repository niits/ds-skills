#!/usr/bin/env python3
"""
Databricks Skill Review Council
───────────────────────────────
A debate council of agents reads skills/databricks/ and critiques the
documentation for Spark/Delta correctness, MLflow reproducibility, and honest
performance claims. All agents argue in English.

Run:
    python skills/databricks/agent_council/review_council.py
"""

import sys
import textwrap
from pathlib import Path

import anthropic

# ─── ANSI colors ──────────────────────────────────────────────────────────────
RED     = "\033[91m"
PURPLE  = "\033[95m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"

AGENT_COLORS = {
    "Spark Correctness Checker": (RED,    "✗"),
    "MLflow Practitioner":       (YELLOW, "⚙"),
    "Performance Auditor":       (PURPLE, "◈"),
    "Defender":                  (GREEN,  "✓"),
    "Chief Editor":              (BLUE,   "★"),
}

# ─── Read skill files ─────────────────────────────────────────────────────────

def load_skill_content(skill_dir: Path) -> dict[str, str]:
    """Load all .md files, keyed by relative path."""
    files = {}
    for md_file in sorted(skill_dir.rglob("*.md")):
        rel = md_file.relative_to(skill_dir)
        files[str(rel)] = md_file.read_text()
    return files


def build_skill_digest(files: dict[str, str]) -> str:
    """Concatenate all skill files into one reviewable document."""
    parts = []
    for path, content in files.items():
        parts.append(f"\n{'═'*60}\n FILE: {path}\n{'═'*60}\n{content}")
    return "\n".join(parts)


# ─── Agent definitions ────────────────────────────────────────────────────────

AGENTS = {
    "Spark Correctness Checker": {
        "color": RED,
        "focus_files": ["SKILL.md", "references/join_strategies.md", "references/window_aggregation_patterns.md"],
        "system": """\
You are the Spark Correctness Checker reviewing a Databricks DS skill.

Your role: verify the Spark/Delta Lake patterns are accurate. Hunt for:
- Deprecated or wrong APIs (e.g., mis-stated join hint syntax, removed methods)
- Incorrect AQE assumptions (what AQE does/does not auto-fix; skew, coalescing)
- Delta features described wrongly (time travel, `replaceWhere`, semi-join semantics)
- Window/aggregation patterns that would give wrong results (frame bounds, missing
  PARTITION BY implications, null handling)

Be specific: quote the exact code or claim and state the correct version.
Write in English. Under 200 words. Be surgical, not exhaustive.""",
    },

    "MLflow Practitioner": {
        "color": YELLOW,
        "focus_files": ["SKILL.md"],
        "system": """\
You are an MLflow practitioner reviewing the Part B — MLflow Model Packaging
guidance.

Your role: challenge whether the packaged model is TRULY notebook-independent and
will reproduce on a cold cluster. Ask:
- Would the logged model actually load in a fresh kernel, or does an example still
  leak a notebook global / relative import?
- Is the preprocessing genuinely inside the artifact in every pattern?
- Are signature/input_example, pinned requirements, and artifacts handled correctly,
  or is something hand-waved?
- Is the Registry stage/alias guidance current (stages vs UC aliases) and the
  `spark_udf` batch pattern correct?

Quote the specific guidance you challenge and say what would break.
Write in English. Under 200 words.""",
    },

    "Performance Auditor": {
        "color": PURPLE,
        "focus_files": ["SKILL.md", "references/join_chain_optimization.md", "references/anti_patterns.md"],
        "system": """\
You are the Performance Auditor reviewing this skill.

Your role: hunt for missing optimizations, misleading performance claims, and
anti-patterns disguised as recommendations. Ask:
- Are the "10x faster" style claims defensible, or stated without conditions?
- Is any recommended pattern actually an anti-pattern at scale (e.g.,
  broadcast of a too-large side, caching that wastes memory, checkpoint misuse)?
- What high-impact optimization is missing (partition sizing, predicate pushdown
  breakers, DPP, shuffle tuning) given the workloads described?

Quote the specific claim or omission. State the condition under which it is wrong.
Write in English. Under 200 words.""",
    },

    "Defender": {
        "color": GREEN,
        "focus_files": ["SKILL.md"],
        "system": """\
You are the Defender in this review council.

You have heard the Spark Correctness Checker, the MLflow Practitioner, and the
Performance Auditor. Rebut their strongest objections with evidence from the docs.

Rules:
- Concede genuinely valid points — do not defend everything
- For each rebuttal, quote the specific text that addresses the criticism
- Distinguish "genuinely wrong/missing" from "covered but the reviewer missed it"
- Note when a criticism depends on a runtime/version the skill explicitly scopes out

Do NOT dismiss criticism without quoting counter-evidence.
Write in English. Under 180 words.""",
    },

    "Chief Editor": {
        "color": BLUE,
        "focus_files": ["*"],
        "system": """\
You are the Chief Editor. You have heard the full debate.

Synthesize into an actionable editorial verdict:

1. KEEP AS-IS (the strongest parts — what makes this skill genuinely valuable)
2. REVISE (specific sections that need work — cite exact location)
3. ADD (concrete missing pieces — say what to write, not just "add more")
4. VERDICT: one of — Production-ready / Needs revision / Major gaps

Be direct. No padding. Write in English. Under 220 words.""",
    },
}

DEBATE_ORDER = [
    ("Round 1 — Attack", ["Spark Correctness Checker", "MLflow Practitioner", "Performance Auditor"]),
    ("Round 2 — Rebuttal", ["Defender"]),
    ("Synthesis", ["Chief Editor"]),
]

# ─── Debate runner ────────────────────────────────────────────────────────────

def print_header(title: str) -> None:
    width = 64
    print(f"\n{BOLD}{'─'*width}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'─'*width}{RESET}")


def print_agent_turn(agent_name: str, content: str) -> None:
    color, icon = AGENT_COLORS.get(agent_name, (BLUE, "•"))
    print(f"\n{color}{BOLD}{icon} {agent_name}{RESET}")
    print(f"{DIM}{'·'*50}{RESET}")
    wrapped = textwrap.fill(content.strip(), width=72, subsequent_indent="  ")
    print(wrapped)


def build_user_prompt(
    agent_name: str,
    skill_digest: str,
    prior_statements: list[dict],
) -> str:
    parts = [f"=== SKILL DOCUMENTATION UNDER REVIEW ===\n{skill_digest}"]

    if prior_statements:
        parts.append("\n=== DEBATE SO FAR ===")
        for stmt in prior_statements:
            parts.append(f"\n[{stmt['agent']}]\n{stmt['content']}")

    parts.append(f"\n=== YOUR TURN: {agent_name} ===\nGive your response now.")
    return "\n".join(parts)


def run_debate(skill_dir: Path) -> None:
    client = anthropic.Anthropic()

    print(f"\n{BOLD}{BLUE}Databricks Skill Review Council{RESET}")
    print(f"{DIM}Reading: {skill_dir}{RESET}")

    files = load_skill_content(skill_dir)
    print(f"{DIM}Loaded {len(files)} files: {', '.join(files.keys())}{RESET}")

    digest = build_skill_digest(files)
    statements: list[dict] = []

    for round_label, agent_names in DEBATE_ORDER:
        print_header(round_label)

        for agent_name in agent_names:
            config = AGENTS[agent_name]
            prior = [{"agent": s["agent"], "content": s["content"]} for s in statements]

            print(f"\n{DIM}[{agent_name} thinking...]{RESET}", end="", flush=True)

            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=600,
                system=config["system"],
                messages=[{
                    "role": "user",
                    "content": build_user_prompt(agent_name, digest, prior),
                }],
            )
            content = response.content[0].text

            print(f"\r{' '*40}\r", end="")  # clear "thinking..." line
            print_agent_turn(agent_name, content)

            statements.append({"agent": agent_name, "content": content})

    print(f"\n{DIM}{'─'*64}{RESET}\n")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    skill_dir = Path(__file__).parent.parent  # skills/databricks/
    if not skill_dir.exists():
        print(f"Error: {skill_dir} not found", file=sys.stderr)
        sys.exit(1)

    run_debate(skill_dir)
