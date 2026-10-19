# Paper-table EC / Rule M complete cohort

All 50 frozen replication seeds complete 20,000 steps: 1,000,050 observations including initial states.
The cumulative raw audit covers 1,002 unique inputs and 20,041,002 observations, preserving all 952 prior records exactly.
Coverage is 750 released-code and 252 paper-table inputs: fifteen and five complete pairings respectively.

All 50 full trajectories are byte-identical to their paired released-code trajectories.
This confirms the parameter changes leave this non-reinforcement-learning pairing unchanged; it does not identify historical learning settings.

Independent R verifies 320,016 means, 320,016 sample standard deviations, and 14 endpoint metrics with 20,000 whole-run bootstrap repetitions.
Maximum scaled errors are 1.275e-15 for means, 1.666e-14 for standard deviations, and 6.492e-16 for interval endpoints.
The corrected paper raster comparison has 3,800 visible records and 76 unresolved records.
Thirteen of fourteen endpoint mean ranges overlap the paper ranges.
EC vision ends at mean 1.10 versus plotted range 1.21819–1.26723; its pointwise bootstrap interval 1.02–1.22 overlaps that range.
Raster ranges are not statistical confidence intervals; these descriptive comparisons do not establish equivalence or a negative replication.

The raw archive is preserved by [the durable-evidence report](../paper-ec-rule-m-durable-evidence-2026-10-19).
Full-paper completion still requires both frozen interpretations, all pairings, figure synthesis, and investigation of unresolved source/measurement differences.
