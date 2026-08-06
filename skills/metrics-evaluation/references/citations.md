# Citation Index (Reference Only)

> Optional provenance index for selected claims in `topics/core/metric_interpretation.md`,
> `topics/core/baselines.md`, and `topics/core/evaluator_semantics.md`. It is listed in
> `SKILL.md` but is not part of normal use.

## AP / AUC-PR
- Davis & Goadrich (2006), "The Relationship Between Precision-Recall and ROC Curves", ICML. Supports the population/no-skill PR reference; exact finite-sample AP also depends on ranking size, ties, and implementation.
- Saito & Rehmsmeier (2015), "The Precision-Recall Plot Is More Informative than the ROC Plot", PLOS ONE. Shows why precision-recall views can be more informative than ROC views for imbalanced data.

## AUC-ROC
- Hosmer & Lemeshow, "Applied Logistic Regression" (2nd ed., 2000), Ch. 5. Source of the 0.7 / 0.8 / 0.9 discrimination labels. Standard, widely-adopted textbook.
- Hanley & McNeil (1982), Radiology. Foundational AUC paper.

## PSI (Population Stability Index)
- Yurdakul (2018), "Statistical Properties of the Population Stability Index", PhD dissertation, Western Michigan University. Original analysis.
- Yurdakul & Naranjo (2020), "Statistical properties of the population stability index", Journal of Risk Model Validation, 14(4). Peer-reviewed version. States the 0.1/0.25 thresholds are used "without reference to statistical type I or type II error rates" and have "no support or references in the academic world." These two are the same work, not independent corroboration.

## MASE / RMSSE (Forecasting)
- Hyndman & Koehler (2006), "Another Look at Measures of Forecast Accuracy", International Journal of Forecasting, 22(4), 679–688. Peer-reviewed, widely cited. Defines MASE; specifies no threshold for "good" below 1.0.
- Makridakis, Spiliotis & Assimakopoulos (2022), "M5 accuracy competition: Results, findings, and conclusions", International Journal of Forecasting. Uses RMSSE rather than MASE. The precise reason is that the MASE denominator can be exactly zero on intermittent series with consecutive equal values, not that MASE fails on all intermittent series.

## Probabilistic Forecasting
- Gneiting & Raftery (2007), "Strictly Proper Scoring Rules, Prediction, and Estimation", Journal of the American Statistical Association, 102(477), 359–378. Defines propriety; establishes CRPS and the quantile (pinball) loss as proper scoring rules.
- Gneiting, Balabdaoui & Raftery (2007), "Probabilistic forecasts, calibration and sharpness", Journal of the Royal Statistical Society Series B, 69(2), 243–268. Source of the "maximize sharpness subject to calibration" framing behind reporting PICP together with interval width.

## Time-Series Anomaly Detection
- Kim et al. (2022), "Towards a Rigorous Evaluation of Time-Series Anomaly Detection", AAAI. Shows point-adjusted F1 is inflated to the point that a randomly generated detector outperforms published state-of-the-art scores; source of the point-adjustment warning in `topics/core/evaluator_semantics.md`.

## NDCG (Ranking)
- Järvelin & Kekäläinen (2002), "Cumulated Gain-Based Evaluation of IR Techniques", ACM TOIS, 20(4), 422–446. Foundational DCG/NDCG definition. Implementations vary in gain, discount, IDCG, and zero-IDCG behavior; use the contract in `topics/core/evaluator_semantics.md` before comparing systems.

## Calibration
- Niculescu-Mizil & Caruana (2005), "Predicting Good Probabilities with Supervised Learning", ICML.

## Position Bias / Unbiased Learning-to-Rank
- Joachims, Swaminathan & Schnabel (2017), "Unbiased Learning-to-Rank with Biased Feedback", WSDM. Inverse propensity scoring for position-debiased training.

## Uplift Modeling
- Radcliffe (2007), "Using control groups to target on predicted lift: Building and assessing uplift model", Direct Marketing Analytics Journal, 14–21. Qini coefficient, uplift segments (persuadables / sure things / lost causes). Industry reference, widely adopted. Cited by `domains/customer_analytics/churn_prediction.md`.

## Multi-Label Classification
- Tsoumakas & Katakis (2007), "Multi-Label Classification: An Overview", International Journal of Data Warehousing and Mining, 3(3), 1–13. Defines the label-powerset and binary-relevance framings and the subset-accuracy / Hamming-loss distinction.
- Wu & Zhou (2017), "A Unified View of Multi-Label Performance Measures", ICML. Shows micro, macro, and instance-averaged measures optimize different objectives and are not interchangeable.

## Confidence Interval Overlap
- Schenker & Gentleman (2001), "On Judging the Significance of Differences by Examining the Overlap Between Confidence Intervals", The American Statistician, 55(3), 182–186. Source of the rule that non-overlap of two marginal intervals is not a valid difference test.

## Model Selection Optimism
- Cawley & Talbot (2010), "On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation", JMLR, 11, 2079–2107. Basis for the nested / outer-loop evaluation requirement in `topics/core/evaluation_protocol.md`.

## Representation Learning
- Kornblith, Shlens & Le (2019), "Do Better ImageNet Models Transfer Better?", CVPR. Controlled transfer and representation comparison.
- Chen et al. (2020), "A Simple Framework for Contrastive Learning of Visual Representations", ICML. Linear evaluation and transfer protocols. Note: both entries share a Google Research lineage and are not fully independent corroboration of the linear-probe protocol.
