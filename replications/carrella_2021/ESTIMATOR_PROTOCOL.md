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

## Historical GAM version sensitivity

The first `mgcv` 1.9-4 run differs from all five published small-dataset values.
Compare the same five-fold workflow, data, seed zero, `bam=TRUE`, and original interval procedure using `mgcv` 1.8-34.
The CRAN archive dates that release to February 16, 2021, before the pinned author's April 2, 2021 commit.
This is a version-sensitivity experiment; no evidence identifies the authors' actual package version.
Do not change fitting options or select versions based on whether they approach the published values.
Retain all five comparisons, runtime information, source hashes, and installation failures.

The unmodified package initially fails compilation against R 4.6.1 because `DOUBLE_EPS` is no longer defined.
R 4.0's `R_ext/Constants.h` defines it as `DBL_EPSILON` from `float.h`.
A second installation attempt supplies exactly that compiler definition without changing the package source.
Even if successful, this isolates the package version under the current R runtime; it does not recreate the full historical environment.

The constant-only attempt then failed on pre-C23 function definitions.
Adding `-std=gnu17` passed those files, but current R headers introduce a `true` macro that collides with an old package variable.
All three installation attempts failed; no historical fit ran.
[Build evidence](results/gam-historical-build-2026-10-15) preserves the source archive hash, compiler settings, logs, and historical constant definition.
Use an older R toolchain for the next attempt instead of changing statistical source code to fit current headers.

The original full-size notebook explicitly passes `hcorr=TRUE` to local-linear and neural-network ABC.
The runner now specifies it explicitly too. The installed package already defaults to `TRUE`, so the earlier local-linear launch has identical correction settings.
The neural-network run retains the original package's ten-network ensemble and five hidden units; no smaller network or sample has been substituted.

## Source isolation for new runs

Use `Rscript -e 'source("replications/carrella_2021/run_estimator.R")' SOURCE METHOD SIZE SEED OUTPUT`.
`source()` parses the complete file before evaluating its expressions. Preserve active source files unchanged regardless.
A local-linear invocation ended with a parsing error after its numerical output was saved when the runner was edited during execution.
All saved predictions validate independently, but retain the nonzero exit and rerun through the isolated launch path.
