# Stability and Out-of-Time Validation

Offline IV on a single validation slice says nothing about whether a feature **holds
up over time**. In lead and credit scoring, distribution drift is the most common
reason a feature that looked great in development decays in production. Two checks:
**PSI** (distribution stability) and **OOT** (does the signal survive a fresh time
window).

---

## PSI — Population Stability Index

PSI measures how much a feature's (or score's) distribution has shifted between a
reference period and a later period.

```python
import numpy as np

def fit_psi_bins(reference: np.ndarray, bins: int = 10):
    """Fit continuous PSI edges on finite training/reference values."""
    finite = np.asarray(reference, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0 or bins < 2:
        raise ValueError("reference needs finite values and bins must be >= 2")
    edges = np.unique(np.quantile(finite, np.linspace(0, 1, bins + 1)))
    if edges.size < 3:
        raise ValueError("use explicit categorical bins for low-cardinality data")
    edges[0], edges[-1] = -np.inf, np.inf
    return edges

def psi_continuous(reference, actual, edges, eps: float = 1e-6):
    """Apply frozen edges and include missingness as an explicit final bucket."""
    reference = np.asarray(reference, dtype=float)
    actual = np.asarray(actual, dtype=float)
    if reference.size == 0 or actual.size == 0 or eps <= 0:
        raise ValueError("non-empty inputs and positive eps are required")
    def shares(x):
        if np.isinf(x).any():
            raise ValueError("infinite values are data defects, not missingness")
        missing = np.isnan(x)
        counts = np.r_[np.histogram(x[~missing], edges)[0], missing.sum()]
        return (counts + eps) / (counts.sum() + eps * counts.size)
    e, a = shares(reference), shares(actual)
    return float(np.sum((a - e) * np.log(a / e)))
```

For categorical features, fit an explicit training category set and missing bucket,
then map unseen values to `__OTHER__`; do not infer categorical handling from collapsed
numeric quantiles. Persist continuous edges and categorical levels and apply them
unchanged to every authorized comparison period. Report missing share, unseen-category mass, and
zero share separately where they are operationally meaningful.

> **The real low-cardinality failure is a false zero, not noise.** Naive quantile-bin
> PSI on a feature with few distinct values (e.g. ~90% zeros after `fill 0`, or any
> binary/categorical flag) collapses the edges into one bin and returns **PSI ≈ 0 —
> "stable" — even when the distribution has genuinely shifted.** Use the explicit
> categorical procedure above; for heavily zero-dominated continuous features, also
> monitor zero share directly.

### Thresholds (conventions, not statistical tests)

| PSI | Interpretation | Action |
|---|---|---|
| < 0.10 | Stable | OK |
| [0.10, 0.25) | Moderate shift | Investigate; keep with monitoring |
| ≥ 0.25 | Significant shift | **Investigate** — recalibrate or drop, don't auto-drop |

These 0.10 / 0.25 cutoffs are **rules of thumb** (commonly attributed to Siddiqi), not significance
tests. PSI is **bin- and sample-size-dependent**: with 10 bins and small samples it
inflates; with millions of rows trivial shifts cross the line. Calibrate to your
own data and **do not auto-drop on PSI alone** — many genuinely useful credit/lead
characteristics breach 0.25 from seasonality or portfolio growth. A breach means
*investigate* (real drift → retrain cadence; pipeline breakage → fix), not delete.

- Track stability at three levels, which are **not** the same statistic:
  - **Feature-distribution PSI** — raw distribution of each feature across periods (the
    code above).
  - **Characteristic contribution drift** — use the institution's declared formula;
    terms such as CSI are not defined uniformly across organizations.
  - **Score PSI** — PSI of the final model score/points itself.
  Applicable governance may require characteristic- and score-level monitoring. Declare
  the formula, baseline, threshold, and jurisdiction/product applicability before use.
- A strong-IV feature whose distribution has genuinely moved is a liability: the model
  was trained on a distribution that no longer exists. But confirm it's drift, not a
  broken join, before acting.

> Causes of high PSI worth distinguishing: genuine population change (acceptable, may
> need retraining cadence) vs **pipeline breakage** (a join changed, a source backfilled,
> units changed) — the latter masquerades as drift and must be fixed, not tolerated.

---

## IV by period (not just pooled)

Pooled IV averages over time and hides decay. During selection, compute IV per
**development period** and inspect the trend. OOT period diagnostics may be reported
only after opening the frozen OOT evaluation and cannot change that configuration.

```python
iv_by_period = {
    p: iv_from_frozen_bins(df[df.period == p], feat, label, train_bins)
    for p in periods
}
```

`train_bins` includes edges/categories and missing/unseen rules fitted on train; never
refit it independently by period.

- Flat or rising IV → durable signal.
- IV high early, collapsing recently → the feature is **dying**; do not rely on it,
  even if pooled IV looks fine.
- IV spiking in one period only → likely a data artifact in that period.

---

## Out-of-Time (OOT) validation

The most important check the original checklist omitted. Validation slices drawn
*randomly* from the same period as training overstate performance because they share
the same regime and the same selection noise.

### Protocol

1. **Split by time, not at random.** Train + validation on `[t0, t1)`; hold out an
   **OOT window** `[t1, t2)` that comes strictly *after* — chronologically, the way
   production will see data.
2. Do **all** feature engineering decisions (IV thresholds, binning, redundancy,
   selection) on **train/validation only**. The OOT window is untouched during
   development (Anti-pattern #13).
3. After the complete pipeline is **locked**, evaluate **once** on OOT:
   - Report Gini/AUC on validation vs OOT and the **drop**.
   - A modest drop (regime change) is expected. A large drop signals overfitting to
     the development period or a leaky/selection-biased feature.
4. If the frozen pipeline fails its predeclared OOT criterion, record NO-GO. Do not
   alter features or thresholds and reuse that window as final confirmation; obtain a
   new later holdout after any revision.

```
   |── train + validation [t0,t1) (decisions) ──|── OOT [t1,t2) ──|
   t0                                            t1                       t2
```

### Why OOT also defends against selection bias

When you screen many candidate features, some look predictive by chance on the
validation slice. Spurious features rarely reproduce on a fresh time window, so OOT
is your defense against multiple-testing inflation as well as against drift.

---

## What to record for Go/No-Go

- PSI per feature across periods (max and latest).
- IV-by-period trend (stable / decaying / spiky).
- Validation vs OOT Gini/AUC for the feature set, with the drop.
- Any feature dropped specifically for instability, and why.
