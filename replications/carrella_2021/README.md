# Carrella (2021): Sugarscape parameter estimation

Paper: [No Free Lunch when Estimating Simulation Parameters](https://www.jasss.org/24/2/7.html), DOI `10.18564/jasss.4572`.
Scope: Sugarscape case study only; conclusions across all 41 models are outside this study.
Status: source audit, **not a completed replication**.

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

## Replication work remaining

1. Recover exact paper-specific numerical targets and predeclare comparison criteria.
2. Run the author model with the historical NetLogo version and validate the summary-statistic timing convention.
3. Audit DTL trade, reproduction, mutation, welfare, and Gini semantics against this source.
4. Implement and validate the required study-specific behavior in this fork.
5. Recompute both simulation ensembles and estimator comparisons, retaining failures and uncertainty.

Do not replace the traded two-resource model with the one-resource McCulloch variant.
Do not count analysis of the archived table alone as an independent simulation replication.
