# Complete ten-setting parameter-space diagnostic

All ten settings complete: 640 author-model and 640 independent-model runs, with 641,280 audited observations and no exclusions.
The outcome-blind selection and seeds match the frozen plan.
Five original cohorts completed within their bounds. Five timed out; separate bounded recoveries completed only their 82 unfinished independent inputs.
Original timeouts and interrupted outputs remain preserved. Dispatch completion does not erase those failures.

Every setting passes archive readback and repeated full-trajectory audits.
The aggregate validates frozen inputs, constituent completion receipts, disjoint recovery seeds, source trajectories, and all ten comparison inputs.
A fresh aggregate invocation reproduces every output byte-for-byte.
Independent R confirms 60 empirical-distribution statistics exactly, 20 Fisher tests, and all 30 Holm adjustments within 1e-12.
R does not independently regenerate Python's permutation samples.

No comparison rejects at the predeclared familywise 0.05 level; all 30 Holm-adjusted p-values equal 1.
The ten unadjusted joint permutation p-values range from 0.10985 to 0.9489.
Maximum empirical-distribution differences across the six metrics range from 0.15625 to 0.265625.
Neither predeclared rare event occurs in these ten settings for either engine.

These results do not detect a difference under this diagnostic. They do not establish equivalence, equal rare-event rates, or behavior across every parameter setting.
The earlier single-setting rare-event experiment remains separate evidence and is not pooled here.
Historical estimator discrepancies remain unresolved; no whole-paper completion is claimed.

Reproduce with `summarize-recovered.py RUN_DIRECTORY NEW_OUTPUT`, then `Rscript crosscheck.R NEW_OUTPUT NEW_R_OUTPUT`.
The run directory must retain the original sources, frozen inputs, failed attempts, and recovery provenance referenced by the manifests.
