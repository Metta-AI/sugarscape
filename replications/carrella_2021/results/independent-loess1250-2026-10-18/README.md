# Independent-simulator GAM, 1,250 inputs

The author generalized additive model estimator completed all five held-out folds
on the first 1,250 independently simulated inputs in 4,893.5 seconds.
The released method is named `loess`; its implementation uses `mgcv::bam`.
The original 146 predictors, selection/discrete options, seed zero, and
10,000 interval draws per held-out observation remain unchanged.

The provenance audit exactly checked 943,750 training/testing cells.
The separate prediction audit validated 6,250 held-out parameter predictions
and recomputed root mean squared errors, interval coverage, and interval widths.
`validated-metrics.csv` contains the resulting five parameter rows.
This establishes execution and audited predictions, not agreement with Table 8.
The 5,000-input run remains ongoing; the whole study remains incomplete.

The archive retains all native fold objects, complete aggregate, package versions,
commands, source scripts, and output log. Every member was compared byte-for-byte
against its retained source. `archive-receipt.json` records its size and SHA-256.
