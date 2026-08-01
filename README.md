# DS Skills

A five-skill Claude Code plugin for data science work: Spark/Delta and MLflow workflows,
model evaluation, visualization, banking investigations, and feature onboarding for lead
and credit scoring.

The repository contains agent instructions, reference documents, and two optional
matplotlib helper modules. It is not a Python package and does not install notebook or
runtime dependencies. Databricks is the primary execution environment for engineering
examples and output conventions, while much of the evaluation and visualization guidance
is platform-independent.

## Install

Use a current Claude Code release with plugin marketplace support.

```text
/plugin marketplace add niits/ds-skills
/plugin install ds-skills@niits-ds-skills
/reload-plugins
```

Plugin skills use the `ds-skills` namespace:

```text
/ds-skills:databricks
/ds-skills:metrics-evaluation
/ds-skills:visualization
/ds-skills:banking-hypothesis-generation
/ds-skills:feature-onboarding
```

Refresh the marketplace and plugin with:

```text
/plugin marketplace update niits-ds-skills
/plugin update ds-skills@niits-ds-skills
```

## Included Skills

| Skill | Scope | Key constraints |
| --- | --- | --- |
| `databricks` | Spark/Delta profiling, efficient joins and windows, distributed EDA, feature engineering, wide modeling datasets, MLflow packaging, Unity Catalog aliases, and batch inference. | No unbounded collection, unpartitioned large windows, hidden notebook state, or confusion between a Delta snapshot and a per-row as-of join. Targets Databricks Runtime 13+, Spark 3.4+, and MLflow 2.x. |
| `metrics-evaluation` | Baseline-anchored and uncertainty-aware verdicts for classification, regression, and ranking, with domain guides and business-impact translation. | Returns `INSUFFICIENT EVIDENCE` instead of a shipping verdict when decision-critical evaluation context is missing. |
| `visualization` | Accessible and statistically honest EDA, publication, stakeholder, model-evaluation, and causal-inference charts using Plotly, plotnine, matplotlib, or seaborn. | Blocks unexplained denominators or aggregation, unsupported causal language, hidden uncertainty, and meaning that depends only on color or hover. |
| `banking-hypothesis-generation` | Competing mechanisms, falsifiable predictions, and investigation designs for credit risk, fraud, customer analytics, AML, and model validation. | Starts from a measured observation, requires predeclared falsification conditions, and checks data quality and population shift before model redesign. |
| `feature-onboarding` | Hypothesis-first onboarding of feature groups into binary lead- and credit-scoring pipelines, from source audit to production monitoring. | Requires scorecard/GBM mode selection, bitemporal point-in-time safety, incremental lift, and one untouched OOT confirmation. Recommendation-system material is an unsupported roadmap. |

Each skill lives at `skills/<skill-name>/SKILL.md`. Technical depth is split into focused
supporting documents under directories such as `references/`, `domains/`, `business/`,
`foundations/`, `diagnosis/`, and `reporting/`. The visualization skill also ships
`assets/swd_style.py` and `assets/color_palettes.py` for optional matplotlib use.

Files under `agent_council/` are internal editorial review utilities or historical review
records. They are not required to invoke or use a skill.

## Suggested Workflow

The skills can be used independently, or as one model-development lifecycle:

1. Use `banking-hypothesis-generation` to explain a measured portfolio, policy, data, or
   model phenomenon and design distinguishing tests.
2. Use `feature-onboarding` when a hypothesis proposes a candidate feature group that
   must be screened and integrated safely.
3. Apply `databricks` for distributed source processing, feature computation, model
   packaging, and reproducible batch inference.
4. Use `metrics-evaluation` for valid baselines, uncertainty, operating economics, and a
   shipping verdict.
5. Use `visualization` to communicate the evidence, assumptions, uncertainty, and
   decision to the intended audience.

Across the repository, stricter domain rules take precedence over generic examples. In
particular, feature production must follow `feature-onboarding` point-in-time and exact
period semantics even when a simplified Spark example would be technically executable.

## Runtime Assumptions

