# Carrella (2021): Sugarscape parameter estimation

Paper: [No Free Lunch when Estimating Simulation Parameters](https://www.jasss.org/24/2/7.html), DOI `10.18564/jasss.4572`.
Scope: Sugarscape case study only; conclusions across all 41 models are outside this study.
Status: all 5,000 fresh author-model simulations validated. All 75 reported Table 8 values evaluated; 38 match printed precision and 37 remain discrepant. Study incomplete.
**Not a completed replication:** estimator discrepancies and the final independent-simulator audit remain unresolved.

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

## Recovered four-dimensional semi-automatic results

The [5,000-input semi-automatic 4D run](results/sabc4d-5000-recovered-2026-10-15/comparison.json) saved all five folds.
Independent analysis validates all 25,000 held-out predictions, coverage, and interval widths.
All five performance values match Table 8 at its printed three-decimal precision.
The process subsequently exited nonzero with `unexpected end of input`, following the previously documented live-script edit.
We retain that failure and all raw outputs; this is not recorded as a successful invocation.
A clean invocation parses the entire script before execution and is running separately.

## Full 5,000-input generalized additive model run

The [five-fold run](results/gam-5000-2026-10-15/comparison.json) completed successfully; independent analysis validates all 25,000 held-out parameter predictions.
All five performance values differ from Table 8 at its printed precision.
Reproduction-wealth performance is −0.632580 versus published −0.894.
The [error audit](results/gam-5000-2026-10-15/error-concentration.json) identifies concentrated extrapolation errors:
fold 1 test row 165 has truth 92 and prediction −1,775.021, accounting for 99.3262% of that fold's squared error.
Fold 4 test row 686 has truth 55 and prediction −2,586.658, accounting for 98.0261%.
No observations are removed. Historical-runtime sensitivity and exact author-environment alignment remain unresolved.
Raw fold objects, predictions, intervals, package versions, logs, and comparison metrics are retained.

The [input-source audit](results/gam-5000-2026-10-15/input-audit/source-mapping.csv) maps each fold's largest reproduction-wealth error back to the original archive.
All 151 parameter/predictor fields match exactly for each selected input.
The source rows are 675, 2856, 3852, 3388, and 2778 (zero-based).
The largest errors in folds 1 and 4 have eight and six predictors outside their training ranges respectively.
All five inputs belong to the completed 5,000-simulation replay, which matches every archived summary statistic.
This audit finds no copied-input discrepancy; it does not identify the cause of the published-score difference.

## Clean semi-automatic ABC 4D rerun

The [clean 5,000-row rerun](results/sabc4d-5000-clean-2026-10-15/comparison.json) exits successfully and independently validates all 25,000 held-out parameter predictions.
All five performance values match Table 8 at its printed three-decimal precision: 0.509, 0.449, 0.458, 0.476, and 0.624.
Metrics, prediction CSVs, and validated interval statistics are byte-identical to the earlier recovered outputs.
All five fold files, complete results, environment, warnings, and successful-run log are retained.
This resolves the earlier post-results script parse failure; it does not complete the remaining estimators or the full paper.

## Full regression-forest workflow launched

The original `randomForest_caretboot_fit` workflow is now running on all 5,000 inputs, five folds, and five parameters.
It preserves native caret tuning, ranger fitting, jackknife standard errors, and residual-simulation intervals.
The launch uses estimator seed zero, cross-validation seed zero, and the declared environment.
Source/data/runner hashes are retained in the external run's `launch-provenance.json`; fold and final output audits remain pending.
The smaller 1,250-input run and full neural-network run are still active.

## Small regression-forest results recovered

[All five 1,250-input folds](results/rfboot-1250-2026-10-16) independently validate 6,250 held-out parameter predictions, interval coverage, and interval widths.
Mutation-probability performance rounds to the published 0.503; the other four values differ at printed precision.
Coverage spans 0.9512–0.9640 across parameters. No observations or folds are dropped.
The original process handle is unavailable, so its exit code is not asserted; complete numerical outputs and the final log are retained.
The log ends with a deprecation warning and contains the final metrics.
Stochastic random-stream and runtime alignment remain unresolved; this does not establish a negative replication.

## GAM source-history audit

The author's `setup.R` changed between commits `8d53cca` and `0400f75`.
The older formula builder counted distinct values in response columns as well as predictors.
The newer builder excludes responses before constructing smooth terms for columns with fewer than ten distinct values.

[All ten saved training folds](results/gam-source-history-2026-10-16/provenance.json) have at least 75 distinct values in every response column.
Consequently, none enters the older low-cardinality list, and all 50 old/new formulas are identical.
The retained audit includes the exact source diff, source and fold hashes, formulas, and runtime.
A controlled two-value response column activates the changed branch and causes the auditor to reject formula equivalence before writing output.
This rules out this specific source revision as an explanation for the GAM discrepancy on these folds.
It does not resolve numerical runtime differences, rerun fitting, or establish author-environment equivalence.

```sh
Rscript replications/carrella_2021/audit_gam_history.R /complete/gam-1250 /complete/gam-5000 /new/history-audit
```

## Independent-model semantic boundary

[The integration audit](MODEL_SEMANTICS.md) identifies differences in scheduling, reproduction, mutation, trading, and Gini definitions between the author model and this fork.
A normal fork configuration cannot substitute for the author's asexual, two-resource model.
[Controlled complete native ticks](results/native-semantics-2026-10-16/proof.json) confirm that cached utility controls reproduction even after holdings change.
Identical current holdings yield one versus two agents when only cached utility differs.
Both cases preserve total holdings after metabolism and retain the previous mean price with zero trades.
The checks pass with trade enabled; the initial trade-disabled diagnostic produces identical output bytes.
These results specify behavior for an independent implementation; they do not complete that implementation or add a replicated paper.

## Independent study model implemented

`model.py` owns a separate Carrella model and scheduler inside this fork.
It implements the audited landscape, movement, metabolism, phased trading, asexual inheritance/mutation, cached utility, Gini, and price carry-forward behavior.
Python's random generator and activation draw order differ from NetLogo; matching seed labels does not promise identical stochastic trajectories.

[Complete-model checks](results/independent-model-2026-10-16/comparison.json) match all 5,000 native resource capacities and three controlled whole-tick scenarios.
The equal-ratio trade scenario confirms that retained potential holdings can be reused; this constructed case does not measure its frequency in original runs.
A deliberately changed model that refreshes utility before reproduction fails the native comparison.
Two bounded 501-observation CLI runs complete with byte-identical trajectories and pass finite-value, population, Gini, and extinction-timestamp checks.
These checks establish initial implementation coverage, not full model equivalence or completed paper replication.
Independent ensemble comparison, mutation boundaries, and broader native trade scenarios remain required.

```sh
python replications/carrella_2021/model.py /parameters.json /new/trajectory.csv
python replications/carrella_2021/verify_model.py /complete/native-semantics /new/model-comparison
```

The parameter JSON uses `population`, `mutation`, `maximum_sugar`, `maximum_spice`, `reproduction`, and integer `seed`.
Both minimum endowments are five, matching the original experiment.
The CLI records before each of 501 native-style steps and preserves repeated terminal states after extinction.

## Trade and mutation boundary coverage

[Four additional native trade ticks](results/trade-mutation-2026-10-16/comparison.json) match individual holdings, utilities, trade counts, and mean prices.
They cover prices above and below one, reciprocal commodity quantities, symmetric trade, and rejection against cached utility.
Resource totals are conserved in these ordinary unequal-ratio cases after metabolism.

Two 16-seed mutation campaigns run complete reproductive ticks in each implementation: 32 native and 32 independent ticks.
Checks verify inherited halves, updated child utility, empty-cell placement within radius three, and allowed trait outcomes.
Both exhibit metabolism values above four and negative vision values; the native model lacks those opposite bounds.
Matching observed support does not imply matching frequencies or random draws.
Controlled reciprocal-price and vision-clamping mutations both cause the verifier to fail before reporting success.
The independent simulator passes these checks without modification.
Independent ensemble comparison and broader multi-step native comparisons remain outstanding.

```sh
python replications/carrella_2021/verify_extensions.py /native/trades.csv /native/mutations.csv /new/comparison
```

## Full independent ensemble launched

The [declared independent ensemble](INDEPENDENT_ENSEMBLE.md) covers all 5,000 original parameter rows and 501 observations per row.
`run_independent.py` records all 150 author-defined summary statistics, native-style observation timing, original seed text, and the independent integer seed.
Raw and losslessly compressed trajectories, source/data hashes, validation results, and per-row completions are preserved.
The [frozen launch](results/independent-launch-2026-10-16/launch.json) uses one worker and the complete original input interval.
The run is incomplete and does not establish model or estimator equivalence.
Python/NetLogo random streams differ, so exact archived-trajectory agreement is not an acceptance criterion for this independent ensemble.

```sh
python replications/carrella_2021/run_independent.py /params_sugarscape.csv /sugarscape.csv 0 5000 /new/independent-run
```

The first four completed independent inputs pass a separate standard-library audit of all 600 saved statistics.
Maximum absolute recomputation difference is 1.14e-13; input mapping, trajectory hashes, and observation timing also pass.
Complete mode rejects the unfinished ensemble, and a deliberately changed saved statistic is rejected before report creation.
The prefix trajectories and audit are retained with the launch evidence.
`audit_independent.py PARAMETERS RUN prefix|complete NEW_OUTPUT` performs this validation without assuming agreement with native random trajectories.

## Complete multi-step native comparisons

[Five deterministic 501-observation trajectories](results/multistep-native-2026-10-16/comparison.json) match 25,050 native values within 1e-13 relative/absolute tolerance.
They cover resource regrowth, harvest/metabolism order, starvation from one or both resources, zero/negative/positive vision, and frozen extinction state.
The two starvation cases stop advancing at ticks seven and ten; remaining observation rows repeat the terminal state.
The independent model required no change. A deliberately incorrect post-extinction tick increment fails at the first affected observation.
Lossless native trajectories, source hashes, native exit status, and comparison/control results are retained.
These deterministic checks strengthen model validation but do not establish stochastic ensemble agreement.

```sh
python replications/carrella_2021/verify_trajectories.py /native/trajectory-probes /new/comparison
```

### Independent/native prefix comparison

`compare_independent.py PARAMETERS REFERENCE RUN prefix|complete OUTPUT` first audits every completed independent trajectory and recomputes all 150 statistics.
It verifies the original reference hash, pairs identical parameter rows, and reports means, differences, root mean squared differences, and native standard deviations.
Different random generators preclude exact trajectory matching. These descriptive measurements impose no equivalence threshold or significance verdict.

[The first 43 inputs](results/independent-comparison-2026-10-16) pass 6,450 independently recomputed statistics, with maximum absolute error 1.14e-13.
Neither implementation becomes extinct on these inputs.
The largest absolute mean difference divided by native standard deviation is 0.596, for mean trade price at observation 450.
Its native and independent means are 1.03867 and 1.01747 respectively.
This is an exploratory maximum over 150 statistics from an incomplete parameter ensemble, not evidence of equivalence or a diagnosed implementation error.
All 43 compressed trajectories, the audit, paired statistics, and a rejected-reference corruption control are retained.
The full 5,000-input run remains in progress; this prefix does not complete the paper replication.

### Expanded independent/native comparison and price trace

[The 238-input prefix](results/independent-expanded-comparison-2026-10-16/comparison.json) passes 35,700 independently recomputed statistics with maximum absolute error 1.14e-13.
Neither implementation becomes extinct on these inputs. All 238 compressed independent trajectories and the audited ledger are retained.
The largest absolute mean difference divided by native standard deviation is 0.2126, for mean trade price at observation 50.
Native and independent prefix means are 1.08927 and 1.16672.
These are descriptive statistics over a growing prefix, without a significance or equivalence verdict.

Input 83 contributes the largest individual difference for that statistic: native 0.63169 versus independent 7.64115.
`trace_prices.py ENSEMBLE ROW NEW_OUTPUT` replays the frozen model parameters, verifies all 501 observations exactly, and exposes raw transaction prices without changing the simulation.
[Its input-83 audit](results/independent-expanded-comparison-2026-10-16/price-trace-83/audit.json) matches all 3,507 values.
At tick 49, two transactions have prices 8.95408 and 6.32822; their arithmetic mean is 7.64115.
Tick 50 has no transactions, so the model carries that mean forward, consistent with the author's reporter semantics.
This explains the observed summary value, not the independent/native stochastic difference.
The input remains included. The full 5,000-input ensemble and independent estimator comparison remain outstanding.

## Partitioned independent-ensemble continuation

The original independent worker was deliberately stopped after 507 completed inputs.
[Its terminal-prefix audit](results/independent-partition-2026-10-16/checkpoint-audit/analysis.json) recomputes all 76,050 statistics with maximum absolute error 1.14e-13.
The detached original launcher did not capture an exit code; the termination request and subsequent PID absence are recorded explicitly.
Original files, including the interrupted next trajectory, remain intact. Only committed completion-ledger rows count.

Before partitioning, input 500 was replayed through the frozen runner in a fresh process.
Its complete trajectory is byte-identical, all 150 saved statistics match, and completion fields agree except elapsed time.
This repeated validation input adds zero ensemble coverage.
Each input constructs its own seeded Python random generator, so worker scheduling does not share or reorder random streams between inputs.

Three workers resume disjoint intervals `[507,2005)`, `[2005,3503)`, and `[3503,5000)`.
Together with the preserved prefix, these cover all original 5,000 inputs without gaps or overlaps.
The frozen model, Python/runtime versions, input hashes, seed conversion, observation timing, and statistics remain unchanged.
This uses local capacity released when the five reference JVM workers moved to remote CPU capacity.
The original per-row free-space guard remains active.

[Initial resumed-prefix audits](results/independent-partition-2026-10-16/coverage.json) validate 11 additional inputs.
Total unique audited coverage is **518 inputs and 77,700 recomputed statistics**.
Inputs 0–237 retain their earlier trajectory artifacts; the new directory retains the added checkpoint trajectories, manifests, ledgers, summaries, proof, and resumed-prefix evidence.
All three workers continue. The full ensemble, independent/native distribution comparison, and remaining estimator replications are still incomplete.

## Reconcile independent partitions before calibration

`reconcile_independent.py PARAMETERS REFERENCE prefix|complete NEW_OUTPUT RUN...` audits each supplied run before combining its completed inputs.
It checks the pinned author data, frozen model/runner/protocol hashes, and consistent producer runtime versions.
Original row indices determine output order; overlapping runs are rejected, including otherwise-valid repeated validation inputs.

`audit_independent.py` now retains and hashes the exact summary snapshot it checked.
Both reconciliation and the existing single-run comparison consume that snapshot, preventing a later read of an advancing live summary file.
Each reconciled table retains its original-row index and input audit provenance.
Prefix mode writes `partial_summary_statistics.csv` and explicit missing intervals.
Complete mode requires every original index `[0,5000)` before writing `summary_statistics.csv` for calibration.
It never silently fills missing rows or deduplicates overlapping simulations.

```sh
python replications/carrella_2021/reconcile_independent.py \
  /params_sugarscape.csv /sugarscape.csv prefix /new/reconciliation \
  /preserved-original-run /independent-shard-1 /independent-shard-2 /independent-shard-3
```

[Real workflow validation](results/independent-reconciliation-2026-10-16/validation.json) audits 561 inputs and 84,150 statistics, with independently verified table ordering.
A complete-mode request against the unfinished original run fails without writing a calibration table.
Combining that run with the separate input-500 validation replay also fails before writing either table.
The existing comparison succeeds on a 24-input shard snapshot and consumes exactly the audited bytes.
A first comparison attempt with only one input was rejected by its existing minimum-size requirement; that failure remains preserved externally.

Compressed workflow snapshots, source manifests, rejection evidence, and a repository-relative index of the required trajectories are retained.
The successful complete-export path awaits the actual 5,000-input ensemble; no full-ensemble, estimator-equivalence, or paper-replication claim follows from these checks.

### Separate independent estimator inputs

After complete reconciliation, prepare a new estimator input directory:

```sh
python3 replications/carrella_2021/prepare_independent_estimator.py \
  /absolute/author-checkout /absolute/complete-reconciliation /absolute/new/independent-inputs
Rscript replications/carrella_2021/run_estimator.R \
  /absolute/new/independent-inputs lm 1250 0 /absolute/new/independent-lm-results
```

The preparer checks complete original-row coverage, summary hashes, finite statistics, and pinned simulation sources.
It copies the hash-pinned author `setup.R` and parameter table, alongside the independent statistics, into a new directory.
A provenance manifest distinguishes these inputs from the archived native table; the author checkout remains unchanged.

[The actual 561-input partial ensemble is rejected](results/independent-estimator-inputs-2026-10-16/validation.json) before any output directory is created.
**The successful preparation and independent estimator paths remain unverified until the real 5,000-input ensemble completes.**
No partial ensemble or copied native table substitutes for that completion requirement.

## Disk-guard checkpoint and cloud handoff

The three independent shards exited when local free space fell below their existing 2 GiB guard.
[Reconciliation](results/disk-stop-reconciliation-2026-10-16/provenance.json) validates 893 unique inputs and independently recomputes 133,950 summary values.
Completed intervals are `[0,631)`, `[2005,2139)`, and `[3503,3631)`; prior published prefixes are included, not added again.
The remaining 4,107 inputs occupy `[631,2005)`, `[2139,3503)`, and `[3631,5000)`.
Original trajectory files and producer logs remain in the retained evidence paths recorded by the audit.

A task-owned CPU node is queued for a Linux portability check using Python 3.11.14, NumPy 1.26.4, and Pydantic 2.12.3.
Eight previously completed inputs will be compared before any remaining production range launches.
No Linux portability result, production launch, or complete independent ensemble is claimed by this checkpoint.

## Linux portability diagnostic

[Eight pinned-runtime replays](results/linux-portability-2026-10-16/provenance.json) completed on Linux with the unchanged independent model.
The strict comparison fails on input zero; its failure and original comparator remain retained.
Across 4,008 observations, 16 Gini values differ by at most `1.1102230246251565e-16`.
All other recorded trajectory values match exactly, including populations, patch resources, trade counts, and mean prices.
Of 1,200 summary values, 1,157 match exactly; the maximum difference is `4.884981308350689e-15`.
The summary comparison exposes differences without applying a new acceptance tolerance.

The model computes utility with fractional powers before calculating wealth inequality, and NumPy computes fitted trend summaries.
These are candidate numerical paths, not an established explanation for the observed differences.
The saved observations do not expose every agent state, so they cannot prove identical hidden-state evolution.
No remaining production interval has launched; platform attribution and acceptance remain pending.

### State trace and bounded continuation

[Passive input-zero traces](results/linux-state-trace-2026-10-16) reproduce all 501 original observations independently on each platform.
All model fields, including random state and agent iteration order, match across platforms at every observation except cached utility-derived wealth.
There are 1,242 differing cached wealth values, with maximum absolute difference `7.105427357601002e-15`.
A scalar fractional-power probe reproduces one discrepancy: `15.145571514632067 ** 0.5` differs by one floating-point step between the tested runtimes.
The trace exposes no change to decisions or non-wealth state for this input; it does not prove universal platform equivalence.
Full traces remain at the retained evidence paths; their hashes, state digests, differences, observer, and unchanged-observation validation are included here.

The remaining 4,107 inputs now run on eight Linux workers in disjoint chunks of at most 25 inputs.
The six-hour wrapper archives outputs and stops its node, bounding this batch to about $2.89 at the observed $0.4824 hourly rate, excluding setup.
Runtime and platform provenance accompany the unchanged frozen producer.
Existing independent statistic-recomputation tolerances (`1e-10` absolute and relative) remain unchanged; the strict cross-platform failure remains failed.
All completed chunks still require independent trajectory and statistic audits before reconciliation and estimator analysis.

## Independently validated cloud checkpoint

[The first sealed cloud checkpoint](results/cloud-checkpoint-2026-10-16/validation.json) contains 50 completed 25-input chunks, adding 1,250 inputs.
Reconciliation with the four retained local runs validates 2,143 unique inputs and recomputes all 321,450 summary values.
It checks original input mappings, runtime/source hashes, 501-observation trajectories, compressed and raw file hashes, and duplicate-free original-row ordering.
Every captured cloud chunk has a successful exit and a matching complete-interval marker.
Controller source, interval plan, and Linux platform provenance are retained with the native evidence.

Completed ranges are `[0,1881)`, `[2005,2139)`, and `[3503,3631)`.
Missing ranges are `[1881,2005)`, `[2139,3503)`, and `[3631,5000)`.
The cloud producer remains active; these counts exclude in-progress and later-completed chunks.
The retained prior local count of 893 is included, not added again to 2,143.
The full 5,000-input gate still fails, so no complete independent calibration table or estimator result is claimed.

## Second independent cloud checkpoint

The [second checkpoint](results/cloud-checkpoint-002-2026-10-16/summary.json) adds90 sealed cloud chunks containing2,238 independent inputs.
Reconciliation combines these with the previous2,143 inputs exactly once, yielding4,381 unique original parameter rows and657,150 recomputed statistics.
Source, runtime, input hashes, trajectory checksums, and original row order pass the existing audit.
Maximum absolute statistic recomputation error is 2.2737367544323206e-13, within the unchanged audit tolerance.
Coverage is contiguous from original row0 through4380; rows4381–4999 remain reserved to the active cloud producer.
The new native archive excludes the earlier50 cloud chunks; the reconciliation retains provenance for both checkpoints and local runs.
The complete5,000-input gate remains unmet, so no independent estimator or scientific equivalence verdict is reported.

## Full independent distribution comparison

`compare_independent_ensemble.py AUTHOR_SOURCE COMPLETE_RECONCILIATION NEW_OUTPUT` implements the planned descriptive comparison of all150 statistics.
It requires all5,000 audited inputs, original row order, frozen model hashes, and matching source-table checksums before creating output.
It reports means, population standard deviations, quantiles, and empirical Wasserstein distances overall and within ten parameter bins for each of five parameters.
Bins use equal widths over original input ranges; other parameters are not held fixed.
Equal seed labels do not imply matched random streams, and no acceptance margin or replication verdict is inferred from these differences.

The [actual4,381-input gate check](results/distribution-analysis-gate-2026-10-16/partial-gate.json) rejects incomplete evidence before creating output.
Formatting and lint checks pass; the complete-data calculation path has not yet run.
The cloud producer subsequently exited successfully after all4,107 reserved inputs reported completion.
Its final619 inputs await download and independent audit; execution completion alone does not satisfy the full-ensemble evidence requirement.

## Table 8 result coverage

The [cell inventory](results/table8-coverage-2026-10-16/coverage.json) reconciles every printed Table8 value with the retained original-data estimator evidence.
Of90 cells,15 are explicitlyNA,65 have computed results, and10 await the active5,000-input neural-network and regression-random-forest runs.
At1,250 inputs, local-linear, neural-network, and four-dimensional semi-automatic methods areNA; their author notebook chunks also disable evaluation.
They are not missing reported numerical targets, and no replacement run was launched for them.
Of65 computed values,33 match the paper’s printed three-decimal precision.
This inventory includes previously documented single-cell matches and supersedes lower summary counts; it creates no new estimator result.
The32 numerical differences still require interpretation, and printed agreement alone does not complete independent-model or whole-paper replication.
Each cell links and hashes its retained comparison artifact.

## Sequential notebook random-stream diagnostic

A [bounded fresh notebook execution](results/notebook-rf-sequence-launch-2026-10-16/manifest.json) now runs the original setup, data preparation, rejection, semi-automatic4D, linear regression, and quantile-random-forest chunks in order.
The original chunk bodies remain unchanged; checkpoints retain all global objects and random state after each chunk.
This follows the notebook’s estimator ordering instead of resetting the seed for every method.
Current packages and explicit Rejection sampling remain declared runtime choices; this is not a historical-runtime reconstruction.
The two-hour diagnostic reached and audited the linear-regression checkpoint, then timed out during the forest stage.
Its terminal traceback is retained; no forest result was produced by that attempt.
A [bounded checkpoint continuation](results/notebook-rf-checkpoint-resume-2026-10-17/manifest.json) restores all 37 saved global objects and all 626 random-state integers exactly.
The unchanged original forest chunk runs with a six-hour limit after both prior processes were confirmed absent.
The continuation completed successfully; its full checkpoint and independent prediction audit are retained below.
The separate regression-forest and neural-network estimators remain intact.

The [actual notebook data checkpoint](results/notebook-rf-sequence-launch-2026-10-16/dataprep-audit.json) passes independent base-R parsing and first-fold alignment checks.
All755,000 numeric cells agree within1e-10; maximum parser difference is1.3877787807814457e-17.
The original five-parameter order and146 nonconstant statistics are retained, excluding the same four constant columns.
The first held-out fold matches the earlier isolated random-forest run within that tolerance.
Because the original notebook uses a different CSV parser, any later forest changes cannot be attributed solely to random-stream order without a parser control.
The full estimator sequence remains running; no additional Table8 match is claimed.

The [completed rejection checkpoint audit](results/notebook-rf-sequence-launch-2026-10-16/rejection-audit.json) reconstructs all five held-out folds and independently recomputes error, coverage, interval width, and baseline-normalized performance.
All 25,000 predictions are checked against the earlier isolated run; the maximum difference is 1.39e-17.
All five printed Table 8 scores agree, as they already did in the isolated execution; this adds no target count.
The checkpoint random state equals the data-preparation random state exactly.
The separate setup audit also confirms that setup and data preparation retain the state from `set.seed(0)`.
Thus this rejection stage did not advance the random stream in the observed execution; later notebook stages remain pending.
The actual rejection checkpoint, audit script, source hashes, and arithmetic report are retained alongside the launch evidence.

The [completed semi-automatic checkpoint audit](results/notebook-rf-sequence-launch-2026-10-16/sabc-audit.json) independently recomputes all five folds and checks 25,000 predictions.
All five scores still match Table 8 at printed precision; these targets were already matched by the isolated execution.
The largest prediction difference from the isolated run is 0.5, and the saved random state differs from the preceding rejection checkpoint.
This establishes that the observed semi-automatic stage advances the random stream; it does not isolate the cause of prediction differences.
Parser differences and execution order remain separate factors for the pending random-forest comparison.
The actual checkpoint, audit script, hashes, and arithmetic report are retained; no new replication target or whole-study completion is claimed.

The [completed linear-regression checkpoint audit](results/notebook-rf-sequence-launch-2026-10-16/lm-audit.json) reconstructs all five folds and independently checks 25,000 predictions, interval coverage, interval width, and normalized errors.
All five printed scores agree, as in the isolated point-estimate calculation; no new target is counted.
The largest prediction difference from that calculation is 3.64e-11.
The saved random state differs from the preceding semi-automatic checkpoint, confirming another state advance before the forest stage.
The actual checkpoint and source hashes are retained. The random-forest continuation is now audited below.

## Regression-forest first-fold checkpoint

The [first completed 5,000-input regression-forest fold](results/rfboot-5000-first-fold-2026-10-17/audit.json) passes independent validation.
Reconstructing the original seed-zero partition matches all 755,000 training/test input cells exactly, after normalizing row labels reset by the author’s filtering.
All 5,000 held-out parameter predictions reproduce the saved root-mean-square errors, interval coverage, and interval widths within 1e-10.
The actual fold, predictions, audit script, package versions, and hashes are retained.
Four folds remained at this checkpoint. The second-fold update below supersedes that count; no aggregate Table 8 score is claimed.

## Completed sequential quantile-random-forest diagnostic

The [original notebook continuation](results/notebook-rf-completed-2026-10-17/audit.json) exited successfully after 1,937.6 seconds. Its complete 7.5 MB checkpoint preserves predictions, preceding notebook objects, and the final random state. The audit reconstructs all five held-out folds and independently verifies all 25,000 predictions, root-mean-square errors, interval coverage, interval widths, and baseline-normalized performance.

| Parameter | Sequential notebook | Earlier isolated run | Published Table 8 |
|---|---:|---:|---:|
| Initial population | 0.476062 | 0.475749 | 0.475 |
| Mutation probability | 0.535328 | 0.537491 | 0.536 |
| Maximum sugar endowment | 0.445939 | 0.446204 | 0.446 |
| Maximum spice endowment | 0.462287 | 0.462307 | 0.463 |
| Reproduction wealth | 0.788391 | 0.787706 | 0.790 |

Only maximum sugar endowment matches the paper’s printed three-decimal precision in either run. The sequential workflow therefore does not resolve the four existing differences or add any newly covered Table 8 cell. Individual predictions differ by up to 36.5 from the isolated run. The random state advanced during the forest stage.

This comparison varies both CSV parsing and the preceding random stream. A new bounded control restores the exact sequential pre-forest random state but replaces only `total_data` with base-R parsed inputs. Before fitting, it verifies exact equality with every saved isolated training/test fold. The original forest chunk and six-hour cap remain unchanged. This isolates parser effects against the completed sequential run; no negative-replication claim is assigned while the discrepancy remains unresolved.

The parser control’s [setup receipt](results/notebook-rf-parser-control-launch-2026-10-17/restoration.json) confirms all five folds exactly match the isolated inputs and the sequential random state is restored. The only numerical input difference from the notebook parse is at most 1.3878e-17 over 755,000 cells. The completed fit is audited below; source and preconditions are retained.

The portable audit reconstructs the same arithmetic and 25,000-row prediction CSV. Its scope text now covers either parser:

```sh
Rscript replications/carrella_2021/audit_notebook_rf.R \
  replications/carrella_2021/results/notebook-rf-completed-2026-10-17/rf.rds \
  /path/to/sequential-lm-checkpoint.rds \
  replications/carrella_2021/results/rf-5000-2026-10-15 \
  /new/audit-output
```

The linear checkpoint is the preserved predecessor named and hashed in the continuation manifest. No estimator is refitted by this audit.

## Completed controlled parser comparison

The [parser-control audit](results/notebook-rf-parser-control-completed-2026-10-17/audit.json) validates all 25,000 predictions after a successful 1,777.9-second fit.
It uses the sequential pre-forest random state and the isolated run’s exact parsed inputs.

| Parameter | Parser control | Published Table 8 |
|---|---:|---:|
| Initial population | 0.475589 | 0.475 |
| Mutation probability | 0.534246 | 0.536 |
| Maximum sugar endowment | 0.446266 | 0.446 |
| Maximum spice endowment | 0.463117 | 0.463 |
| Reproduction wealth | 0.788780 | 0.790 |

The [controlled comparison](results/notebook-rf-parser-control-completed-2026-10-17/parser-comparison.json) finds changes in 16 input columns, each no larger than 1.39e-17.
These changes produce individual population predictions differing by up to 36 and different final random states.
The two fits began with the same random state, source, runtime, and fold partition.
Thus tiny parsing changes affect this forest execution; input agreement within 1e-10 does not establish identical fitting behavior.
Two control scores match printed precision, versus one sequential score. This diagnostic does not replace the declared primary protocol or increase replicated-target counts.
The paper remains incomplete, with no negative verdict assigned from these differences.

## Neural-network first-fold checkpoint

[The first completed neural-network fold](results/neuralnet-5000-first-fold-2026-10-17/audit.json) passes independent validation of all 755,000 training/test input cells and 5,000 parameter predictions.
The audit reconstructs the seed-zero partition: 4,000 training rows and 1,000 held-out rows.
Root-mean-square errors, interval coverage, and interval widths agree with the checkpoint within 1e-10.

The native ABC-neural-network result stores posterior medians under `medians`; the earlier forest audit expected `predictions`.
The failed audit attempt is retained, and the corrected audit reads the native field without refitting or changing the simulation.
The actual checkpoint, exported predictions, package versions, and hashes are included.
Four folds remained at this checkpoint. The second-fold update below supersedes that count; no aggregate Table 8 score is claimed.

## Second-fold checkpoints

The neural-network and regression-forest estimators have each completed two of five folds.
Their second folds pass independent reconstruction of the original seed-zero partition:
4,000 training rows, 1,000 held-out rows, and all 755,000 input cells match exactly.
Each audit checks 5,000 predictions and recomputes errors, coverage and interval widths
within 1e-10 of the native checkpoint.

[Neural-network fold two](results/neuralnet-5000-second-fold-2026-10-17/audit.json)
has parameter errors 46.85941829, 0.02945162, 10.30926337, 10.56059195 and 6.18819910.
[Regression-forest fold two](results/rfboot-5000-second-fold-2026-10-17/audit.json)
has errors 59.95620953, 0.02618469, 11.43422205, 11.23398809 and 5.00277238.
Parameter order is initial population, mutation probability, maximum sugar endowment,
maximum spice endowment and reproduction wealth. These are root-mean-square errors,
not the paper's aggregate cross-validation scores.

Both checkpoints, prediction exports, runtime metadata and hashes are retained.
At this checkpoint, three folds remained for each estimator. The third-fold update
below supersedes the forest count; no aggregate Table 8 score is claimed.


## Third regression-forest fold

[The third native forest checkpoint](results/rfboot-5000-third-fold-2026-10-17/audit.json)
passes independent reconstruction of the original seed-zero held-out rows 2001–3000.
All 755,000 input cells match, and all 5,000 predictions are finite. Recomputed errors,
interval coverage, and interval widths agree with the checkpoint within 1e-10.
Parameter errors are 60.71296364, 0.02664347, 12.00947956, 11.65893629, and 4.66388069,
in the parameter order above. The native checkpoint, prediction export, hashes, and
runtime metadata are retained. At that checkpoint, forest completion was 3/5 folds
and neural-network completion was 2/5. The neural-network update below supersedes that count.

## Neural-network third fold

[The third native neural-network checkpoint](results/neuralnet-5000-third-fold-2026-10-17/audit.json)
passes the original seed-zero partition check: 4,000 training rows and 1,000 held-out
rows, covering 755,000 input values. All 5,000 predictions are finite; independently
recomputed error, coverage, and interval width agree with saved metrics within 1e-10.

Root mean square errors are 49.608317 for initial population, 0.028831 for mutation
probability, 10.506691 for sugar endowment, 10.347184 for spice endowment, and
5.917523 for reproduction wealth. These are fold measurements, not aggregate Table 8 scores.

Both expensive estimators have completed three of five folds. Their original processes
remain active. The native checkpoint, compressed predictions, hashes, runtime metadata,
and auditor are retained; no additional study completion is claimed.

## Completed remaining 5,000-input estimators

The [neural-network workflow](results/neuralnet-5000-complete-2026-10-17) and
[regression-forest workflow](results/rfboot-5000-complete-2026-10-17) both exited
successfully with all five folds. Independent audits reconstructed all original
fold memberships and checked 7,550,000 training/test cells and 50,000 predictions
across the two methods. Errors, baseline errors, coverage, widths, and aggregate
scores match the retained native outputs within 1e-10.

| Parameter | Neural network | Paper | Regression forest | Paper |
| --- | ---: | ---: | ---: | ---: |
| Initial population | 0.587812 | 0.588 | 0.472824 | 0.474 |
| Mutation probability | 0.502640 | 0.502 | 0.538378 | 0.538 |
| Maximum sugar endowment | 0.508427 | 0.510 | 0.448165 | 0.448 |
| Maximum spice endowment | 0.519019 | 0.519 | 0.464153 | 0.465 |
| Reproduction wealth | 0.742542 | 0.736 | 0.796842 | 0.797 |

Two neural-network and three regression-forest cells match printed precision.
The [updated Table 8 inventory](results/table8-coverage-2026-10-17/coverage.json)
now covers all 75 reported values: 38 match and 37 differ. The remaining 15 table
cells are published as NA. These differences need attribution before negative
replication verdicts; completing the estimator runs does not complete the paper.

## Controlled GAM input-parser experiment

[The frozen control](results/gam-parser-control-launch-2026-10-17) repeats the complete
1,250-input GAM workflow with the notebook's `readr::read_csv` parser. Only the two
input reads differ from the original isolated-seed runner. All five folds, five targets,
interval draws, seed zero, observations, and fitting options remain unchanged.
Execution was bounded to 1,800 seconds and completed in 1,624.35 seconds. Full results follow below.

The pre-fit audit verifies identical random states: all 626 integers agree. Parsing
changes 2,620 of the 188,750 data cells by at most 1.3878e-17. The control uses the
same mgcv 1.9-4, Matrix 1.7-5, dplyr 1.2.1, and readr 2.2.0 versions as the primary run.
This isolates parser sensitivity under the current runtime; it does not reconstruct
the authors' unknown historical environment or the notebook's preceding random stream.
The primary results remain unchanged, and no additional Table 8 match is claimed.

## GAM parser control: first two completed folds

[The saved-fold audit](results/gam-parser-control-prefix-2026-10-17/prefix-audit.json)
reconstructs both held-out partitions, verifies 377,500 input cells exactly against
notebook-parsed inputs, and checks 2,500 predictions and their interval metrics.
Both complete native fold checkpoints are retained.

The maximum prediction change is 31.9513 in fold one and 1,206.9118 in fold two.
The known reproduction-wealth outlier at original input 675 changes from −6,945.8109
to −8,152.7227; its true value is 92. Thus the notebook parser does not resolve
this outlier. Small input differences can materially affect this fitted GAM.

The pre-fit random states and relevant package versions match, as recorded in the
launch evidence. Maximum input change remains 1.3878e-17. At this checkpoint, three folds remained;
these checkpoint results alone do not supply an aggregate Table 8 comparison or negative
replication verdict. No observation or difficult fold is excluded.

To verify the retained checkpoints, pass the pinned source directory, this result
directory, the original `gam-1250-2026-10-15` directory, and a new JSON path to
`audit_parser_prefix.R`. Readback from the published copies reproduces the audit exactly.

## Complete GAM parser control

[All five folds](results/gam-parser-control-complete-2026-10-17/parser-comparison.json)
pass the independent saved-output audit: 6,250 predictions and 943,750 input cells.
The audit reconstructs train/test membership and recomputes errors, baseline errors,
interval coverage, interval widths, and aggregate scores. Relevant package versions match.

| Parameter | Primary score | Notebook-parser control |
| --- | ---: | ---: |
| Initial population | 0.499665 | 0.534255 |
| Mutation probability | 0.436194 | 0.234060 |
| Maximum sugar endowment | 0.347444 | 0.337638 |
| Maximum spice endowment | 0.164329 | 0.340425 |
| Reproduction wealth | -3.002351 | -3.678426 |

The maximum input change is 1.3878e-17; the maximum prediction change is 1,206.9118.
Parsing affects the fit materially but does not resolve the reproduction-wealth outlier.
This controlled sensitivity does not recover the authors' historical environment or
preceding notebook random stream. Primary Table 8 results and completion status remain unchanged.

The result directory retains all five fold checkpoints, complete predictions, runtime
metadata, source pins, terminal receipt, auditor, and SHA-256 inventory. Running its
`audit_parser_inputs.R` with the pinned source directory, result directory, primary
`gam-1250-2026-10-15` directory, and a new JSON path reproduces the comparison exactly.

## GAM outlier term decomposition

[The point-fit diagnostic](results/gam-term-decomposition-2026-10-17) refits only
fold two's reproduction-wealth response with unchanged inputs, formula, and fitting options.
Both parser variants reproduce all 250 retained point predictions exactly.
Summing their 146 smooth terms and fitted intercept reconstructs predictions within 3.13e-13.

| Quantity at held-out row 131 | Primary | Notebook parser |
| --- | ---: | ---: |
| True reproduction wealth | 92 | 92 |
| Predicted reproduction wealth | -6,945.811 | -8,152.723 |
| Contribution from `snap.450.mean.prices` | -7,104.840 | -8,334.386 |

That price input is 17.7618, beyond its training range of 0.3101–1.3947.
Its term supplies the largest absolute contribution under both parsers. The remaining
terms and intercept offset part of its negative contribution. This identifies the
dominant extrapolating term; it does not establish why the published table differs.

`diagnose_gam_terms.R FOLD_RDS REFERENCE_FIT_RDS VARIANT OUTPUT` reproduces this
diagnostic. The reference formula comes from the earlier fold-two current-runtime
`wealth.reproduction.rds`. Native models remain in the retained paths recorded by
`provenance.json`; compact predictions, contributions, and audit reports are published.

Both R fits completed and passed their checks. The enclosing wrapper then failed
its 100 MiB aggregate storage guard: retained evidence totals 118,476,107 bytes.
That operational failure remains recorded separately from the successful numerical checks.
An earlier diagnostic incorrectly expected an intercept attribute from `predict.bam`;
the corrected diagnostic uses the fitted intercept coefficient. No observations were excluded.

### Complete independent ensemble recovered and audited

[The final evidence](results/independent-ensemble-complete-2026-10-18) recovers
all 619 remaining inputs across 25 successfully completed native chunks.
Complete reconciliation re-audits all 5,000 original parameter rows and
recomputes all 750,000 statistics from retained trajectories. No indices are
missing or duplicated. The complete table has SHA-256
`ca4125920859ddbfb528ef9d7ae7ec8c635804a8eaba45069fa8578e37cb2f9f`.

The full-data paths now pass for reconciliation, independent estimator-input
preparation and distribution comparison. The published audit archive extracts
byte-for-byte to the verified records. Earlier incomplete-data rejection
evidence remains retained. Original author parameters and estimator source
are unchanged; only the simulation-statistics table is independent.

All 150 statistics are compared globally and across ten bins of each of five
parameters, producing 7,650 descriptive comparison rows. For example, average
population is 452.096687 in the author table and 451.959111 independently.
These values do not establish equivalence: the random streams differ, and no
post-hoc tolerance or paired-randomness assumption is introduced.

The independent five-fold linear-regression workflows for 1,250 and 5,000
inputs are launched in sequence with the original estimator and interval
procedures. Their results require separate held-out prediction audits. An
initial invocation failed before fitting because it omitted the installed R
library path; that attempt is retained, and the corrected invocation uses
the existing library without changing statistical source.

Full independent estimator comparisons and interpretation of the published
Table 8 discrepancies remain required. This does not complete the paper.

### Independent 1,250-input linear regression audited

[The completed five-fold workflow](results/independent-lm1250-2026-10-18)
validates all 6,250 held-out parameter predictions, intervals and aggregate
metrics. `audit_independent_folds.R INPUTS RUN NEW_OUTPUT` additionally verifies
the hash-pinned independent input table, all 943,750 training/testing cells,
original fold allocation and baseline errors. Public-archive extraction
reproduces both audits byte-for-byte.

| Parameter | Author-data performance | Independent-data performance |
| --- | ---: | ---: |
| Initial population | 0.513273 | 0.578945 |
| Mutation probability | -0.130966 | 0.412859 |
| Maximum sugar endowment | 0.399341 | 0.519539 |
| Maximum spice endowment | 0.386771 | 0.529832 |
| Reproduction wealth | 0.394302 | 0.763990 |

Performance is one minus mean fold error divided by mean fold baseline error.
Baseline errors agree because parameters and fold allocation are identical.
Simulation statistics differ, including their random streams; these differences
require interpretation rather than an automatic negative verdict.

The native run reports 26 R warnings whose individual messages were not
retained by the original runner. Finite-value, interval and prediction audits
pass, but the warning count remains disclosed. The initial missing-library
failure is also retained. The 5,000-input workflow is still running.
No estimator or paper scope has been reduced.

### First-fold warning control reproduces the complete result

[An unchanged first-fold replay](results/independent-lm-warning-control-2026-10-18)
uses immediate warning reporting and all 200 bootstrap fits for each of five
parameters. Its complete result and final random state are identical to the
saved native fold, including predictions, interval bounds and metrics.

The replay emits five legacy `unnest()` interface warnings and one deprecated
`as_data_frame()` warning. No numerical warning appears in this replay.
This identifies the first-fold warnings without changing the author estimator.
It does not recover individual messages from the other four original folds
or resolve independent-versus-author simulation differences.

### Independent 5,000-input linear regression audited

[The full-size workflow](results/independent-lm5000-2026-10-18) completes all
five folds and validates 25,000 held-out parameter predictions, intervals and
metrics. Its provenance audit checks 3,775,000 training/testing cells and
recomputes baseline errors against the independent input table. Both audits
reproduce byte-for-byte from the public native archive.

| Parameter | Author-data performance | Independent-data performance |
| --- | ---: | ---: |
| Initial population | 0.605727 | 0.608121 |
| Mutation probability | 0.278754 | 0.361315 |
| Maximum sugar endowment | 0.539300 | 0.554948 |
| Maximum spice endowment | 0.545552 | 0.560682 |
| Reproduction wealth | 0.734455 | 0.754933 |

Both required linear-regression sizes are now audited. Performance remains
a descriptive comparison across different simulation random streams; no
new acceptance margin is introduced. The original 200-bootstrap interval
procedure is retained. Rejection-ABC estimation on the same independent table
is running at both sizes with immediate warning capture and one-hour bounds
per size. Other estimator methods and paper-level interpretation remain open.

### Independent 1,250-input rejection ABC audited

[The completed workflow](results/independent-rejection1250-2026-10-18) validates
all five folds, 6,250 held-out parameter predictions and 943,750 exact input
cells. Baseline errors match the author-data run exactly. Every public archive
member is read back and compared byte-for-byte with the audited native files.

| Parameter | Author-data performance | Independent-data performance |
| --- | ---: | ---: |
| Initial population | 0.170326 | 0.147350 |
| Mutation probability | 0.224828 | 0.232909 |
| Maximum sugar endowment | 0.156109 | 0.160068 |
| Maximum spice endowment | 0.143698 | 0.128314 |
| Reproduction wealth | 0.598317 | 0.594002 |

These are descriptive cross-simulation comparisons, without an equivalence
margin or paper-level verdict. The full-size rejection workflow and both
semi-automatic one-degree estimator sizes are active under one-hour-per-size
bounds, using frozen author functions and immediate warning capture.

### Independent 1,250-input semi-automatic ABC audited

[The degree-one workflow](results/independent-sabc1d1250-2026-10-18) validates
all five folds, 6,250 held-out parameter predictions and 943,750 exact input
cells. Baseline errors match the author-data run exactly. Every public archive
member matches its audited native file byte-for-byte.

| Parameter | Author-data performance | Independent-data performance |
| --- | ---: | ---: |
| initial.population | 0.463495 | 0.481085 |
| pmut | 0.350284 | 0.359729 |
| maximum.sugar.endowment | 0.423884 | 0.443673 |
| maximum.spice.endowment | 0.436138 | 0.445264 |
| wealth.reproduction | 0.563549 | 0.577930 |

These comparisons describe separate simulation random streams; they do not
establish equivalence or complete the paper. The 5,000-input degree-one and
rejection workflows remain active under their existing one-hour bounds.

### Independent 5,000-input semi-automatic ABC audited

[The full-size degree-one workflow](results/independent-sabc1d5000-2026-10-18)
validates all five folds, 25,000 held-out parameter predictions and 3,775,000
exact input cells. Baseline errors match the author-data run exactly. Every
public archive member matches its audited native file byte-for-byte.

| Parameter | Author-data performance | Independent-data performance |
| --- | ---: | ---: |
| initial.population | 0.546478 | 0.543322 |
| pmut | 0.372123 | 0.388448 |
| maximum.sugar.endowment | 0.505361 | 0.507500 |
| maximum.spice.endowment | 0.516449 | 0.513282 |
| wealth.reproduction | 0.601442 | 0.603185 |

Both degree-one sample sizes are now audited. These descriptive comparisons
use separate simulation random streams and do not establish equivalence.
Other independent estimators and historical Table 8 discrepancies remain open.
