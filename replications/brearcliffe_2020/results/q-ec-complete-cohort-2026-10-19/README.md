# Q-learning / EC complete cohort

All 50 released-code inputs pass full 20,001-row trajectory audits.
The cumulative audit preserves all 453 previous inputs exactly and adds 50, reaching 10,060,503 observations.
Independent R checks verify 320,016 means, 320,016 sample standard deviations, and fourteen bootstrap intervals.
Maximum scaled errors are below 1.75e-14.

Ten of fourteen endpoint mean ranges overlap the corrected paper raster bounds.
Q-learning sugar and age, EC vision, and EC maximum age do not overlap at the mean-range level.
Each has an overlapping pointwise 95% bootstrap interval.
Of 3,876 curve records, 3,773 are visible and 103 remain unresolved.
Image bounds are not confidence intervals; the bootstrap intervals do not establish equivalence or simultaneous coverage.
Historical seeds and parameter interpretation remain unresolved, and this is not a completed-paper verdict.

The snapshot and readback scripts preserve source configurations, complete trajectories, and member hashes.
`audit.json` records all 503 audited inputs; `comparison-summary.json` retains all endpoint values.
