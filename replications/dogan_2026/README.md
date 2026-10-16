# Dogan (2026): Policy Robustness Under Accelerating Automation

Source: [author repository and working paper](https://github.com/dgnerg867-ux/sugarscape), pinned to `0b6a3df470388f60535d8ffb67c34a7f9fa0059a`.
The author's citation identifies this as an unpublished 2026 working paper, not a peer-reviewed publication.
This study supplements the existing replication program; it does not replace unfinished studies.

The repository contains the manuscript, original model, canonical result tables, and experiment scripts.
Author contributions use MIT licensing; Mesa-derived files retain Apache-2.0 licensing and attribution.
The reference checkout remains separate and unmodified.

## Declared execution protocol

Use the author's Python 3.12.4 and exact four dependency versions from `requirements.txt` on macOS arm64.
Run `python replications/dogan_2026/run.py REFERENCE NEW_OUTPUT` using that environment.
The runner validates the source revision, clean tracked files, and installed versions before execution.
It launches the original script in a fresh output directory, preserving published CSVs and recording source/reference hashes.
`PYTHONHASHSEED=0` is an explicit reproducibility setting; the model's original seeds and all experimental settings remain unchanged.

The canonical sweep includes 25 static-policy runs, 105 transition runs, 75 welfare-sensitivity runs, and two threshold-calibration runs.
All policy experiments retain the original five seeds and 300-step horizons.
Compare every output row and column with the author's corresponding CSV before interpreting the paper's claims.
Undefined statistics must retain matching missingness rather than being silently replaced or excluded.
Validate the reported tables and policy rankings independently of the author's analysis.

## Remaining scope

Canonical execution alone does not complete this paper.
The manuscript also includes composition, per-seed threshold, displacement-levy, horizon, starvation, and transfer-rate robustness analyses.
Their exact reported targets and scripts require auditing, followed by complete executions and independent comparisons.
An equivalent integration in the Metta-AI fork and paper-level conclusions remain unfinished.

## Environment recovery

The exact four-package installation fails before simulation: Mesa imports `networkx`, which the author's requirements omit and Mesa declares as an extra.
The failed run's manifest, traceback, and exit status are retained.
A separate retry adds NetworkX 3.7; this version is our recovery choice, not a verified author version.
`environment.txt` records every installed distribution so transitive dependencies are explicit.
The original Python version and four author-pinned versions remain unchanged.
The snapshot reference has 24,675 rows; no constant-population assumption is imposed on the transition model.

## First completed canonical comparison

[Part A](results/static-2026-10-15/comparison.json) completes all 25 static-policy runs.
All 1,050 cells match the original 25-row, 42-column CSV at the declared tolerance; the entire CSV is also byte-identical.
The remaining canonical experiments are still running. This is not a complete paper replication.

## Robustness execution and targets

`run_robustness.py REFERENCE NEW_OUTPUT` runs four original scripts sequentially, with original seeds and full horizons.
The queue covers 45 horizon runs at 600 steps, 210 composition runs, 75 displacement-levy runs, and 105 per-seed threshold runs.
The latter three retain 300 steps; each script also performs its original calibration runs.
The runner checks the complete recovered environment and source hashes, and records each native exit status.

[Manuscript targets](manuscript-targets.json) preserve all nine Table D.1 rows before fresh horizon results arrive.
The deposited horizon and composition CSVs permit full per-seed comparisons.
The levy and per-seed threshold CSVs are absent from the public deposit; their regenerated outputs must be checked against manuscript claims.
The transfer-multiplier script requires a canonical Part B CSV for its benchmark; it remains pending fresh canonical completion.
The older starvation script overlaps the canonical mortality study and requires a source comparison before deciding whether it adds distinct evidence.

## Independent horizon-table audit

`audit_horizon.py CSV PROVENANCE NEW_OUTPUT` requires the complete 45-run speed/policy/seed grid and reconstructs Table D.1 directly.
The validator checks finite metrics, Gini bounds, monotonic cumulative mortality, all 36 printed table cells, and six mortality ratios.
It records whether the input is the author deposit or a fresh replay; provenance is not inferred from numerical agreement.

[The deposited-data audit](results/deposited-horizon-audit-2026-10-15/table-d1.json) matches all 36 table values at printed precision.
At 600 steps, the means-tested mortality ratios range from 0.06535 to 0.09751 of the same-speed baseline.
This confirms internal reporting consistency only. Fresh horizon simulations are still running and must pass separate native-output and table checks.

## Mortality table and transfer-multiplier coverage

`audit_mortality.py CSV PROVENANCE NEW_OUTPUT` checks all 105 speed/policy/seed combinations and reconciles each run's three death categories.
[The deposited-data audit](results/deposited-mortality-audit-2026-10-15/table4.json) reconstructs all 42 Table 4 means and coefficients of variation at printed precision.
It explicitly reports both sample and population coefficients; the sample convention matches the table.
The seven-policy mortality ranking is identical across the three automation speeds in these deposited data.
This checks reporting consistency; fresh simulation and full-paper verification remain separate requirements.

`run_uhi.py ENGINE FRESH_CANONICAL NEW_OUTPUT` runs the author's sixty transfer-multiplier experiments and both original calibrations.
Before starting, it requires every fresh Part B benchmark cell to match the pinned deposit, including missing values, at the declared tolerance.
It copies that verified fresh benchmark into the isolated output directory and records hashes, rather than using deposited outcomes as fresh results.

## Fresh transition sweep

[Part B evidence](results/transition-2026-10-15/comparison.json) contains all 105 native transition runs and the 24,675-row agent snapshot.
All 201,810 cells match the author deposit at the declared tolerance, including missing values; both CSVs are also byte-identical.
The fresh data reconstructs all 42 Table 4 values and passes per-run mortality-cause accounting.
The native canonical process continues with Part C, so this evidence makes no claim about its eventual exit status.
The transfer-multiplier run has started using this verified fresh benchmark.
Full welfare sensitivity, robustness comparisons, and remaining manuscript claims still require validation before this paper can count as completed.

## Independent inequality decomposition

`audit_decomposition.py SNAPSHOT MAIN_CSV PROVENANCE NEW_OUTPUT` reconstructs the inequality decomposition directly from individual wealth, using pairwise absolute differences.
It imports no author analysis functions, checks wealth accounting and population totals, and reconciles every run's Gini with the native aggregate output.
[Fresh evidence](results/decomposition-2026-10-15/table3.json) covers all 24,675 agent records across 105 runs and matches all 105 printed Table 3 values.
Between-type shares are averaged per run, matching the reported five-seed means.
This validates the numerical decomposition; it does not by itself establish the paper's causal explanation of policy rankings.

`compare_robustness.py ENGINE RUN horizon|composition|uhi NEW_OUTPUT` requires a successful native experiment before comparing every output cell with its pinned deposit.
It verifies source hashes, row keys, missingness, native ordering, and the declared numerical tolerance.
For the multiplier study it also checks that the verified fresh benchmark remained unchanged.
