# Carrella (2021): Sugarscape parameter estimation

Paper: [No Free Lunch when Estimating Simulation Parameters](https://www.jasss.org/24/2/7.html), DOI `10.18564/jasss.4572`.
Scope: Sugarscape case study only; conclusions across all 41 models are outside this study.
Status: all 5,000 fresh author-model simulations validated; 25 estimator Table 8 values reproduced.
**Not a completed replication:** the other estimators and independent simulator work remain unfinished.

## Complete simulation replay

[The complete replay](results/full-author-replay-2026-10-15) reconstructs all 750,000 archived statistics from 5,000 fresh trajectories.
Every statistic matches the declared `rtol=1e-10, atol=1e-10` tolerance; maximum absolute error is `3.1833e-12`.
Each input retains all 501 observations, including repeated terminal states after extinction: 2,505,000 observations in total.
Five lossless trajectory archives preserve every raw CSV, independently verified against per-row SHA-256 hashes.
The fresh statistics, complete comparisons, and exact source-file assembly are retained alongside them.
The assembly explicitly records nine complete intervals spanning interrupted and resumed jobs; all interrupted evidence remains preserved.
No input or statistic was discarded. This completes the author-model replay, not the estimator comparisons or independent fork replication.

## Author implementation

[CarrKnight/nofreelunch](https://github.com/CarrKnight/nofreelunch), revision
`0400f750063215d06659a203f777b21da2e99231`, contains the NetLogo trade model, simulation driver,
5,000 parameter rows, 150 summary statistics per simulation, and estimation notebooks.
The repository's MIT license does not replace the embedded model's Creative Commons
Attribution-NonCommercial-ShareAlike 3.0 notice. Preserve both notices when using those sources.

The model identifies NetLogo 6.1.1. The Python driver specifies NetLogo 6.1 and 501 observations.
It tracks population, Gini, two resource totals, trade count, and mean price.
Each observable contributes six trajectory summaries and 19 snapshots, yielding 150 columns.
The five estimated parameters are population, mutation probability, two initial endowments, and reproduction wealth.
Random seed is a sixth input, excluded from estimation.

The driver samples 5,000 inputs uniformly, rounding population and resource/reproduction thresholds.
The notebooks use five-fold cross-validation, with 5,000 rows or the first 1,250 rows.
Their algorithms include rejection methods, regression, random forests, local regression, and neural networks.
Numerical Sugarscape estimator outputs are absent from the repository's `errors`, `contained`, and `intervals` trees at this revision.
The notebooks and source table remain available for recomputation.

## Source audit

Run from this repository root:

```sh
python3 replications/carrella_2021/audit_source.py --output /absolute/new/evidence/path
```

This downloads only pinned study sources, preserves licenses, hashes every artifact, and checks all 5,000 rows.
It rejects nonfinite data, invalid parameter ranges, duplicate columns, and unexpected dimensions.
Raw data stay in the requested evidence directory; `audit.json` records the checks and hashes.
Successful execution validates the input artifacts, not their generation or any paper result.

## Author-model replay

The first and last archived inputs (rows 0 and 4,999) each reproduce **150/150 summary statistics**
within floating-point tolerance `rtol=1e-10, atol=1e-10`.
Raw trajectories, comparisons, and runtime hashes are in [results/author-replay-2026-10-15](results/author-replay-2026-10-15).
These runs validate the author model and measurement pipeline; they do not validate DTL equivalence or estimator results.

The first attempt produced 126/150 matches because it used the newer connector's timing convention.
The [pre-2020 connector](https://github.com/quaquel/pyNetLogo/blob/becbe42ad5eda943181727a92413b51f2604bf4f/pyNetLogo/core.py)
records **before** each of 501 `go` calls. Observation indices are 0–500; model ticks stop advancing after extinction.
The [January 2020 change](https://github.com/quaquel/pyNetLogo/commit/2ac86b806d56edb8e85c675bd3c645e5079a7c7f)
adds an extra observation by default. That explains all 24 mismatched final/aggregate statistics.
The failed trajectory and comparison are preserved alongside the corrected runs.

Download [NetLogo 6.1.1](https://www.netlogo.org/downloads/archive/6.1.1/).
The Linux archive's platform-independent application JARs run headlessly on this macOS machine with OpenJDK 11.0.32.1.
The archive SHA-256 is `972ea6e0e9f04988c86a92d6bae305f824487832a3fd5b27eeefbd8b8c6b08c8`.
Use NumPy 1.26.4 for the comparison script. From the repository root:

```sh
/path/to/jdk/bin/java -Djava.awt.headless=true -cp '/path/to/NetLogo 6.1.1/app/*' \
  replications/carrella_2021/Replay.java \
  '/path/to/audit/data/sugarscape/Sugarscape trade.nlogo' \
  /path/to/audit/data/sugarscape/params_sugarscape.csv 0 10 /new/trajectories
python3 replications/carrella_2021/compare_replay.py /new/trajectories \
  /path/to/audit/data/sugarscape/sugarscape.csv --start 0 --stop 10 --output /new/comparison
```

Both commands reject existing output directories. Ranges are zero-based and half-open.
Use `4999 5000` and `--start 4999 --stop 5000` to replay the last archived input.
The batch runner reuses one workspace and resets the seed and model for every input, as the original worker pool does.

## Linear point-estimation results

The [predeclared experiment](POINT_ESTIMATION_PROTOCOL.md) independently recomputes five-fold cross-validation
for both dataset sizes with R's ordinary linear regression.
Using the newer `Rejection` sampling algorithm, **10/10 results match Table 8 at three-decimal precision**.
The historical `Rounding` algorithm matches 0/10; both results are retained.
This supports the newer sampling convention without identifying the authors' exact R installation.

[Recorded results](results/linear-2026-10-15/comparison.json) include all 62,500 held-out predictions,
fold memberships, baseline predictions, software details, and source hashes.
No confidence-interval coverage has been reproduced by this experiment.
The R script uses only base/recommended R functionality; the recorded runtime is R 4.6.1.

```sh
Rscript replications/carrella_2021/point_estimates.R \
  /path/to/audit/data/sugarscape /absolute/new/linear-results
```

## Additional original-estimator runs

The [estimator protocol](ESTIMATOR_PROTOCOL.md) runs the original five-fold routines with their full sampling and bootstrap settings.
For both dataset sizes, rejection estimation reproduces **10/10 Table 8 values at printed precision**.
[The 5,000-input result](results/rejection-5000-2026-10-15/comparison.json) includes all 25,000 held-out parameter predictions.
[Results](results/rejection-1250-2026-10-15/comparison.json) include fold inputs, predictions, interval endpoints, aggregate metrics, and runtime provenance.

The first quantile-random-forest run differs from published performance by at most 0.002.
[Its five comparisons](results/rf-1250-2026-10-15/comparison.json) retain the differences without declaring agreement or a negative replication.
The isolated seed and current package versions differ from the notebook's sequential random stream.
Repeated runs and historical dependency checks remain necessary for statistical interpretation.

Two other attempts failed while saving checkpoints because the filesystem filled.
Their partial outputs and logs remain in the local evidence directory; neither attempt counts as a scientific result.

The first semi-automatic one-dimensional run also completed all five folds.
[Its recorded comparisons](results/sabc1d-1250-2026-10-15/comparison.json) differ from published performance by up to 0.0132.
These stochastic differences remain unresolved; no negative conclusion is assigned.
`analyze_estimator.R INPUT_DIRECTORY NEW_OUTPUT_DIRECTORY` independently recomputes errors, coverage, and interval widths from saved fold predictions.
It validates all 6,250 predictions for this run and all 25,000 predictions for rejection with 5,000 inputs.

## Complete simulation ensemble

The [declared ensemble protocol](ENSEMBLE_PROTOCOL.md) covers every one of the 5,000 archived parameter/seed inputs.
All four fresh batches stopped with confirmed disk-write failures; no full-ensemble result is claimed.
Of 1,060 logged completions, four files were truncated or empty.
The comparison gate rejected those files before calculating paper statistics.
The runner now verifies all 501 rows, tick order, column count, and finite values before logging completion.
The **1,056 intact simulations reproduce 158,400/158,400 archived statistics**.
[Interrupted ensemble evidence](results/ensemble-interrupted-2026-10-15) retains every comparison, failure log, and truncated-file audit.
Restart ranges are [256,1250), [1516,2500), [2768,3750), and [4016,5000), using new output directories.
The original partial files remain preserved; infrastructure failures are not scientific disagreements.
The first 100 completed inputs from each batch reproduce **60,000/60,000 statistics across 400 simulations**.
[Partial comparisons](results/ensemble-prefix-validation-2026-10-15) retain every row hash and all freshly calculated statistics.
These ranges are [0,100), [1250,1350), [2500,2600), and [3750,3850); they do not represent all 5,000 inputs.
The optimized runner matches all 35,070 numeric trajectory values from the separate-call path on ten complete simulations.
Both paths reproduce 1,500/1,500 archived statistics; the optimized last-input replay also matches 150/150.
[Validation evidence](results/batch-validation-2026-10-15) includes trajectories, comparisons, hashes, and timing logs.
An intentionally corrupted reference statistic yields 1,499/1,500 matches and a nonzero exit, confirming that the comparison gate detects disagreement.

## Replication work remaining

1. Extend the Table 8 comparison to the remaining eight estimators and interval coverage.
2. Finish and validate all 5,000 author-model simulations.
3. Audit DTL trade, reproduction, mutation, welfare, and Gini semantics against this source.
4. Implement and validate the required study-specific behavior in this fork.
5. Complete both simulation ensembles and estimator comparisons, retaining failures and uncertainty.

Do not replace the traded two-resource model with the one-resource McCulloch variant.
Do not count analysis of the archived table alone as an independent simulation replication.

## Generalized additive model audit

The first 1,250-input generalized additive model run completed all five folds.
Independent recalculation validates all 6,250 held-out parameter predictions and the saved errors, interval coverage, and widths.
[Recorded results](results/gam-1250-2026-10-15/comparison.json) differ from all five printed Table 8 values.
Reproduction wealth performance is -3.002351 versus the published -1.329; no negative replication is assigned.
Both original Sugarscape notebooks set `bam=TRUE`, matching our runner and the original `mgcv::bam` call.
This estimator uses 10,000 residual/prediction-error draws per held-out observation for intervals; it does not use the other estimators’ 200-fit bootstrap.
Historical package versions and numerical fitting behavior remain to be investigated.

## Full-size quantile random forest

The 5,000-input run completed all five folds and independently validated all 25,000 held-out parameter predictions.
[Results](results/rf-5000-2026-10-15/comparison.json) retain raw fold outputs, interval coverage, runtime provenance, and the paper comparison.
Maximum absolute performance difference from Table 8 is 0.002295, on reproduction wealth; one of five values matches printed precision.
This single random realization does not establish statistical equivalence or a negative replication.
The full-size semi-automatic one-dimensional and local-linear results are documented below.

## Full-size semi-automatic estimation

The one-dimensional semi-automatic estimator completed all five folds on 5,000 inputs.
[Recorded results](results/sabc1d-5000-2026-10-15/comparison.json) include 25,000 independently validated held-out parameter predictions and interval metrics.
All published-score differences remain explicit; no equivalence or negative-replication verdict is assigned from a single random realization.

## Recovered local-linear outputs

The full-size local-linear invocation saved all five folds and final metrics, then exited with an unexpected-end-of-input parsing error.
The runner was edited during execution, so source-stream interference is suspected; the current file parses successfully.
[Recovered artifacts](results/loclin-5000-recovered-2026-10-15/comparison.json) independently validate all 25,000 predictions and interval metrics.
The failed process status remains explicit. A [clean invocation](results/loclin-5000-clean-2026-10-15/comparison.json) subsequently completed with exit status zero.
All five fold objects, final metrics, and 25,000 independently checked predictions are byte-identical to the retained artifacts.
All five Table 8 values match printed precision; this completes this estimator check, not the paper study.
Do not edit scripts while their interpreters are executing them. Future R launches use `Rscript -e` with `source()` to parse the complete runner before execution.

## Extinction timing correction

Input 3,110 reaches extinction at model tick 109. The original model then returns from `go` without advancing time.
The driver still records 501 observations, including repeated terminal states.
Our new validation incorrectly required 501 distinct ticks and stopped this batch; the author model was unchanged.
Validation now requires advancing ticks while agents survive and identical state after extinction.
Summaries and snapshots remain indexed by observation, matching the original driver.
[Evidence](results/extinction-validation-2026-10-15) reproduces 51,450/51,450 statistics for inputs 2,768–3,110 and 150/150 in a fresh extinct replay.
The fresh trajectory is byte-identical to the initially rejected one. There are now 1,399 uniquely validated inputs and 209,850 matching statistics.
The remaining part of this batch resumes at input 3,111 in a new directory.

## Historical-runtime diagnostic

[Both runtime diagnostics](results/gam-runtime-diagnostic-2026-10-15/comparison.json) completed five point fits on the identical first-fold input.
The historical container uses unmodified R 4.0.5 and mgcv 1.8-34; the host uses R 4.6.1 and mgcv 1.9-4.
Predictions differ, but first-fold reproduction-wealth RMSE is 6.43 on the host and 6.56 in the historical container.
These diagnostics omit interval simulation and confound several runtime changes; they do not establish a package-specific cause.
An audit of the full current-runtime study locates the large reproduction-wealth error in fold 2: RMSE 445.13 versus 3.55–6.43 in other folds.
The [same paired diagnostic on fold 2](results/gam-fold2-runtime-diagnostic-2026-10-15/comparison.json) completed both runtimes without changing data or model formulas.
All 2,500 prediction records and ten reported RMSE values were independently validated.
Reproduction-wealth RMSE is 445.127 in the current runtime and 376.224 in the historical runtime.
The same observation dominates both errors: its true value is 92, with predictions −6,945.811 and −5,856.279 respectively.
It accounts for 99.9924% and 99.9886% of the respective fold squared errors.
The tested historical runtime therefore does not remove the extrapolation problem.
It remains a plausible historical environment, not a verified author package pin; multiple runtime differences remain confounded.
All five folds remain in the study; no outlier is discarded.

## Failing-observation audit

[Fold 2 test observation 131](results/gam-outlier-audit-2026-10-15/audit.json) accounts for 99.9924% of that fold's reproduction-wealth squared error.
Its true value is 92; the prediction is −6,945.81. The input is archived simulation row 675.
Its final mean price is 20.9823, beyond the training range 0.3101–1.2538.
A fresh author-model trajectory matches all 150 archived statistics for this input, including the extreme price.
Thus this observation is reproducible simulation output, not an identified data-copy error.
The estimator extrapolation and runtime comparison remain under investigation; the observation stays in every reported metric.
