# Remaining estimator and coverage experiments

Run the pinned author's `setup.R` fitting and cross-validation functions on the complete archived reference table.
The wrapper records complete fold inputs, outputs, and random state; it does not substitute another estimator implementation.
Use all five parameters, all 146 nonconstant summaries, five folds, and the first 1,250 or all 5,000 rows.
Use the validated `Rejection` discrete sampler and cross-validation seed zero.
Retain the original 200 bootstrap fits and interval procedures where the source uses them.

The first pass uses estimator seed zero separately for each method and size.
This differs from the notebook's shared, sequential random stream across estimator calls.
It makes each experiment independently repeatable, but does not promise identical stochastic forest or neural-network realizations.
Record both point performance and interval coverage. Keep all methods, including those with published `NA` values.
An error is a failed execution requiring diagnosis; it is not a numerical result or a completed negative replication.

Compare every finite published entry in `published_table8.json` at its three-decimal precision.
The first pass is a reproduction audit, not a statistical equivalence claim for stochastic estimators.
Investigate mismatches using package versions, algorithms, random streams, and additional fixed-seed repeats before any negative verdict.
Do not replace a difficult algorithm or shrink its data, folds, or bootstrap counts to manufacture agreement.

Retain logs, package versions, full fold results, and failure artifacts.
The archived paper's aggregate coverage statements span other models, so Sugarscape-only coverage cannot validate those aggregate claims.
