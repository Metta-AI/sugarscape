# Independent initialization-stream diagnostic

This post hoc experiment tests seed reuse as one possible contributor to the Figure 10 discrepancy.
Its design was frozen before execution; it was motivated by the earlier 40x40 reconstruction results.
All 37,600 native runs complete the original 50-step horizon and pass the execution audit.
Seeds are sampled without replacement and never reused across policies, clock phases, models, or replicates.
The auditor reconstructs the frozen assignment and checks every original request, output, policy, source, model, and terminal status.

The scientific reference is a new 10,000-run 50x50 ensemble with 50 independent runs per policy and clock.
The comparisons contain another 10,000 full-size runs and 17,600 40x40 runs.
The old convergence ensemble is used only for the native pipeline qualification, not for scientific rankings here.
All declared budget rounding, tie conventions, mean-rate strata, and linear/quadratic weights are retained.
The analysis performs 38,400 independent rank-value checks and 768 exact-rational concordance checks.

| Comparison | Clock phase | Full-budget pooled mortality concordance, linear average ranks |
| --- | --- | --- |
| 50x50 | 0 | 0.888989 |
| 50x50 | 4 | 0.860484 |
| 40x40 | 0 | 0.868587 |
| 40x40 | 4 | 0.869486 |

Within the three mean-tax-rate strata, 40x40 mortality concordance ranges from 0.528493 to 0.784416 across both clocks.
The separate comparison CSV retains common-seed and independent-seed estimates for every full-budget linear average-rank stratum and metric.
This is a comparison of two finite ensembles, not an uncertainty interval or proof of a population-level effect.
Removing seed reuse lowers several observed concordance estimates but does not establish the original authors' convention or resolve all reconstruction differences.
No validated negative replication or paper-completion credit is claimed.

Raw evidence is retained in the archive; every member passes SHA-256 readback.
The updated analyzer's common-seed path reproduces both existing full-size analysis CSVs byte-for-byte.
