# Complete EC / Rule M cohort

All 50 frozen released-code seeds complete 20,000 ticks, totaling 1,000,050 observations.
Remote audit and fresh local readback verify all 500 run files. The union preserves all 202 prior records exactly.
Total audited coverage is 252 inputs and 5,040,252 observations: 250 released-code and two paper-table inputs.
Archive: 33,987,091 bytes; SHA256 `53a1dd0961674d1ae95764029ba8acff1c215594e5600e4a2315ba58d0d78c19`.
Raw archive and extracted trajectories remain in `/Users/relh/Code/workspace/sugarscape-replication-evidence/brearcliffe-ec-rule-m-snapshot-001`.

Independent R verifies 320,016 means, 320,016 sample standard deviations, and 14 endpoint intervals using 20,000 retained whole-run bootstrap draws.
Maximum scaled errors: means 1.28e-15, standard deviations 1.67e-14, endpoint intervals 6.50e-16.
This checks arithmetic, not paper fidelity or the random-number generator.

The corrected horizontal calibration yields 3,800 visible and 76 unresolved curve records.
Thirteen of fourteen endpoint range comparisons overlap the paper raster intervals.
EC mean vision is 1.10, below the paper interval 1.218187912–1.267234952.
Its pointwise bootstrap interval is 1.02–1.22, narrowly overlapping that raster interval.
Neither this overlap nor the other endpoint comparisons establish equivalence or a validated negative replication.

Five of sixteen released-code pairings now have complete cohorts.
The larger ensemble continues; paper-table sensitivity, historical seeds, and independent fork implementation remain outstanding.
The collector launch initially used an invalid wake-timeout flag and was rejected before execution; corrected launch cmd-65g88 completed successfully.
Before archive download, the disk check verified 802,684,928 available bytes against 405,162,537 required bytes, including a 256 MiB reserve.
No simulation was restarted and no existing evidence was removed.
