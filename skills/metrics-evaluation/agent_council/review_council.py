#!/usr/bin/env python3
"""
Metrics Skill Review Council
────────────────────────────
Agents đọc nội dung skills/metrics-evaluation/ và phản biện nhau về
chất lượng, độ chính xác, và tính thực tế của tài liệu.

Run:
    python skills/metrics-evaluation/agent_council/review_council.py
"""

import os
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
    "Citation Checker":    (RED,    "✗"),
    "Practitioner":        (YELLOW, "⚙"),
    "Gap Auditor":         (PURPLE, "◈"),
    "Defender":            (GREEN,  "✓"),
    "Chief Editor":        (BLUE,   "★"),
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
    "Citation Checker": {
        "color": RED,
        "focus_files": ["foundations/metric_interpretation.md", "SKILL.md"],
        "system": """\
You are the Citation Checker reviewing a data science skill documentation set.

Your role: verify that every threshold, rule, and claim has proper justification.
Hunt for:
- Thresholds stated as fact without academic or industry source
- Citations that exist but whose actual content doesn't support the claim
- Industry conventions mislabeled as academic findings
- Missing caveats where the authors overclaim certainty

Be specific: quote the exact phrase that's problematic and explain why.
Format: short paragraphs, each starting with the file name and line context.
Under 200 words. Be surgical, not exhaustive.""",
    },

    "Practitioner": {
        "color": YELLOW,
        "focus_files": ["SKILL.md", "diagnosis/checklist.md", "diagnosis/patterns.md"],
        "system": """\
You are a senior ML practitioner reviewing a skill documentation set.

Your role: challenge whether this guidance actually works on a Monday morning
with a real Databricks notebook, a 3pm deadline, and messy data.

Challenge:
- Steps that sound clean on paper but are ambiguous in practice
- Missing "what to do when" branches (the checklist may cover clean cases, not real ones)
- Workflow ordering that doesn't match how real problems unfold
- Guidance that's correct but unusable without additional context not provided

Quote the specific guidance you're challenging. Propose concretely what's missing.
Under 200 words.""",
    },

    "Gap Auditor": {
        "color": PURPLE,
        "focus_files": ["domains/", "diagnosis/patterns.md", "business/kpi_mapping.md"],
        "system": """\
You are the Gap Auditor reviewing a data science skill documentation set.

Your role: find what's missing. Not nitpicks — structural gaps that would cause
a data scientist to fail silently on a real problem.

Look for:
- Domains mentioned in passing but not covered in depth
- Patterns that exist in practice but aren't in the pattern library
- Business contexts where the KPI mapping would give wrong guidance
- The case where all individual steps are correct but the synthesis is incomplete

Be concrete: "A data scientist evaluating a fraud model would reach step X and
have no guidance on Y" is useful. "Could be more comprehensive" is not.
Under 200 words.""",
    },

    "Defender": {
        "color": GREEN,
        "focus_files": ["SKILL.md", "foundations/metric_interpretation.md"],
        "system": """\
You are the Defender in a skill documentation review council.

You have heard the Citation Checker, Practitioner, and Gap Auditor.
Your role: rebut their strongest objections with evidence from the documentation itself.

Rules:
- Concede points that are actually valid — don't defend everything
- For each rebuttal, quote the specific text that addresses the criticism
- Distinguish between "this is genuinely missing" and "this is covered but the
  reviewer missed it"
- Point out if a criticism applies to ALL skill docs (a general problem) vs
  this specific one

Do NOT dismiss criticism without quoting the counter-evidence.
Under 180 words.""",
    },

    "Chief Editor": {
        "color": BLUE,
        "focus_files": ["*"],
        "system": """\
You are the Chief Editor. You've heard the full debate.

Synthesize into an actionable editorial verdict:

1. KEEP AS-IS (strongest parts — what makes this skill genuinely valuable)
2. REVISE (specific sections that need work — cite exact location)
3. ADD (concrete missing pieces — be specific about what to write, not just "add more")
4. VERDICT: one of — Production-ready / Needs revision / Major gaps

Be direct. No padding. Under 220 words.""",
    },
}

DEBATE_ORDER = [
    ("Round 1 — Attack", ["Citation Checker", "Practitioner", "Gap Auditor"]),
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

    print(f"\n{BOLD}{BLUE}Metrics Skill Review Council{RESET}")
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
    skill_dir = Path(__file__).parent.parent  # skills/metrics-evaluation/
    if not skill_dir.exists():
        print(f"Error: {skill_dir} not found", file=sys.stderr)
        sys.exit(1)

    run_debate(skill_dir)
