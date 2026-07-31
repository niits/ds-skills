# Lag Horizon Analysis

Choose retained horizons from measured evidence, not a default set.

For each candidate lag:

1. Establish earliest source period and exact calendar/business-period semantics.
2. Compute eligible coverage; lag `N` first becomes available at `data_start + N`.
3. Measure redundancy among horizons and with level features.
4. Compare predictive screening and paired validation lift by horizon.
5. Retain only horizons supported by coverage, stability, and incremental evidence.

Define lag `N` as exactly `N` periods, not `N` preceding rows. Build a complete
entity-period spine or use an exact-period keyed join. Never request a horizon longer
than source history supports. In scorecard mode, retained lags still enter through the
declared WoE representation.
