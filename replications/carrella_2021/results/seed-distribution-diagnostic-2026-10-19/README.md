# Exploratory distribution comparison

All 64 native and 64 independent runs from the existing fixed-parameter ensemble are retained.
The six metrics cover final/minimum population, price at observation 475, final price, maximum price and mean price.
This parameter setting was selected after estimator failures; this analysis is exploratory.

The largest empirical cumulative-distribution difference is 0.1875, for mean price.
Among 19,999 shared label permutations, 13,864 have an equal or larger maximum across the six metrics.
The plus-one Monte Carlo p-value is 0.69325. Individual values range from 0.2092 to 0.9878.
Ties are retained; shared permutations preserve dependence between metrics.
Seed labels are unpaired because the engines use different random streams.

These outcomes provide no evidence here for a broad distribution shift, but do not establish equivalence.
They cannot resolve the frequency of rare persistent price spikes with 64 runs per engine.
The next stochastic validation needs additional independently declared seeds or a mechanism-level diagnosis of the rare trajectories.
Neither primary estimator results nor the study's incomplete status changes.

Two complete CLI executions produce byte-identical summaries.
A separate direct threshold-count calculation agrees exactly with each observed distribution statistic.
The input CSV hash and NumPy version are retained in the report.

Run from the repository root:

```sh
python replications/carrella_2021/results/seed-distribution-diagnostic-2026-10-19/analyze.py \
  replications/carrella_2021/results/fixed-parameter-seeds-2026-10-19/runs.csv /path/to/new-output
```
