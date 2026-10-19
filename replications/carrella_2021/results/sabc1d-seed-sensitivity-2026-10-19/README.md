# Fixed-data estimator seed sensitivity

Ten predeclared seeds (1–10) rerun the complete 1,250-input, five-fold semi-automatic one-dimensional estimator.
The author data, 146 predictors, outer partition seed zero, tolerance, and original estimator remain unchanged.
All ten runs exit zero. Exact train/test comparisons verify 9,437,500 input cells against the primary saved folds.
R audits check 62,500 predictions; independent Python arithmetic from archive bytes reproduces errors, coverage, widths, and normalized performance within 1e-10.
Relevant package versions match the primary seed-zero execution.

| Parameter | Published | Ten-seed mean | Observed minimum | Observed maximum |
| --- | ---: | ---: | ---: | ---: |
| initial.population | 0.468 | 0.467843 | 0.455719 | 0.478444 |
| maximum.spice.endowment | 0.423 | 0.435883 | 0.424633 | 0.443223 |
| maximum.sugar.endowment | 0.424 | 0.418056 | 0.407445 | 0.424027 |
| pmut | 0.338 | 0.338786 | 0.320642 | 0.348959 |
| wealth.reproduction | 0.567 | 0.567522 | 0.561955 | 0.577906 |

Four published values fall within their observed seed ranges.
Spice endowment remains outside: published 0.423 versus observed 0.424633–0.443223.
The installed `abctools::semiauto.abc` defaults split training rows into disjoint regression and inference halves using random sampling.
The archive retains that function body and the complete runner, protocol, ten fold sets, prediction audits, package versions, and exit receipts.

Observed ranges are not confidence intervals. Ten seeds cannot establish distributional equivalence or identify the historical notebook random state.
No primary score is replaced, no additional printed-precision match is claimed, and no paper-completion credit is assigned.
This diagnostic separates estimator randomness from simulator randomness by using the unchanged author input table.

The archived `run.py` records every command and checks source hashes before each seed.
The archived `audit_inputs.R` compares each fold with the primary result; `analyze_estimator.R` recalculates all prediction metrics.
`summary.json` reports every parameter, and `scores.csv` retains all 50 scores without selection.
