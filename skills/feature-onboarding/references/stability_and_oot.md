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

def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10, eps: float = 1e-6):
    """PSI of `actual` vs an `expected` reference.
    Continuous features: quantile bins of `expected`. Low-cardinality features:
    one bin per distinct value -- otherwise the quantile edges collapse to a single
    bin and a real shift (e.g. a binary 30%->50%) silently returns PSI = 0."""
    edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:                       # <=2 distinct edges -> discrete feature
        cats = np.union1d(np.unique(expected), np.unique(actual))
        e = np.array([(expected == c).mean() for c in cats]) + eps
        a = np.array([(actual   == c).mean() for c in cats]) + eps
    else:
        edges[0], edges[-1] = -np.inf, np.inf
        e = np.histogram(expected, edges)[0] / len(expected) + eps
        a = np.histogram(actual,   edges)[0] / len(actual)   + eps
    e, a = e / e.sum(), a / a.sum()          # renormalize after eps so both sum to 1
    return float(np.sum((a - e) * np.log(a / e)))
```

> **The real low-cardinality failure is a false zero, not noise.** Naive quantile-bin
> PSI on a feature with few distinct values (e.g. ~90% zeros after `fill 0`, or any
> binary/categorical flag) collapses the edges into one bin and returns **PSI ≈ 0 —
> "stable" — even when the distribution has genuinely shifted.** The discrete branch
> above prevents this; for heavily zero-dominated continuous features, also monitor the
> zero-share directly as its own series.

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
  - **CSI (Characteristic Stability Index)** — the *score-attributed* shift: the same
    distribution deltas **weighted by the characteristic's WoE / points contribution**,
    so it measures how much each feature *moves the score*, not just how much it moves.
  - **Score PSI** — PSI of the final model score/points itself.
  Regulators expect characteristic-level (CSI) **and** score-level monitoring; a feature
  can drift a lot in distribution yet barely move the score (low CSI), or vice versa.
- A strong-IV feature whose distribution has genuinely moved is a liability: the model
  was trained on a distribution that no longer exists. But confirm it's drift, not a
  broken join, before acting.

> Causes of high PSI worth distinguishing: genuine population change (acceptable, may
> need retraining cadence) vs **pipeline breakage** (a join changed, a source backfilled,
> units changed) — the latter masquerades as drift and must be fixed, not tolerated.

---

## IV by period (not just pooled)

Pooled IV averages over time and hides decay. Compute IV **per period** and look at
the trend.

```python
iv_by_period = {p: woe_iv(df[df.period == p], feat, label)[0] for p in periods}
```

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

1. **Split by time, not at random.** Train + validation on `[t0, t1]`; hold out an
   **OOT window** `[t1, t2]` that comes strictly *after* — chronologically, the way
   production will see data.
2. Do **all** feature engineering decisions (IV thresholds, binning, redundancy,
   selection) on **train/validation only**. The OOT window is untouched during
   development (Anti-pattern #13).
3. After the feature set is **provisionally locked**, evaluate **once** on OOT:
   - Report Gini/AUC on validation vs OOT and the **drop**.
   - A modest drop (regime change) is expected. A large drop signals overfitting to
     the development period or a leaky/selection-biased feature.
4. If a feature's contribution evaporates OOT, drop it regardless of in-sample IV.

```
   |──── train + validation (decisions here) ────|── OOT (confirm once) ──|
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
