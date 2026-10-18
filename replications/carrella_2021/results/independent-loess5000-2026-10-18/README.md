# Independent-simulator GAM, 5,000 inputs

All five held-out folds completed in 5,206.0 seconds using the original 146 predictors,
selection/discrete options, seed zero, and 10,000 interval draws per held-out observation.
The released method is named `loess`; its implementation uses `mgcv::bam`.
No estimator settings changed between the declared sizes.

The fold audit exactly validates 3,775,000 training/testing values.
The independent prediction audit checks 25,000 predictions and recomputes the released
mean-fold root mean squared error, interval coverage, and interval widths.

| Parameter | Performance score | Interval coverage |
| --- | ---: | ---: |
| Initial population | 0.663102 | 0.9324 |
| Mutation probability | 0.360610 | 0.9226 |
| Maximum sugar endowment | 0.586290 | 0.9320 |
| Maximum spice endowment | 0.593215 | 0.9356 |
| Reproduction wealth | 0.662000 | 0.9140 |

Performance is one minus mean-fold error divided by the corresponding baseline error.
These results describe the independently simulated input statistics. They do not replace
the author-data experiment or resolve the paper's historical discrepancies.

All native fold objects, complete aggregate, source scripts, execution receipt, package
versions, and logs are retained in the archive. All 18 members were checked byte-for-byte.
Both audits were rerun from a fresh extraction; their results matched the original audits exactly.
`archive-receipt.json` pins the 17,777,197-byte archive.

Both GAM sizes are now complete. Neural-network and bootstrap-forest experiments remain
unfinished, and the whole study remains incomplete.
