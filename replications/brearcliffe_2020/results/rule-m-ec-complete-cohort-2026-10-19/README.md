# Complete Rule M / EC cohort

The [horizontal calibration correction](../horizontal-calibration-correction-2026-10-19) supersedes this directory’s curve comparison. Simulation and arithmetic evidence remain unchanged.
All 50 prospectively frozen seeds complete 20,000 ticks, totaling 1,000,050 observations.
The 49 remote runs passed full-trajectory audit before snapshotting; fresh local readback verified all 490 files.
The union with previous work contains 94 inputs and 1,880,094 observations. All 45 prior audit records are unchanged.
Archive SHA256: `8d45d7c83715aa2727ee9becb4a64e63ee22dd2e9bbdaede3c2c4e83a27506f6` (33,382,701 bytes).
The retained archive and extracted trajectories are under `/Users/relh/Code/workspace/sugarscape-replication-evidence/brearcliffe-rule-m-ec-snapshot-001`.

The full successful Python summary and independent R workflow now pass.
R recomputes 320,016 means, 320,016 sample standard deviations, and 14 endpoint intervals using the retained 20,000 whole-run bootstrap draws.
Maximum scaled mean error is 1.17e-15; maximum scaled standard-deviation error is 3.60e-14.
R checks the arithmetic, not the random-number generator or published-result fidelity.

The curve comparison retains 3,810 visible and 194 unresolved raster records.
Twelve of fourteen endpoint comparisons overlap the paper's raster intervals after horizontal calibration uncertainty.
EC mean vision is 1.22, above the paper's 1.18655–1.21819 raster interval; our pointwise bootstrap interval is 1.12–1.34.
Rule M maximum age averages 5,203.06, below the paper's 5,406.01–6,329.51 raster interval; our bootstrap interval is 4,880.396–5,535.5.
Both sampling intervals overlap the corresponding raster intervals. This does not establish equivalence or a negative replication.
Paper seeds and between-run uncertainty remain unknown; neighboring pixels are dependent.

This is one of sixteen pairings. The larger ensemble continues unchanged, and independent fork implementation remains outstanding.
Neither method in this pairing uses the disputed reinforcement-learning hyperparameters, so this result cannot resolve that discrepancy.
