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

### `storytelling-with-data/`

Framework for communicating data findings to an audience. Covers general visualization principles
and domain-specific chart patterns for financial services DS work.

**General framework:** Six-step process — context-setting (Big Idea, audience tiers) → chart selection →
clutter elimination → pre-attentive attention → Gestalt-based design → narrative arc.

**Domain chart libraries** (under `references/domain/`):
- Credit and risk analytics: KS curve, vintage, migration matrix, risk heatmap, bullet chart, PSI
- Model evaluation: ROC, calibration, SHAP waterfall, feature importance, lift/gain
- Fraud detection: anomaly time series, calendar heatmap, rolling z-score, scatter outlier
- Customer analytics: cohort retention heatmap, funnel, segment profile, churn distribution, A/B test CI
- Causal inference: coefficient plot, parallel trends, event study, RDD binned scatter, propensity overlap

Includes `swd_style.py` helpers: `declutter()`, `apply_swd_palette()`, `annotate_insight()`,
`risk_colormap()`, `psi_status()`, `waterfall_colors()`.
Output rendered inline in Databricks notebooks via `display(fig)` and `displayHTML()`.

### `feature-onboarding/`

End-to-end lifecycle for onboarding a new feature group into a supervised ML pipeline,
from data-source understanding to production code. Primary focus on **lead scoring** and
**credit scoring** (binary, ranking-oriented), extensible to recommendation systems.

Twelve phases with a hard Go/No-Go gate. Opinionated on a **Model Mode** choice
(scorecard/WoE vs GBM) that keeps binning, null handling, monotonicity, and fairness
consistent. Emphasizes **hypothesis-before-compute** (no brute-forced features) and
guards the failures that kill models in production:
- **Leakage** — temporal point-in-time (future/restated/late-arriving data, embargo) *and* definitional tautology (label-proxy correlation test)
- **Predictive power** — IV/WoE with the practical traps handled (zero-event smoothing, min-event-per-bin, sparse/tie features, rare-event instability); binary-only scope with regression/multiclass alternatives
- **Redundancy + lift** — Spearman & VIF/multivariate redundancy, then incremental-lift (wrapper/embedded) as the actual decision, not univariate IV alone
- **Stability** — PSI and out-of-time (OOT) validation
- **Null handling** — absence vs unknown, missingness flags, mode-dependent imputation

Reference files (`references/`) carry the technical depth with PySpark/pandas snippets;
domain files (`domains/`) cover credit scoring (scorecard, reason codes, fairness/proxy,
reject inference), lead scoring (feature latency, selection bias), and the recsys
extension path.

---

## Sources

Skills are adapted from the following open-source repositories:

| Skill | Source | License |
|-------|--------|---------|
| `hypothesis-generation` | [K-Dense-AI/claude-scientific-skills — hypothesis-generation](https://github.com/K-Dense-AI/claude-scientific-skills/tree/main/scientific-skills/hypothesis-generation) | MIT |
| `scientific-visualization` (core) | [K-Dense-AI/claude-scientific-skills — scientific-visualization](https://github.com/K-Dense-AI/claude-scientific-skills/tree/main/scientific-skills/scientific-visualization) | MIT |
| `scientific-visualization` (ML chart patterns) | [Orchestra-Research/AI-Research-SKILLs — academic-plotting](https://github.com/Orchestra-Research/AI-Research-SKILLs/tree/main/20-ml-paper-writing/academic-plotting) | MIT |
| `storytelling-with-data` | Adapted from *Storytelling with Data* by Cole Nussbaumer Knaflic (Wiley, 2015) | — |

### Adaptations

All skills have been modified for Databricks:
- LaTeX output removed; replaced with Markdown/HTML rendered in notebook cells
- File export removed; figures displayed inline via `display(fig)`
- Script imports reference DBFS paths (`/dbfs/FileStore/...`)
