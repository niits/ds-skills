# Redundancy and Incremental Lift

Two separate questions, often collapsed into one and done badly:

1. **Redundancy** — does this feature *duplicate* information already present?
2. **Lift** — does adding it *improve the model*?

A feature can be non-redundant yet add no lift (noise orthogonal to signal), or
redundant yet still add lift (correlated but complementary in interactions). You
need both checks.

---

## 1. Redundancy — beyond pairwise Pearson

### Pearson is necessary but not sufficient

Pearson catches only **linear** pairwise duplication. Two failure modes it misses:

**(a) Non-linear / monotonic duplication.** Two features that are monotone
transforms of each other (e.g. `balance` and `log(balance)`, or rank vs raw) can
have modest Pearson but are informationally identical to a tree. Use **Spearman**
(rank correlation) — it aligns with the rank-based spirit of WoE and ranking models.

```python
# Report both; Spearman is the stricter redundancy screen for monotone duplicates
corr_pearson  = df[cols].corr(method="pearson")
corr_spearman = df[cols].corr(method="spearman")
```

**(b) Multivariate redundancy.** A new feature can be near-orthogonal to *each*
existing feature individually yet be an exact linear combination of *several*.
Pairwise `|r|` never sees this. Two robust checks:

```python
# Exploratory raw-source VIF: how well is the new feature explained by existing inputs?
# CRITICAL: statsmodels' variance_inflation_factor needs an intercept column.
# Without add_constant it regresses through the origin and reports VIFs that are
# wildly inflated for any feature whose mean is large vs its variance (e.g. ~130
# instead of ~1). This is the classic statsmodels VIF gotcha.
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
X = add_constant(df[existing_cols + [new_col]].dropna())   # adds 'const' at col 0
vif_new = variance_inflation_factor(X.values, X.columns.get_loc(new_col))
# VIF > 5  -> notable multicollinearity ; VIF > 10 -> severe (drop or combine)
```

```python
# Or directly: R^2 of regressing the new feature on the existing set (sklearn fits an
# intercept by default, sidestepping the through-origin VIF gotcha above).
# High R^2 means the new feature adds little NEW variance.
from sklearn.linear_model import LinearRegression
d = df[existing_cols + [new_col]].dropna()        # align rows; this skill keeps NaNs
r2 = LinearRegression().fit(d[existing_cols], d[new_col]).score(d[existing_cols], d[new_col])
# r2 > 0.9 -> the existing set already reconstructs it
```

> Naming: `new_col` is the **single** feature whose redundancy you're testing; `new_cols`
> (in the lift section) is the **whole candidate group** being onboarded. **Caveat on
> `dropna()`**: listwise dropping across `existing_cols + new_col` can shed most rows
> when this skill deliberately keeps NaNs (GBM mode), biasing the redundancy estimate
> toward the dense subpopulation. Check how many rows survive; if it collapses, compute
> redundancy on an explicitly imputed copy *for the diagnostic only* (never feed that
> imputation to the model).

### Mode dependence

- **Scorecard mode**: redundancy tolerance is **low**. Compute coefficient-collinearity
  diagnostics on the actual train-fitted WoE design matrix, with an intercept. Raw
  source-column VIF/R² is only an exploratory data diagnostic.
- **GBM mode**: trees tolerate correlated inputs. Redundancy mainly costs
  interpretability and a little training time. Be lenient, but still drop true
  duplicates to keep SHAP attributions clean.

### Pairwise decision table

| `|r|` (Spearman) | Action |
|---|---|
| ≥ 0.7 | Investigate with mode-specific ablation and governance needs |
| [0.5, 0.7) | Compare stable conditional/group lift |
| [0.3, 0.5) | Keep — incremental info |
| < 0.3 | Keep — orthogonal |

Treat these as default screening bands. Final retention depends on stable validation
ablation and model-mode governance, not correlation or IV alone.

---

## 2. Incremental lift — the decision step

IV and correlation are **filters**. The *decision* is whether the model gets
better. This is the embedded/wrapper step the original checklist was missing.

### Protocol (train/validation only — the OOT slice stays untouched)

> **Do not touch the out-of-time (OOT) window here.** Per-feature lift decisions
> happen on a validation holdout carved from the development data. The OOT window is
> consumed exactly **once**, on the final locked set, in Phase 8 (Anti-pattern #13).
> Fitting on train and scoring on OOT for every candidate would burn OOT as a
> selection set — the single most common way this step goes wrong.

```python
# Fit on TRAIN; measure the lift delta on a VALIDATION holdout. OOT is not used here.
from sklearn.metrics import roc_auc_score

def gini(y, p):                      # Gini = 2*AUC - 1, standard in credit
    return 2 * roc_auc_score(y, p) - 1

base = fit_model(X_train[existing_cols],            y_train)
cand = fit_model(X_train[existing_cols + new_cols], y_train)
delta = gini(y_val, cand.predict_proba(X_val[existing_cols + new_cols])[:, 1]) \
      - gini(y_val, base.predict_proba(X_val[existing_cols])[:, 1])
# Keep the feature group only if delta exceeds a pre-agreed, noise-aware threshold.
```

- Set the keep-threshold *before* looking (e.g. ΔGini ≥ 0.005), and account for
  uncertainty. Prefer repeated rolling/expanding chronological validation folds,
  refitting every learned transformation and model only on each fold's past-training
  partition, so the delta is not a one-period fluke.

### Embedded importance as a cross-check

For GBM mode, **permutation importance** or **SHAP** on validation can show how a fitted
model uses or attributes a feature, but neither proves incremental lift. Correlated
inputs make individual attribution unstable; use grouped or conditional permutation
where appropriate and keep paired baseline-versus-candidate validation ablation as the
decision evidence.

```python
from sklearn.inspection import permutation_importance
imp = permutation_importance(model, X_val, y_val, scoring="roc_auc", n_repeats=10)
# Near-zero marginal importance is diagnostic, not an automatic drop rule.
```

### Why low-IV features sometimes survive here

Univariate IV evaluates a feature alone. Interaction-only features (valuable only
*conditioned* on another feature) show near-zero IV but real lift. The lift step is
the only place these are caught — which is why **IV < 0.02 is a "drop unless it adds
lift" rule, not an automatic delete.**

---

## 3. Multiple-testing / selection bias

When you screen dozens of candidate features by IV on the validation set, **some will
look predictive by chance**. Guards:

- Decide the candidate list and thresholds **before** screening; don't expand the
  search after seeing results.
- The **OOT confirmation** (see `stability_and_oot.md`) is the real defense: spurious
  features rarely survive a fresh time window.
- Be suspicious of a feature that is strong on validation but whose strength is not
  reproducible across CV folds or time periods — that is selection noise, not signal.
