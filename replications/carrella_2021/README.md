# Carrella (2021): Sugarscape parameter estimation

[Completed qualified method reproduction](results/method-verdict-2026-10-19), under the user’s October 19 method-based criterion. All original simulation inputs and reported estimator workflows are complete. The 37 numerical discrepancies and historical provenance qualifications remain explicit; this is not a validated negative paper verdict.

[The complete ten-seed historical GAM sensitivity is audited](results/gam-historical-seed-sensitivity-complete-2026-10-19). All 56,250 additional point predictions exactly match seed zero; all 112,500 interval bounds differ. None of the five printed scores is recovered by any seed. The bounded experiment is complete; historical provenance and the 37 primary discrepancies remain unresolved.

Paper: [No Free Lunch when Estimating Simulation Parameters](https://www.jasss.org/24/2/7.html), DOI `10.18564/jasss.4572`.
Scope: Sugarscape case study only; conclusions across all 41 models are outside this study.
Status: completed qualified method reproduction. All 5,000 fresh author-model simulations and all reported independent estimator workflows are validated. Of 75 Table 8 values, 38 match printed precision and 37 remain discrepant.
The [complete ten-setting diagnostic](results/parameter-cohorts-complete-2026-10-19) validates 1,280 runs and 641,280 observations. None of the 30 predeclared comparisons rejects after Holm correction. Archive readback, repeated aggregation, and independent R checks pass. This does not establish stochastic equivalence or resolve the historical estimator discrepancies.

[The updated discrepancy-control reconciliation](results/discrepancy-control-reconciliation-full-data-2026-10-19) verifies all 90 table cells and joins 18 discrepant scores to selected same-size controls. Seven of nine SABC1D discrepancies fall within observed seed ranges; spice endowment remains outside at both sizes. Primary scores and the other controls remain unchanged.

[The full-data estimator sensitivity control is complete](results/sabc1d5000-seed-sensitivity-complete-2026-10-19): all ten seeds pass 37,750,000 input-cell and 250,000 prediction checks. Four published scores lie within observed seed ranges; spice endowment remains outside. Independent arithmetic, fresh archive analysis, and object-storage readback pass. These ranges are not confidence intervals and do not change primary scores.

[A historical abctools source check](results/abctools-source-history-2026-10-19) finds one transformation-validation change in `semiauto.abc` between 2018 and 2025. Its sampling and regression source is unchanged; dependencies and historical runtime remain unresolved.

[The complete-ensemble analyzer](results/seed-summary-analyzer-validation-2026-10-19) independently recomputes estimator and training-mean baseline errors. It passes the complete 1,250-input control; its completion gate rejected the then-unfinished full-data ensemble before output.

[The historical abc source check](results/abc-source-history-2026-10-19) confirms unchanged estimator and numerical-summary function bodies between versions 2.1 and 2.2.2. The changed histogram and model-choice paths are absent from the audited author wrapper; runtime and dependency uncertainty remain.

**Method completion and numerical agreement are separate:** all independent estimator folds are audited. Historical estimator discrepancies and stochastic equivalence remain unresolved; the method verdict above records the qualifications.

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

## Preserved evidence

[The full experiment record](https://github.com/Metta-AI/sugarscape/blob/d2b4b5c81b43de87e01264e243e8ef1b57d377b5/replications/carrella_2021/README.md) retains dated runs, budgets, failures, source hashes, figures, and detailed controls. Existing histories, outputs, and checkpoints remain unchanged. Historical launch notes do not establish current job status. Restore archived raw inputs before rerunning an analysis, as described in that record.