- The plugin itself has no install-time Python dependencies.
- Examples may require PySpark, MLflow, pandas, NumPy, scikit-learn, matplotlib, seaborn,
  Plotly, plotnine, statsmodels, or other libraries called out in the relevant reference.
- Databricks examples assume suitable cluster, table, Unity Catalog, Feature Engineering,
  or registry permissions for the operation being demonstrated.
- The optional `agent_council/review_council.py` scripts require the `anthropic` package,
  API credentials, and network access. They are maintainer tools, not skill prerequisites.
- The repository does not pin these dependencies or run examples against a live
  Databricks workspace in CI.

## Development

Load the repository directly:

```bash
claude --plugin-dir .
```

Validate both distribution manifests:

```bash
claude plugin validate .claude-plugin/plugin.json
claude plugin validate .claude-plugin/marketplace.json --strict
```

The plugin intentionally omits a fixed `version`, allowing the Git commit SHA to identify
updates. The plugin validator consequently emits a non-fatal version warning. The
marketplace must pass strict validation.

## Publishing

GitHub is the distribution host; publishing means making the marketplace manifest and
plugin content available on `master`, not uploading an npm, PyPI, or release artifact.

`.github/workflows/publish.yml` performs the following checks:

- On pull requests targeting `master`: validate the plugin manifest and strictly validate
  the marketplace manifest.
- On pushes to `master`: run the same validation, then register the public marketplace and
  install `ds-skills@niits-ds-skills` as a distribution smoke test.
- On manual dispatch: run manifest validation only.

The workflow verifies discovery and installation. It does not invoke every skill, execute
the Python examples, or test against Databricks.

## Provenance

This repository contains independently written synthesis, adaptations of open-source
material, and instructions informed by public references. The table distinguishes those
relationships; citing a source does not imply endorsement by its author.

| Repository content | Relationship to source | Upstream terms |
| --- | --- | --- |
| `banking-hypothesis-generation` | Modified and expanded from K-Dense AI's `hypothesis-generation` skill | MIT |
| Parts of `visualization` | Modified and expanded from K-Dense AI's `scientific-visualization` skill | MIT |
| ML chart patterns in `visualization` | Modified and expanded from Orchestra Research's `academic-plotting` skill | MIT |
| Parts of plotnine guidance | Independently organized using the plotnine API and documentation as technical references | plotnine: MIT |
| Plotnine quick-reference concepts | Informed by Posit cheatsheets; adapted portions are identified as modified | CC-BY-4.0 |
| Storytelling and chart-design guidance | Original implementation informed by concepts discussed in *Storytelling with Data* by Cole Nussbaumer Knaflic (Wiley, 2015) | All rights reserved; no license to reproduce the book is claimed |

Upstream links, applicable copyright and permission notices, and modification notes are
in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Ordinary academic and industry
citations that support technical claims remain in the relevant skill references, such as
`skills/metrics-evaluation/foundations/citations.md`.

## Copyright Guidance

Rewriting a skill after learning from a source is not automatically infringement. In
general, copyright protects the source's particular text, code, tables, diagrams, and
other creative expression; it does not protect facts, ideas, methods, or APIs by
themselves. The practical obligations depend on what was reused:

- For MIT sources, modification and redistribution are permitted, but the upstream
  copyright and permission notice must remain with copies or substantial portions.
- For CC-BY-4.0 material, credit the creator, link the source and license, and identify
  changes. CC-BY-4.0 does not contain a ShareAlike requirement.
- For an all-rights-reserved book, use the underlying ideas and write your own structure,
  wording, examples, tables, and figures. Do not closely translate or paraphrase
  protectable passages, and do not reproduce book figures without permission or a clear
  legal exception.
- Attribution does not cure copying that the source license does not permit. Conversely,
  independently written material does not become a derivative work merely because it
  cites the same facts or methods.

These notes document this project's licensing approach and are not legal advice. For
commercial distribution or uncertain close paraphrases, obtain a qualified legal review.

## License

Original contributions in this repository are licensed under the MIT License; see
[LICENSE](LICENSE). Third-party portions remain subject to their applicable upstream
terms listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
