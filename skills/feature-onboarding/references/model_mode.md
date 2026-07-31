# Model Mode

Choose one mode before source analysis and use it consistently.

| Decision | Scorecard mode (WoE + logistic) | GBM mode (tree ensemble) |
|---|---|---|
| Typical use | Credit scoring and governed lending | Lead scoring and internal ranking |
| Representation | Train-fitted supervised bins and WoE | Raw or transformed values; binning optional |
| Missing values | Every value needs a defined bin/representation | Native routing only if estimator and serving support it; otherwise train-fitted imputation plus flag |
| Monotonicity | Apply declared policy/domain requirement | Optional monotone constraints |
| Redundancy | Low tolerance; inspect WoE design matrix | Correlation is diagnostic, not an automatic drop rule |
| Fairness/proxy review | Required by decision-domain governance | Required by decision-domain governance |

GBM may be used for explicitly provisional exploration when mode is unknown. Switching
mode later requires rerunning transformations, criteria, lift comparisons, fairness and
reason-code checks, and validation. GBM results do not validate a scorecard.

See `null_handling.md` and `../domains/credit_scoring.md` for domain consequences.
