# Independent-simulator bootstrap forest, 1,250 inputs

The original bootstrap-forest estimator completed all five folds in 10,548.8 seconds.
The run preserves 146 predictors, seed zero, caret/ranger tuning, the best-model refit,
infinitesimal-jackknife uncertainty with the released fallback, and 1,000 interval draws.
No scientific settings were reduced to complete the run.

The provenance audit checks 943,750 training/testing values exactly.
A separate prediction audit validates all 6,250 parameter predictions and recomputes
mean-fold root mean squared error, coverage, and interval widths.

| Parameter | Independent-data performance | Published performance |
| --- | ---: | ---: |
| Initial population | 0.416131 | 0.416 |
| Mutation probability | 0.494192 | 0.503 |
| Maximum sugar endowment | 0.400567 | 0.392 |
| Maximum spice endowment | 0.419041 | 0.441 |
| Reproduction wealth | 0.752162 | 0.764 |

One of five values agrees at printed precision. This does not replace the primary
author-data experiment or establish historical equivalence. Coverage ranges from
0.9528 to 0.9600 across the five parameters; all individual interval widths remain retained.

The archive preserves native folds, the complete aggregate, commands, source scripts,
execution receipt, package versions, and output log. Every archive member was
byte-checked. Both audits were rerun from a fresh extraction and matched exactly.
The 5,000-input batch remains running under its existing four-hour limit.
Neural-network outputs and unresolved estimator discrepancies still prevent completion.
