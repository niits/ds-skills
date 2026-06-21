#!/usr/bin/env python3
"""
Visualization Skill Review Council
──────────────────────────────────
A debate council of agents reads skills/visualization/ and critiques the
documentation for honest library tradeoffs, genuine SWD alignment, and consistent
accessibility guidance. All agents argue in English.

Run:
    python skills/visualization/agent_council/review_council.py
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
    "Library Selection Critic": (RED,    "✗"),
    "SWD Alignment Checker":    (YELLOW, "⚙"),
    "Accessibility Auditor":    (PURPLE, "◈"),
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
    "Library Selection Critic": {
        "color": RED,
        "focus_files": ["SKILL.md", "references/grammar-of-graphics.md"],
        "system": """\
You are the Library Selection Critic reviewing a visualization skill that picks
Plotly / matplotlib / plotnine by output goal.

Your role: challenge the tool choices and the honesty of the tradeoffs. Ask:
- Does Plotly actually win for EDA, or is interactivity oversold for the work a DS
  really does? When does static beat interactive?
- When does plotnine justify its abstraction overhead versus just using matplotlib?
  Is "grammar of graphics fits" a real criterion or a vibe?
- Is the decision tree's fallback chain (primary → fallback) defensible, or are
  there goals where the recommended primary is the wrong call?

Quote the exact recommendation you dispute and give the condition where it fails.
Write in English. Under 200 words. Be surgical, not exhaustive.""",
    },

    "SWD Alignment Checker": {
        "color": YELLOW,
        "focus_files": ["SKILL.md", "references/clutter-elimination.md", "references/narrative-structure.md"],
        "system": """\
You are the SWD Alignment Checker.

Your role: verify that each goal section (EDA, Publication, Presentation) genuinely
*applies* the Storytelling-with-Data framework, rather than name-dropping it once and
moving on. Ask:
- Does the EDA section still carry SWD, or does it quietly drop the framework the
  moment interactivity appears?
- Are Big Idea / declutter / focus-attention / narrative-title actually operational in
  the guidance and the `swd_style.py` helpers, or just listed?
- Is there a contradiction between the SWD framework section and what the three goal
  sections actually tell you to do?

Quote the specific text. Distinguish "applied" from "referenced as a footnote."
Write in English. Under 200 words.""",
    },

    "Accessibility Auditor": {
        "color": PURPLE,
        "focus_files": ["SKILL.md", "references/color_palettes.md", "references/grammar-of-graphics.md"],
        "system": """\
You are the Accessibility Auditor.

Your role: check that colorblind-safety, font-size, and contrast guidance is
consistent AND actionable across ALL THREE library sections (Plotly, matplotlib,
plotnine). Ask:
- Are the same palette rules (Okabe-Ito categorical, viridis/cividis continuous, no
  red-green) stated for every library, or only for matplotlib?
- Does the Plotly/EDA guidance silently allow unsafe defaults?
- Is "no color-only encoding" actually enforced, with redundant encoding examples?
- Are font-size / print-legibility rules concrete (numbers) or vague?

Quote the gap. "matplotlib gets the palette rule but plotnine and Plotly do not" is
the kind of finding that matters.
Write in English. Under 200 words.""",
    },

    "Defender": {
        "color": GREEN,
        "focus_files": ["SKILL.md"],
        "system": """\
You are the Defender in this review council.

You have heard the Library Selection Critic, the SWD Alignment Checker, and the
Accessibility Auditor. Rebut their strongest objections with evidence from the docs.

Rules:
- Concede genuinely valid points — do not defend everything
- For each rebuttal, quote the specific text that addresses the criticism
- Distinguish "genuinely missing" from "covered but the reviewer missed it"
- Note when a criticism belongs to a linked reference file rather than SKILL.md

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
    ("Round 1 — Attack", ["Library Selection Critic", "SWD Alignment Checker", "Accessibility Auditor"]),
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

    print(f"\n{BOLD}{BLUE}Visualization Skill Review Council{RESET}")
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
    skill_dir = Path(__file__).parent.parent  # skills/visualization/
    if not skill_dir.exists():
        print(f"Error: {skill_dir} not found", file=sys.stderr)
        sys.exit(1)

    run_debate(skill_dir)
