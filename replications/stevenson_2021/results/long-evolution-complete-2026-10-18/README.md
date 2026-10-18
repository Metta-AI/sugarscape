# Complete conditional long-run evolutionary ensembles

All 200 runs complete 100,000 cycles without extinction: 20 million native cycles and 200,200 recorded observations.
Both scenarios retain the same 100 seeds as the earlier 500-cycle experiments, with exact matches at all shared sample times.
They extend prior trajectories; they are not additional independent seeds.
Every final population is fixed at its joint minimum-infertility/zero-birth-cost trait combination.

The independent analyzer validates model/source hashes, commands, sample schedules, finite bounds, native accounting outputs and all sampled joint-trait populations.
The native model checks resource and population balances on every cycle, including unrecorded cycles.
A second native-CSV readback recomputes 96 statistical quantities with Python's standard-library statistics and R's Student-t critical value.
The maximum absolute discrepancy is 3.42e-10. All native archive members pass SHA-256 readback.
Execution took 697.18 seconds after qualification, within the declared one-hour limit.

## Late-window results

Means below use seed-level time averages for cycles 75,100–100,000, sampled every 100 cycles.
The paper's precise sampling procedure and interpretation of its percentage uncertainties remain unknown.

| Metric | Stable reconstruction | Stable Table 1 | Chaotic reconstruction | Chaotic Table 1 |
| --- | ---: | ---: | ---: | ---: |
| Population | 858.77408 | 859 | 919.12496 | 916 |
| Mean age | 12.761814 | 12.7 | 1.390324 | 1.41 |
| Total wealth | 499.61400 | 504 | 466.60244 | 480 |
| Gini | 0.689854 | 0.688 | 0.728303 | 0.73 |

All eight mean changes between the declared earlier and later windows have seed-based 95% intervals containing zero.
This does not prove stationarity or equivalence to the paper.
The complete per-seed windows, standard deviations and confidence intervals are retained in `analysis/analysis.json`.

## All Table 1 means

`table1/comparison.csv` combines these eight new late-window estimates with the previously audited fixed-society and growth-fit results.
It covers all twenty printed means and retains all numerical disagreements.
Targets are extracted directly from the hash-pinned original LaTeX, with source rows and printed percentages retained.
Printed percentages are not interpreted as confidence intervals or acceptance bounds.
Population maps to printed carrying capacity K via late-window population mean; that measurement correspondence remains conditional.
Growth estimates come from the separate one-founder continuous-logistic fits, not the initially 830-agent evolutionary trajectories.
In particular, the chaotic growth fit has poor residual behavior; a converged optimizer does not establish an appropriate model.

The stable population and chaotic Gini match printed rounding, but numerical proximity is not a paper-level replication verdict.
Fixed-society mean-age discrepancies, growth-rate disagreements, original initialization/inheritance, measurement conventions and remaining figure/Appendix B requirements remain unresolved.
No whole-paper completion or validated negative replication is claimed.

```sh
python analyze_long_evolution.py /path/to/completed-experiment /path/to/new-analysis
python compare_table1.py /path/to/original-ssc2021xNojpg.tex /path/to/new-analysis /path/to/new-comparison
```

The full analyzer requires all 200 successful native records and the terminal completion marker.
Earlier qualification and partial snapshots remain retained; this archive contains the complete ensemble and supersedes their coverage counts.
