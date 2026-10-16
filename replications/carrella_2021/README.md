# Carrella (2021): Sugarscape parameter estimation

Paper: [No Free Lunch when Estimating Simulation Parameters](https://www.jasss.org/24/2/7.html), DOI `10.18564/jasss.4572`.
Scope: Sugarscape case study only; conclusions across all 41 models are outside this study.
Status: two author-model replays validated; ten linear-regression and ten rejection-estimation Table 8 values reproduced.
**Not a completed replication:** the other estimators and independent simulator work remain unfinished.

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
records **before** each of 501 `go` calls: ticks 0–500.
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
Four fresh batches are running; no full-ensemble result is claimed yet.
The optimized runner matches all 35,070 numeric trajectory values from the separate-call path on ten complete simulations.
Both paths reproduce 1,500/1,500 archived statistics; the optimized last-input replay also matches 150/150.
[Validation evidence](results/batch-validation-2026-10-15) includes trajectories, comparisons, hashes, and timing logs.
An intentionally corrupted reference statistic yields 1,499/1,500 matches and a nonzero exit, confirming that the comparison gate detects disagreement.

## Replication work remaining

1. Extend the Table 8 comparison to the remaining eight estimators and interval coverage.
2. Expand the validated author replay beyond the first and last archived inputs.
3. Audit DTL trade, reproduction, mutation, welfare, and Gini semantics against this source.
4. Implement and validate the required study-specific behavior in this fork.
5. Complete both simulation ensembles and estimator comparisons, retaining failures and uncertainty.

Do not replace the traded two-resource model with the one-resource McCulloch variant.
Do not count analysis of the archived table alone as an independent simulation replication.
