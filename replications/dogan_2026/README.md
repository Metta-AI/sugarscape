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

## Inequality rankings and resource-exhaustion tables

`audit_transition.py CSV PROVENANCE NEW_OUTPUT` reconstructs Tables 2 and 5 from all 105 native transition runs.
[Fresh results](results/transition-tables-2026-10-15/tables2-and5.json) match all 168 printed means, coefficients of variation, death counts, fractions, and stocks at death.
The inequality rankings change across automation speeds, as reported; this calculation does not establish statistical significance or causal attribution.
Single-resource death fractions span 87.389–98.026% across five-seed means, but 80–100% across individual runs.
The manuscript's 87.4–98.0% range therefore describes group means, not bounds on every seed.
These results preserve the table's averaging convention rather than replacing mean fractions with pooled death ratios.

## Fresh 600-step horizon replication

[The complete horizon experiment](results/horizon-2026-10-15/comparison.json) finishes all 45 runs with native exit status zero.
Its 360 output cells match the author deposit; the CSV is byte-identical.
The independent Table D.1 audit also matches all 36 printed values from fresh runs.
Means-tested mortality at 600 steps is 6.535–9.751% of the same-speed baseline across the six comparisons.
The original log, source manifest, completion record, complete CSV, and both audits are retained.
Composition, levy, per-seed calibration, multiplier, and welfare-sensitivity studies remain unfinished; this is not a complete paper-level verdict.

## Welfare-sensitivity audit and reporting discrepancy

`audit_welfare.py MAIN_CSV SENSITIVITY_CSV PROVENANCE NEW_OUTPUT` checks all fifteen paired five-seed cells, death accounting, printed values, and unrounded policy rankings.
[The deposited-data audit](results/deposited-welfare-audit-2026-10-15/table-b1.json) matches all 120 Table B.1 values.
All three mortality rankings remain unchanged; two of three inequality rankings remain unchanged.
Under balanced automation, baseline minus Universal High Income (UHI) mean Gini changes from −0.002635257 to +0.000285507.
That small reversal contradicts the literal no-ranking-change statement, but does not establish a statistically meaningful difference or invalidate the main mortality finding.
Cross-type trade reductions span 58.211–93.101%, clarifying the prose's approximate 60–90% range.
Fresh welfare simulations are still running; deposited-data consistency checks are not counted as a fresh replication or completed negative study.

## Transfer-multiplier validation

`audit_uhi.py SWEEP BENCHMARK PROVENANCE NEW_OUTPUT` requires the complete sixty-run grid and reconciles all fifteen two-times settings with canonical results.
It checks the common base transfer rate, mortality accounting inputs, and each five-seed comparison against wealth-funded means-tested redistribution.
[Deposited-data results](results/deposited-uhi-audit-2026-10-15/multiplier-audit.json) reconcile all fifteen canonical rows.
All twelve speed/multiplier means have higher mortality than the means-tested benchmark, with ratios from 1.541 to 1.844.
These are descriptive means, not significance tests; the fresh sweep must pass its own source-output and interpretation audits.

## Fresh transfer-multiplier replication

[All sixty native runs](results/multiplier-2026-10-15/comparison.json), plus both calibration runs, complete with exit status zero.
All 360 output cells match the author deposit, and the complete CSV is byte-identical.
The independent fresh audit reconciles all fifteen two-times settings with the canonical sweep.
All twelve speed/multiplier mean mortality ratios remain above the means-tested benchmark, spanning 1.541–1.844.
Native source and benchmark hashes, exit status, log, both CSVs, and both audits are retained.
Other robustness studies remain outstanding, so this component does not complete the full paper.

`run_reports.py ENGINE COMPLETED_CANONICAL NEW_OUTPUT` regenerates the author's nine canonical reports in an isolated directory.
It requires a successful full canonical exit, preserves the four fresh input CSVs, verifies the pinned source and environment, and compares every generated report byte-for-byte with its deposit.
This author-analysis replay complements the independent numerical audits; it does not replace them.

## Complete canonical replay and original reports

[The full canonical sweep](results/full-canonical-2026-10-15/comparison.json) completes 205 experiments and both original calibration runs with exit status zero.
All 206,010 cells match the deposited four CSVs, including missingness; all four files are byte-identical.
The 75-run welfare-sensitivity component reconstructs all 120 Table B.1 values from fresh results.
Its unrounded balanced-automation baseline/UHI reversal is therefore reproduced by the fresh simulation, not only found in deposited data.
The small difference remains descriptive; all three mortality rankings are unchanged.

The unmodified author analysis regenerates all nine canonical text reports byte-for-byte from these fresh inputs.
Source manifests, full native logs, exit records, all four CSVs, independent welfare analysis, and original report outputs are retained.
Composition, displacement-levy, per-seed calibration, remaining manuscript claims, and fork integration still prevent a completed paper verdict.

## Running the bundled study from this fork

The `vendor/` directory contains unchanged author source, model data, experiment scripts, and original MIT/Apache notices.
`vendor-provenance.json` pins every file to the original Git revision by SHA-256.
This integrates the original model into the study; it does not claim the DTL engine implements the same rules independently.
The separate reference runners remain the original-code comparison path and their evidence is preserved.

