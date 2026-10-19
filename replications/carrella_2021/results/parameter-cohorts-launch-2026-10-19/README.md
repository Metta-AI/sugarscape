# Outcome-blind parameter-space diagnostic launch

Ten original parameter rows were selected using only the five parameter columns.
Start nearest the range-normalized midpoint, then greedily maximize distance to the selected set.
Lowest row index breaks ties. Independent NumPy and scalar implementations select the same ten rows.
The plan fixes 64 seeds per engine per setting: 1,280 runs with 501 observations each.
The same integer seeds do not align NetLogo and Python random streams.

Each setting uses the unchanged native model and frozen independent engine.
Existing full-trajectory audits and distribution-comparison tools run after each successful cohort.
Simulation dispatch is sequential, bounded at 600 seconds per cohort and 6,000 seconds total.
Analysis commands have separate 60-second bounds. Storage is capped at 512 MiB with a 2 GiB free-space gate.
Failures remain in the ledger; no substitution, retry, or exclusion is authorized by this protocol.

Report six empirical-distribution distances, their joint permutation comparison, and two rare-event comparisons per setting.
Apply Holm adjustment across all 30 cohort-level tests before flagging differences.
Incomplete cohorts prevent a complete ten-setting conclusion.
Failure to reject does not establish equivalence or resolve historical Table 8 estimator discrepancies.

The first native cohort has started and emitted three complete trajectories.
No completed ensemble or paper-level result is claimed here.
