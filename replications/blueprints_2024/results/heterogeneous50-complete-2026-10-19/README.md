# Complete heterogeneous 50% condition

All 500 original inputs for 50% utilitarian and 50% egoistic agents are independently audited.
The ensemble exits zero; its terminal archive contributes 24 inputs and 100,779 observations: 20 full runs and four native extinctions.
Two fresh extractions reproduce all 24 producer audits byte-for-byte and verify 1,250 archive files.
The full inventory preserves all 982 previous records exactly, reaching 1,006/100,000 supplementary inputs.
Terminal archive: 9,386,515 bytes, SHA256 `4d1102ad108537198e08fbbbc148d2119b874c128be3e265740337641ff96488`.

## Population comparison with Figure 16

The complete condition contains 1,781,148 observations and 150 native extinctions.
The paper plots the median of per-run mean population across 500 seeds.
Our complete-condition medians fall within the independently extracted Figure 16 ink interval, 925.371924–943.243674:

| Averaging convention | Median population |
| --- | ---: |
| Observed rows, including initial state | 938.1762647470506 |
| Observed rows, excluding initial state | 938.3139 |
| Zero after extinction, including initial state | 938.1762647470506 |
| Zero after extinction, excluding initial state | 938.3139 |

Zero extension assumes the population remains zero after native extinction; it does not change this cohort's median.
The primary calculation uses exact rational arithmetic. Repeating the full trajectory analysis produces byte-identical summaries and per-run records.
Independent NumPy sorting selects the same exact rational middle pair under all four conventions.
The initial bit-for-bit floating check failed for two conventions: rounding each run mean before averaging differs from rounding the exact midpoint by one floating-point unit.
That retained failure is explained and checked in `population/comparison.json`; the exact primary result is unchanged.

This reproduces the plotted median for this complete condition within graphical precision under four explicit conventions.
The ink interval is not a confidence interval. Historical averaging and quantile choices, other population statistics, and the remaining sweep remain unresolved.
This is not a completed whole-paper replication. No additional study-completion credit is assigned.