Create the study environment and run a complete experiment:

```sh
uv venv --python 3.12.4 /tmp/sugarscape-dogan-env
uv pip install --python /tmp/sugarscape-dogan-env/bin/python -r replications/dogan_2026/environment.txt
/tmp/sugarscape-dogan-env/bin/python replications/dogan_2026/run_fork.py canonical /tmp/dogan-canonical-new
```

Exact replay has been evaluated on macOS arm64; other platforms require comparison rather than assumed numerical equivalence.
The same command accepts `horizon`, `composition`, `levy`, and `perseed` as full original experiments.
`multiplier` and `reports` additionally require `--canonical PATH_TO_COMPLETED_RUN` and preserve input hashes.
Every run requires a fresh output directory, records exit status and source/environment hashes, and leaves failures visible.

[Bundled report verification](results/fork-reports-2026-10-15) regenerates all nine reports identically to the separate original analysis.
The complete bundled canonical simulation is being run separately; report agreement alone does not establish native execution equivalence.

## Legacy starvation-script scope

[The source audit](legacy-starvation-protocol-audit.json) compares the older starvation runner with canonical Part B at the pinned revision.
Both use the same seven policies, three automation speeds, five seeds, 300-step horizon, seed42 calibration, and geometric-mean welfare rule.
The completed canonical sweep therefore covers this cumulative-mortality experiment; the older script does not supply another independent set of conditions.
Its stock-at-death statistic differs: it averages positive per-step means equally, whereas the canonical calculation weights those means by deaths.
The old report is not asserted reproduced, and its stock statistic must not replace the current manuscript's measurement.
This resolves duplicated simulation scope without counting repeated settings as additional evidence.

## Composition table and ranking claims

`audit_composition.py COMPOSITION_CSV CANONICAL_CSV PROVENANCE NEW_OUTPUT` checks the full 315-run combined grid and reconstructs Table C.1.
[Deposited-data results](results/deposited-composition-audit-2026-10-15/table-c1.json) match all 126 printed values.
The baseline has highest mortality and the two pure means-tested policies lowest mortality in all nine composition/speed settings.
There are nevertheless two distinct full mortality orderings, so that narrower result must not be restated as complete rank invariance.
Seven of nine tested inequality ranks rise from slow to fast automation when the displacement levy is included.
The two exceptions are low-composition levy, fifth-to-first, and high-composition wealth/means-tested, seventh-to-fifth.
The prose's explanation that those ranks were already fixed at extremes does not match these unrounded rankings.
These are reporting checks on deposited data; fresh composition runs remain pending and no whole-paper negative verdict is assigned.

## Bundled simulation verification

[The bundled Part A](results/fork-static-2026-10-15/comparison.json) completes all 25 static runs and produces a byte-identical CSV to the independent author replay.
The full bundled canonical process continues; this component does not imply a successful final exit.
`compare_fork.py REFERENCE_REPLAY FORK_RUN NEW_OUTPUT` requires successful complete canonical runs, matching pinned model provenance, the full four-file output ledger, and all 206,010 cells.
Its report-only rejection was exercised through the public command: nine valid generated reports are insufficient simulation evidence.
The full comparison remains pending native completion.

## Independent static and Universal High Income table audit

[Tables 1 and 6](results/static-uhi-2026-10-15) match all 56 printed numeric values against fresh canonical simulations.
The auditor validates complete 25-run static and 105-run transition grids, then independently computes means, sample coefficients of variation, and baseline mortality percentages.
Static mean rankings match for inequality and mortality: wealth/means-tested, labor/means-tested, wealth/UBI, labor/UBI, baseline.
Universal High Income produces more deaths than either pure means-tested policy in all 30 paired transition-seed comparisons.
These are descriptive comparisons across the published seeds, not significance tests or causal identification.

The manuscript's static-results sentence says every coefficient of variation is below 0.13.
Fresh data give a maximum of 0.1320268268 for labor/means-tested Gini, correctly printed as 0.132 in Table 1.
All static coefficients remain below 0.15. This is a narrow prose discrepancy, not a failed numerical table replication.
A changed-Gini copy of the complete static input is rejected; its mismatch report is retained alongside the successful audit.
The canonical originals remain unchanged.

## Confirmed native levy accounting defect

[A traced native run and independent repeat](results/levy-events-2026-10-15) use fast automation, D=50, seed zero, and 300 steps.
All per-step outputs are byte-identical with and without the observer.
Final inequality, cumulative mortality, tax revenue, and redistribution match the corresponding fresh canonical run.

All 60 observed levy events violate transfer conservation: owners lose 762.5 units, but the treasury receives 180.0583142.
The original code deducts `W * min(1,L/W)` but credits `L * min(1,L/W)`, where W is incoming owner wealth and L the nominal levy.
Equation 4 specifies the same capped amount, `min(L,W)`, deducted and credited.
No observed event reaches the owner-wealth cap in this run; the manuscript's roughly-quarter claim is not supported by this diagnostic.

The [declared correction study](LEVY_DIAGNOSTIC.md) retains a separate accounting patch and specifies a paired 75-run sweep.
Original and bundled source remain unchanged for faithful replay.
The defect establishes a code/specification discrepancy; its impact on policy conclusions remains unmeasured.
