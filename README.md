# DS Skills for Databricks Agent

A collection of data science skills adapted for use with a Databricks-based agent.
All skills run on Databricks clusters and render output inline in notebooks.

## Skills

Skills are grouped into **general DS skills**, **banking-domain skills**, and an
**ML-pipeline skill**. Most skills ship an `agent_council/review_council.py` — a debate
council of agents that critiques the skill's own content (all in English).
(`feature-onboarding` does not yet include one.)

### General DS skills

#### `databricks/`

Effective Databricks usage for Data Scientists, in two parts. **Part A — Querying:**
read and shape large data with Spark SQL/PySpark and Delta Lake (read-only profiling,
predicate pushdown, join hints, semi-join pre-filtering, wide modeling-dataset join
chains, window aggregations, EDA patterns, pandas interop). **Part B — MLflow Model
Packaging:** turn a trained model into a reproducible, notebook-independent artifact
(`log_model` with `input_example`/signature, `pyfunc` for custom models, Model Registry
stage/alias promotion, `spark_udf` batch inference, a reproducibility checklist).

#### `plotnine-visualization/`

Grammar-of-graphics visualizations in Python using [plotnine](https://plotnine.org) — a faithful ggplot2 port for Python.
Use for EDA, business dashboards, and any chart built by layering geoms + aesthetics + scales + themes.
Covers the full grammar: geoms (40+), stats, scales, facets, coordinate systems, position adjustments, and themes.
Includes ready-to-use patterns (scatter, histogram, violin, heatmap, time series, faceted small multiples)
and theme recipes (NYT, FT, dark/presentation, publication/academic).
Works with both **pandas** and **polars** DataFrames.
Display in Databricks notebooks via `display(p.draw())`.

#### `visualization/`

Make charts that communicate. Applies the Storytelling-with-Data (SWD) framework to
**every** chart, then picks the library by output goal via a decision tree:
Plotly for interactive EDA, matplotlib/seaborn for publication, matplotlib + NYT theme
for presentations, and plotnine when the grammar of graphics fits. Carries the SWD
principles, scientific/publication styling references, a plotnine grammar-of-graphics
reference, and the `swd_style.py` / `style_presets.py` helpers plus `.mplstyle` presets.

#### `metrics-evaluation/`

Metric selection, interpretation, baselines, and diagnosis of metric movements, with
business KPI mapping and domain guides (churn, lead scoring, recommendation).

### Banking-domain skills

#### `banking-hypothesis-generation/`

Structured hypothesis formulation for banking DS: credit risk, fraud, customer
analytics, AML, and regulatory model validation. Follows the scientific method adapted
for banking constraints (internal data, regulatory oversight, champion-challenger
testing) — observations → competing hypotheses → experimental design → testable
predictions.

#### `banking-visualization/`

Domain layer for banking charts. Audience tiers (executive / risk committee / regulator
/ practitioner), trustworthiness obligations in regulated environments (axis-at-zero,
data-as-of dates, no color-only encoding, dual-axis caveats), and a task map of standard
charts (KS curve, PSI bar, migration matrix, vintage curve, fraud anomaly enclosure,
cohort retention). Defers the SWD framework and library choice to `visualization/`.

### ML-pipeline skills

#### `feature-onboarding/`

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
| `banking-hypothesis-generation` | [K-Dense-AI/claude-scientific-skills — hypothesis-generation](https://github.com/K-Dense-AI/claude-scientific-skills/tree/main/scientific-skills/hypothesis-generation) | MIT |
| `visualization` (publication core) | [K-Dense-AI/claude-scientific-skills — scientific-visualization](https://github.com/K-Dense-AI/claude-scientific-skills/tree/main/scientific-skills/scientific-visualization) | MIT |
| `visualization` (ML chart patterns) | [Orchestra-Research/AI-Research-SKILLs — academic-plotting](https://github.com/Orchestra-Research/AI-Research-SKILLs/tree/main/20-ml-paper-writing/academic-plotting) | MIT |
| `visualization` / `banking-visualization` (SWD framework + domain charts) | Adapted from *Storytelling with Data* by Cole Nussbaumer Knaflic (Wiley, 2015) | — |
| `plotnine-visualization` | Based on [plotnine](https://plotnine.org) docs and [rstudio/cheatsheets](https://github.com/rstudio/cheatsheets) | MIT / CC BY SA |

### Adaptations

Skills have been modified for Databricks:
- LaTeX output removed; replaced with Markdown/HTML rendered in notebook cells
- File export removed; figures displayed inline via `display(fig)`
- For skills that ship Python assets (`visualization`, `shared`), script imports
  reference DBFS paths (`/dbfs/FileStore/...`); the analysis-only skills
  (`feature-onboarding`, `metrics-evaluation`, `banking-hypothesis-generation`) are
  pure-PySpark/pandas snippets with no DBFS path dependencies
