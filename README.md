# DS Skills for Databricks Agent

A collection of data science skills adapted for use with a Databricks-based agent.
All skills run on Databricks clusters and render output inline in notebooks.

## Skills

### `hypothesis-generation/`

Structured hypothesis formulation from observations. Follows the scientific method:
literature search → evidence synthesis → competing hypotheses → experimental design → testable predictions.
Output is rendered as Databricks-native HTML blocks via `displayHTML()`.

### `scientific-visualization/`

Publication-quality figures for scientific manuscripts and ML conference papers,
rendered inline in Databricks notebooks via `display(fig)`.
Covers matplotlib/seaborn chart patterns for line plots, grouped bars, heatmaps,
leaderboard charts, and multi-panel figures with colorblind-safe palettes and
venue-specific sizing (NeurIPS, ICML, Nature, Science, Cell).

---

## Sources

Skills are adapted from the following open-source repositories:

| Skill | Source | License |
|-------|--------|---------|
| `hypothesis-generation` | [K-Dense-AI/claude-scientific-skills — hypothesis-generation](https://github.com/K-Dense-AI/claude-scientific-skills/tree/main/scientific-skills/hypothesis-generation) | MIT |
| `scientific-visualization` (core) | [K-Dense-AI/claude-scientific-skills — scientific-visualization](https://github.com/K-Dense-AI/claude-scientific-skills/tree/main/scientific-skills/scientific-visualization) | MIT |
| `scientific-visualization` (ML chart patterns) | [Orchestra-Research/AI-Research-SKILLs — academic-plotting](https://github.com/Orchestra-Research/AI-Research-SKILLs/tree/main/20-ml-paper-writing/academic-plotting) | MIT |

### Adaptations

All skills have been modified for Databricks:
- LaTeX output removed; replaced with Markdown/HTML rendered in notebook cells
- File export removed; figures displayed inline via `display(fig)`
- Script imports reference DBFS paths (`/dbfs/FileStore/...`)
