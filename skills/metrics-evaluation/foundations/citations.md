# Citation Index (Reference Only)

> Consolidates every academic/industry source behind `foundations/metric_interpretation.md` and `foundations/baselines.md`. **Not listed in SKILL.md's Resources** — not read during normal skill use. Exists for anyone who wants to verify a threshold's provenance. The `[Academic]` / `[Industry]` / `[Definitional]` tags and caveats in the main files are self-contained without this file.
>
> Citation counts are point-in-time and drift — treat as a rough authority signal, not a precise figure.

## AP / AUC-PR
- Davis & Goadrich (2006), "The Relationship Between Precision-Recall and ROC Curves", ICML. Supports the population/no-skill PR reference; exact finite-sample AP also depends on ranking size, ties, and implementation.
- Saito & Rehmsmeier (2015), "The Precision-Recall Plot Is More Informative than the ROC Plot", PLOS ONE. ~3,594 citations. Confirms the AP baseline; shows PR is more informative than ROC for imbalanced data — not because ROC inflates, but because AP captures positive-class performance ROC's specificity term obscures.

## AUC-ROC
- Hosmer & Lemeshow, "Applied Logistic Regression" (2nd ed., 2000), Ch. 5. Source of the 0.7 / 0.8 / 0.9 discrimination labels. Standard, widely-adopted textbook.
- Hanley & McNeil (1982), Radiology. Foundational AUC paper.
- Richardson et al. (2024), Patterns, Cell Press: "ROC-AUC is only inflated by imbalance in simulations where changing imbalance changes the score distribution" — i.e. AUC-ROC is robust to prevalence changes for a fixed classifier. Quote paraphrased from the abstract, not independently re-verified word-for-word — treat as directionally reliable.

## KS Statistic (Credit)
- Anderson (2007), "The Credit Scoring Toolkit", Oxford University Press. KS concept in credit context.
- Yan et al. (2018), "Directly Maximizing the KS Statistic", Computational Statistics & Data Analysis. KS as a training objective.
- The 20/40/60 thresholds appear consistently in banking practice (SAS Institute publications, credit scoring practitioners) but are not traceable to a specific academic textbook — industry rule of thumb only.

## Gini Coefficient (Credit)
- Gini = 2×AUC−1 is a mathematical identity, not a citation-dependent claim.
- Practitioner cutoffs (0.4 / 0.6 / 0.8) come from industry norms, not from Hosmer & Lemeshow directly. See Siddiqi (2006/2017), "Credit Risk Scorecards", Wiley — industry-standard textbook, Gini/Somers' D as primary scorecard validation metric.

## PSI (Population Stability Index)
- Yurdakul (2018), "Statistical Properties of the Population Stability Index", Journal of Risk Model Validation (peer-reviewed). States the 0.1/0.25 thresholds are used "without reference to statistical type I or type II error rates" and have "no support or references in the academic world."

## MASE / RMSSE (Forecasting)
- Hyndman & Koehler (2006), "Another Look at Measures of Forecast Accuracy", International Journal of Forecasting, 22(4), 679–688. Peer-reviewed, widely cited. Defines MASE; specifies no threshold for "good" below 1.0.
- M5 Competition (Makridakis et al. 2022) uses RMSSE instead of MASE specifically because MASE is undefined for intermittent-demand series.

## NDCG (Ranking)
- Järvelin & Kekäläinen (2002), "Cumulated Gain-Based Evaluation of IR Techniques", ACM TOIS. Foundational NDCG definition.

## Calibration
- Niculescu-Mizil & Caruana (2005), "Predicting Good Probabilities with Supervised Learning", ICML.

## Position Bias / Unbiased Learning-to-Rank
- Joachims, Swaminathan & Schnabel (2017), "Unbiased Learning-to-Rank with Biased Feedback", WSDM. Inverse propensity scoring for position-debiased training.

## Uplift Modeling
- Radcliffe (2007). Qini coefficient, uplift segments (persuadables / sure things / lost causes). Industry reference, widely adopted.
