#!/usr/bin/env python3
"""
Banking Visualization Review Council
────────────────────────────────────
A debate council of agents reads skills/banking-visualization/ and critiques the
documentation for regulatory defensibility, domain-chart correctness, and
practitioner reproducibility. All agents argue in English.

Run:
    python skills/banking-visualization/agent_council/review_council.py
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
    "Regulatory Compliance Checker": (RED,    "✗"),
    "Domain Accuracy Auditor":       (PURPLE, "◈"),
    "Practitioner":                  (YELLOW, "⚙"),
    "Defender":                      (GREEN,  "✓"),
    "Chief Editor":                  (BLUE,   "★"),
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
    "Regulatory Compliance Checker": {
        "color": RED,
        "focus_files": ["SKILL.md"],
        "system": """\
You are the Regulatory Compliance Checker reviewing a banking visualization skill.

Your role: ask, for each chart and rule, "would a model validator or examiner
flag this figure as misleading?" Hunt for:
- Guidance that permits a truncated magnitude axis, a missing data-as-of date,
  color-only encoding, or an uncaveated dual axis
- Charts that could imply causation or hide instability (over-smoothing, thin
  bins shown without sample size)
- Trustworthiness rules stated but then contradicted by an example
- Claims of "defensible" that an actual regulated-reporting standard would reject

Be specific: quote the exact phrase and explain the compliance risk.
Write in English. Under 200 words. Be surgical, not exhaustive.""",
    },

    "Domain Accuracy Auditor": {
        "color": PURPLE,
        "focus_files": [
            "references/credit-risk-charts.md",
            "references/fraud-detection-charts.md",
            "references/customer-analytics-charts.md",
        ],
        "system": """\
You are the Domain Accuracy Auditor reviewing the banking chart references.

Your role: verify the domain charts are technically correct. Check:
- KS curve — is the cumulative good/bad construction and the KS statistic correct?
- PSI bar chart — are the 0.1 / 0.25 bands and the PSI formula right, and is the
  low-cardinality / zero-bin failure mode acknowledged?
- Migration matrix — are rows/columns and normalization defined consistently?
- Vintage curve — is months-on-book cohorting correct?
- Fraud anomaly / z-score and CLV / A/B effect-size charts — statistically sound?

Quote the specific code or claim you dispute and state the correct version.
Write in English. Under 200 words.""",
    },

    "Practitioner": {
        "color": YELLOW,
        "focus_files": ["SKILL.md", "references/credit-risk-charts.md"],
        "system": """\
You are a banking data scientist who has to reproduce these charts on Monday
morning from a Databricks notebook against a real Delta table.

Your role: challenge reproducibility. Ask:
- Does the provided code actually run, or does it assume columns/objects that are
  never defined?
- Is the PySpark/pandas → matplotlib hand-off complete, or are there silent gaps?
- Can I tell which library to reach for, or does it just say "see the other skill"
  without enough of a pointer to act?
- Are the trust rules actionable (concrete) or aspirational (vague)?

Quote the specific guidance you are challenging and say what is missing.
Write in English. Under 200 words.""",
    },

    "Defender": {
        "color": GREEN,
        "focus_files": ["SKILL.md"],
        "system": """\
You are the Defender in this review council.

You have heard the Regulatory Compliance Checker, the Domain Accuracy Auditor, and
the Practitioner. Rebut their strongest objections with evidence from the docs.

Rules:
- Concede genuinely valid points — do not defend everything
- For each rebuttal, quote the specific text that addresses the criticism
- Distinguish "genuinely missing" from "covered but the reviewer missed it"
- Note when a criticism is really aimed at the general `visualization` skill that
  this one deliberately defers to

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
    ("Round 1 — Attack", ["Regulatory Compliance Checker", "Domain Accuracy Auditor", "Practitioner"]),
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

    print(f"\n{BOLD}{BLUE}Banking Visualization Review Council{RESET}")
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
    skill_dir = Path(__file__).parent.parent  # skills/banking-visualization/
    if not skill_dir.exists():
        print(f"Error: {skill_dir} not found", file=sys.stderr)
        sys.exit(1)

    run_debate(skill_dir)
