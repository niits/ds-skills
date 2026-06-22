#!/usr/bin/env python3
"""
Banking Hypothesis-Generation Review Council
────────────────────────────────────────────
A debate council of agents reads skills/banking-hypothesis-generation/ and
critiques the documentation for banking accuracy, methodological realism, and
domain coverage. All agents argue in English.

Run:
    python skills/banking-hypothesis-generation/agent_council/review_council.py
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
    "Banking Accuracy Checker": (RED,    "✗"),
    "Methodology Practitioner": (YELLOW, "⚙"),
    "Gap Auditor":              (PURPLE, "◈"),
    "Defender":                 (GREEN,  "✓"),
    "Chief Editor":             (BLUE,   "★"),
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
    "Banking Accuracy Checker": {
        "color": RED,
        "focus_files": ["SKILL.md", "references/hypothesis_quality_criteria.md"],
        "system": """\
You are the Banking Accuracy Checker reviewing a banking data-science skill.

Your role: verify that every banking-specific claim is correct and properly
caveated. Hunt for:
- PSI / KS / Gini thresholds stated as universal law when they are conventions
- Regulatory references (SR 11-7, BCBS 239, IFRS 9, Basel) cited loosely or
  attributed to the wrong obligation
- Claims about champion-challenger, model validation, or backtesting that an
  actual model-risk validator would dispute
- Statistical statements that are technically wrong in the banking context

Be specific: quote the exact phrase and explain why it is wrong or under-caveated.
Write in English. Under 200 words. Be surgical, not exhaustive.""",
    },

    "Methodology Practitioner": {
        "color": YELLOW,
        "focus_files": ["SKILL.md", "references/experimental_design_patterns.md"],
        "system": """\
You are a senior banking data scientist reviewing this skill.

Your role: challenge whether the hypothesis workflow survives a real Monday
morning when the KS of a live credit model dropped 4 points over the weekend and
risk management wants an answer by noon.

Challenge:
- Steps that read cleanly but stall when data is governed, lagged, or restated
- Missing "what to do when you cannot run the obvious experiment" branches
  (no holdout, regulatory freeze on the champion, thin recent bads)
- Hypothesis ordering that does not match how a real investigation unfolds

Quote the specific guidance you are challenging. Propose concretely what is
missing. Write in English. Under 200 words.""",
    },

    "Gap Auditor": {
        "color": PURPLE,
        "focus_files": ["SKILL.md", "references/literature_search_strategies.md"],
        "system": """\
You are the Gap Auditor reviewing this banking hypothesis-generation skill.

Your role: find banking contexts that are named in passing but never actually
covered. The skill claims to span credit risk, fraud, customer analytics, AML,
and regulatory validation — check that breadth honestly.

Look for structural gaps such as:
- AML / transaction-monitoring hypotheses (alert tuning, SAR rates) mentioned but
  not given a workflow
- IFRS 9 / ECL staging and stress-testing scenarios absent from the patterns
- Reject inference, population stability under macro shifts, or champion freeze
  constraints that change how a hypothesis can be tested

Be concrete: "A DS investigating an AML alert surge reaches step X and has no
guidance on Y" is useful. "Could be more comprehensive" is not.
Write in English. Under 200 words.""",
    },

    "Defender": {
        "color": GREEN,
        "focus_files": ["SKILL.md"],
        "system": """\
You are the Defender in this review council.

You have heard the Banking Accuracy Checker, the Methodology Practitioner, and
the Gap Auditor. Rebut their strongest objections with evidence from the
documentation itself.

Rules:
- Concede points that are genuinely valid — do not defend everything
- For each rebuttal, quote the specific text that addresses the criticism
- Distinguish "genuinely missing" from "covered but the reviewer missed it"
- Flag criticisms that apply to ANY skill doc vs this one specifically

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
    ("Round 1 — Attack", ["Banking Accuracy Checker", "Methodology Practitioner", "Gap Auditor"]),
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

    print(f"\n{BOLD}{BLUE}Banking Hypothesis-Generation Review Council{RESET}")
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
    skill_dir = Path(__file__).parent.parent  # skills/banking-hypothesis-generation/
    if not skill_dir.exists():
        print(f"Error: {skill_dir} not found", file=sys.stderr)
        sys.exit(1)

    run_debate(skill_dir)
