---
name: visualization
description: Use this skill when creating or critiquing statistically honest charts, making a quick EDA plot, designing a slide or infographic, choosing an encoding, teaching Grammar of Graphics or plotnine, or visualizing model-evaluation or causal-inference results.
license: MIT; third-party notices apply
compatibility: Designed for Kiro CLI, Claude Code, and OpenCode; Python examples require the libraries they import.
metadata:
    skill-author: ds-skills
    domain: general
---

# Visualization

Use progressive disclosure: classify the task, read the mapped reference, and load additional
files only when the task needs them. Do not preload the entire `references/` directory.

## Primary Routing

| User intent | Required reference |
|---|---|
| Quick EDA, notebook check, inspect/debug a distribution or relationship | `references/workflows/quick-eda.md` |
| Shared slide, infographic, report, or explanatory chart | `references/workflows/slide-infographic.md` |
| Learn GoG, use plotnine, or decompose/reconstruct a chart | `references/foundations/grammar-of-graphics.md` |
| Critique or validate an existing chart | `references/delivery/audit-and-delivery.md` plus the closest topic reference below |

Quick EDA uses matplotlib only. A request for plotnine code follows the GoG route or the shared
artifact route, not Quick EDA.

## Topic Routing

| Need | Load |
|---|---|
| Choose a chart or encoding | `references/foundations/chart-selection.md` |
| Audit data, uncertainty, accessibility, captions, or delivery | `references/delivery/audit-and-delivery.md` |
| Color palette or color-vision validation | `references/delivery/color-palettes.md` |
| Attention, layout, direct labels, or decluttering | `references/delivery/attention-and-layout.md` |
| Multi-slide narrative or audience adaptation | `references/delivery/narrative-structure.md` |
| Non-obvious matplotlib implementation | `references/implementations/matplotlib-patterns.md` |
| Model-performance chart | `references/domains/model-evaluation.md` |
| Causal estimate or identifying-assumption diagnostic | `references/domains/causal-inference.md` |
| Reusable matplotlib helpers | `assets/swd_style.py`, `assets/color_palettes.py` |

## Common Behavior

- Apply specialist references as overlays on the selected primary workflow.
- Interpret results only after inspecting rendered output; otherwise mark interpretation pending.
- Ask one short clarification only when the artifact or audience would change the workflow.
- Routing here takes precedence; detailed rules live in the mapped reference.
