# Complete EC / EC cohort

All 50 frozen released-code seeds complete 20,000 ticks, totaling 1,000,050 observations.
Remote audit and fresh local readback verify all 500 run files. All 253 prior input records remain unchanged.
Total audited coverage is 303 inputs and 6,060,303 observations: 300 released-code and three paper-table inputs.
Archive: 28,710,641 bytes; SHA256 `ba2627478b9792e42f6210714617c10f511be8c2dbca167ec243b6a867a06ed6`.
Raw archive and extracted trajectories remain in `/Users/relh/Code/workspace/sugarscape-replication-evidence/brearcliffe-ec-ec-snapshot-001`.

Independent R verifies 320,016 means, 320,016 sample standard deviations, and 14 endpoint intervals using 20,000 retained whole-run bootstrap draws.
Maximum scaled errors: means 1.47e-15, standard deviations 7.15e-15, endpoint intervals 5.54e-16.
This checks arithmetic, not paper fidelity or the random-number generator.

The corrected horizontal calibration yields 3,274 visible and 602 unresolved curve records.
Only two of twelve visible endpoint range comparisons overlap the paper raster intervals; two endpoints remain unresolved.
These discrepancies require investigation before any negative replication claim.
For example, breed A mean vision is 1.88015 against paper ink 2.26092–2.35195; its pointwise bootstrap interval is 1.60895–2.16420.
Breed B mean vision is 2.16945 against paper ink 1.78414–1.85597; its interval is 1.88475–2.45992.
Several endpoint orderings reverse between breeds. Breed identities were retained as recorded, without swapping them to improve agreement.
Historical seeds, paper uncertainty, breed mapping, and implementation fidelity remain unresolved explanations.
Pointwise intervals do not provide simultaneous coverage across metrics or include uncertainty in the paper results.

Six of sixteen released-code pairings now have complete cohorts. The larger ensemble continues.
Paper-table sensitivity and an independent fork implementation remain outstanding; this is not a completed paper replication.
The publication script initially expected uncompressed bootstrap indices; the retained failure was corrected to copy the existing gzip artifact.
Scientific audits passed before that packaging failure. No simulation was restarted.
