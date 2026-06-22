# Predictive Power: IV / WoE and the binning traps

## Scope — read this first

**IV and WoE are defined for a binary target.** They measure how well a feature
separates two classes. They do **not** apply directly to regression or multiclass.

| Target type | Univariate screen to use |
|---|---|
| Binary (default here) | WoE → IV |
| Multiclass | One-vs-rest IV per class, or mutual information |
| Regression | Correlation ratio (η), mutual information, or binned target-mean monotonicity |
| Ranking / recsys relevance | Treat graded relevance as binary at a cutoff, or use rank-IC (Spearman of feature vs label) |

The rest of this file assumes **binary**.

---

## Two methods — know which one you're using

There are two distinct WoE/IV computations and they are NOT interchangeable:

- **Quick quantile-bin screen** (below) — fast, for the Phase 4 *filter* across many
  candidates. Uses equal-frequency bins + Laplace smoothing as a guard. The smoothing
  keeps empty bins finite but **biases IV slightly downward** for sparse bins, so this
  is a *screening* number, not a final scorecard IV.
- **Monotonic / optimal supervised binning** (scorecard mode, see below) — the
  *authoritative* method for credit. It merges bins to a minimum size and enforces
  monotonic event-rate, so zero-event bins never arise and no smoothing is needed.
  Use a library binner (e.g. `optbinning.OptimalBinning`) — a validator will expect
  IV computed this way, not on smoothed quantile bins.

### Quick quantile-bin screen

```python
import numpy as np
import pandas as pd

def woe_iv(df: pd.DataFrame, feature: str, label: str,
           n_bins: int = 10, min_events: int = 5, smoothing: float = 0.5):
    """Fast IV/WoE screen with three guards home-grown versions often miss:
       (1) quantile binning that collapses gracefully on ties,
       (2) Laplace smoothing so zero-event/zero-nonevent bins don't -> +/-inf,
       (3) a min-event guard so 'non-monotonic' isn't just small-sample noise.
    NOTE: smoothing biases IV downward on sparse bins -> screening only, not the
    scorecard IV. It FLAGS unreliable bins (g['reliable']); it does not merge them.
    For the authoritative number use monotonic/optimal binning (below).
    """
    s = df[[feature, label]].copy()

    # (1) quantile bins; duplicates='drop' handles features with many ties / zeros
    s["bin"] = pd.qcut(s[feature], q=n_bins, duplicates="drop")
    # NaNs form their own bin (do NOT silently drop them - missingness can be signal)
    s["bin"] = s["bin"].cat.add_categories(["__NULL__"]).fillna("__NULL__")

    tot_e = s[label].sum()
    tot_ne = (1 - s[label]).sum()

    g = s.groupby("bin", observed=True)[label].agg(["sum", "count"])
    g.columns = ["events", "n"]
    g["nonevents"] = g["n"] - g["events"]

    # (2) Laplace smoothing -> no infinities
    g["dist_e"] = (g["events"] + smoothing) / (tot_e + smoothing * len(g))
    g["dist_ne"] = (g["nonevents"] + smoothing) / (tot_ne + smoothing * len(g))
    g["woe"] = np.log(g["dist_e"] / g["dist_ne"])
    g["iv_part"] = (g["dist_e"] - g["dist_ne"]) * g["woe"]
    g["event_rate"] = g["events"] / g["n"]

    iv = g["iv_part"].sum()
    # (3) flag unreliable bins
    g["reliable"] = g["events"] >= min_events
    return iv, g
```

### Why each fix matters

1. **`duplicates="drop"` on `qcut`** — a feature with lots of zeros (common after
   `fill 0` for absence-based features) cannot be cut into 10 equal-frequency bins.
   Naive `qcut(...,10)` throws or produces empty bins. Dropping duplicate edges
   yields *fewer but valid* bins.

2. **Laplace smoothing** — a bin with 0 events gives `WoE = log(0) = -inf` and an
   infinite IV contribution. Smoothing (`+0.5`) keeps it finite and bounded. Never
   report an IV computed without handling empty bins; it is meaningless. **But** the
   right fix in scorecard mode is to *not have* empty bins: merge to a minimum bin
   size (monotonic/optimal binning) so smoothing is unnecessary. Smoothing is the
   pragmatic guard for the *screening* path only, and it nudges IV down on sparse bins.

3. **Min event count per bin** — with a rare positive class (say 2% event rate),
   10 bins leave ~0.2% of events per bin → `event_rate` bounces around from noise.
   *Before* calling a feature "non-monotonic", check `reliable`. If most bins are
   unreliable, **re-bin with fewer bins** (5, or event-count-based bins) rather than
   concluding the relationship is non-linear. Note the `min_events=5` default only
   *flags* thin bins; it does **not** merge them. For rare-event work raise the floor
   (e.g. ≥ 30 events/bin) or use the event-count-based / monotonic binning recommended
   below — the flag is a tripwire, not a fix.

---

## Rare-event / imbalanced labels

Lead scoring and credit default are often **highly imbalanced** (1–5% positive).
Consequences:
- Equal-frequency bins put too few events per bin → unstable WoE.
- Prefer **monotonic binning with a minimum event-count constraint** per bin
  (merge adjacent bins until each has ≥ `min_events`).
- Do **not** rebalance/oversample *before* computing IV — it inflates apparent signal.
  Compute IV on the natural distribution; resample only for model fitting if needed.

---

## Monotonic supervised binning (scorecard mode)

In **scorecard mode** features enter the model as WoE, and regulators expect a
**monotonic** relationship (more of X → monotonically more/less risk). Use a
supervised binning that enforces monotonic event-rate across bins (e.g. an
isotonic / tree-based binner such as `optbinning`'s `OptimalBinning`, or a manual
merge-until-monotonic routine). A non-monotonic raw feature can still be usable if
it bins into a monotonic WoE transform — but document the transform.

In **GBM mode** you do not need monotonic binning; trees learn splits. Keep raw
values. (Optionally apply monotone constraints in the booster for explainability.)

---

## IV thresholds — heuristics, not laws

| IV | Label | Note |
|---|---|---|
| < 0.02 | Useless (univariate) | Drop **unless** kept for a known interaction |
| [0.02, 0.1) | Weak | Keep only if orthogonal AND adds lift |
| [0.1, 0.3) | Medium | Keep |
| [0.3, 0.5) | Strong | Keep |
| [0.5, 0.8) | "Suspicious / too good to be true" | **Verify** point-in-time + tautology (Phase 6) before trusting |
| ≥ 0.8 | Very high | **Verify hard** — but do NOT auto-reject (see caveat) |

The bands up to "> 0.5 = suspicious" are the classic Siddiqi credit-scoring rules of
thumb. The "> 0.8" row is **our** flag, not Siddiqi's, and it means *verify*, not
*reject*: a single strong characteristic (worst-ever delinquency, utilization, a
clean bureau attribute) can legitimately reach IV 0.5–1.0+ without any leakage.
High IV **raises the priority of the Phase 6 checks; it does not condemn the
feature.** Treat all bands as **screening heuristics** — the final keep/drop decision
is **incremental lift** (Phase 5), not IV.

> **The trap IV cannot catch**: univariate IV evaluates each feature alone. A
> feature with IV 0.01 can be highly valuable inside an interaction, and a feature
> with IV 0.6 can add nothing once correlated features are already in the model.
> Use IV to prune the obviously-dead; let the model judge the rest.
