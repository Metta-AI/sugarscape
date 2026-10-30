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

## Current verdict

**Completed mixed replication.** All original numerical experiments and the bundled canonical integration complete.
The [claim-by-claim verdict](VERDICT.md) separates reproduced outcomes from validated mechanism and reporting contradictions.
All 653 printed numerical cells and 42 plotted ordinates reproduce; this is not a wholly positive paper verdict.
The integration uses original author source, not an independently implemented DTL variant.
Earlier component sections below retain their historical findings; the verdict and completed-run evidence supersede pending-run statements.

## Environment recovery

The exact four-package installation fails before simulation: Mesa imports `networkx`, which the author's requirements omit and Mesa declares as an extra.
The failed run's manifest, traceback, and exit status are retained.
A separate retry adds NetworkX 3.7; this version is our recovery choice, not a verified author version.
`environment.txt` records every installed distribution so transitive dependencies are explicit.
The original Python version and four author-pinned versions remain unchanged.
The snapshot reference has 24,675 rows; no constant-population assumption is imposed on the transition model.

## First completed canonical comparison

[Part A](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/static-2026-10-15/comparison.json) completes all 25 static-policy runs.
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

[The deposited-data audit](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/deposited-horizon-audit-2026-10-15/table-d1.json) matches all 36 table values at printed precision.
At 600 steps, the means-tested mortality ratios range from 0.06535 to 0.09751 of the same-speed baseline.
This confirms internal reporting consistency only. Fresh horizon simulations are still running and must pass separate native-output and table checks.

## Mortality table and transfer-multiplier coverage

`audit_mortality.py CSV PROVENANCE NEW_OUTPUT` checks all 105 speed/policy/seed combinations and reconciles each run's three death categories.
[The deposited-data audit](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/deposited-mortality-audit-2026-10-15/table4.json) reconstructs all 42 Table 4 means and coefficients of variation at printed precision.
It explicitly reports both sample and population coefficients; the sample convention matches the table.
The seven-policy mortality ranking is identical across the three automation speeds in these deposited data.
This checks reporting consistency; fresh simulation and full-paper verification remain separate requirements.

`run_uhi.py ENGINE FRESH_CANONICAL NEW_OUTPUT` runs the author's sixty transfer-multiplier experiments and both original calibrations.
Before starting, it requires every fresh Part B benchmark cell to match the pinned deposit, including missing values, at the declared tolerance.
It copies that verified fresh benchmark into the isolated output directory and records hashes, rather than using deposited outcomes as fresh results.

## Fresh transition sweep

[Part B evidence](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/transition-2026-10-15/comparison.json) contains all 105 native transition runs and the 24,675-row agent snapshot.
All 201,810 cells match the author deposit at the declared tolerance, including missing values; both CSVs are also byte-identical.
The fresh data reconstructs all 42 Table 4 values and passes per-run mortality-cause accounting.
The native canonical process continues with Part C, so this evidence makes no claim about its eventual exit status.
The transfer-multiplier run has started using this verified fresh benchmark.
Full welfare sensitivity, robustness comparisons, and remaining manuscript claims still require validation before this paper can count as completed.

## Independent inequality decomposition

`audit_decomposition.py SNAPSHOT MAIN_CSV PROVENANCE NEW_OUTPUT` reconstructs the inequality decomposition directly from individual wealth, using pairwise absolute differences.
It imports no author analysis functions, checks wealth accounting and population totals, and reconciles every run's Gini with the native aggregate output.
[Fresh evidence](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/decomposition-2026-10-15/table3.json) covers all 24,675 agent records across 105 runs and matches all 105 printed Table 3 values.
Between-type shares are averaged per run, matching the reported five-seed means.
This validates the numerical decomposition; it does not by itself establish the paper's causal explanation of policy rankings.

`compare_robustness.py ENGINE RUN horizon|composition|uhi NEW_OUTPUT` requires a successful native experiment before comparing every output cell with its pinned deposit.
It verifies source hashes, row keys, missingness, native ordering, and the declared numerical tolerance.
For the multiplier study it also checks that the verified fresh benchmark remained unchanged.

## Inequality rankings and resource-exhaustion tables

`audit_transition.py CSV PROVENANCE NEW_OUTPUT` reconstructs Tables 2 and 5 from all 105 native transition runs.
[Fresh results](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/transition-tables-2026-10-15/tables2-and5.json) match all 168 printed means, coefficients of variation, death counts, fractions, and stocks at death.
The inequality rankings change across automation speeds, as reported; this calculation does not establish statistical significance or causal attribution.
Single-resource death fractions span 87.389–98.026% across five-seed means, but 80–100% across individual runs.
The manuscript's 87.4–98.0% range therefore describes group means, not bounds on every seed.
These results preserve the table's averaging convention rather than replacing mean fractions with pooled death ratios.

## Fresh 600-step horizon replication

[The complete horizon experiment](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/horizon-2026-10-15/comparison.json) finishes all 45 runs with native exit status zero.
Its 360 output cells match the author deposit; the CSV is byte-identical.
The independent Table D.1 audit also matches all 36 printed values from fresh runs.
Means-tested mortality at 600 steps is 6.535–9.751% of the same-speed baseline across the six comparisons.
The original log, source manifest, completion record, complete CSV, and both audits are retained.
Composition, levy, per-seed calibration, multiplier, and welfare-sensitivity studies remain unfinished; this is not a complete paper-level verdict.

## Welfare-sensitivity audit and reporting discrepancy

`audit_welfare.py MAIN_CSV SENSITIVITY_CSV PROVENANCE NEW_OUTPUT` checks all fifteen paired five-seed cells, death accounting, printed values, and unrounded policy rankings.
[The deposited-data audit](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/deposited-welfare-audit-2026-10-15/table-b1.json) matches all 120 Table B.1 values.
All three mortality rankings remain unchanged; two of three inequality rankings remain unchanged.
Under balanced automation, baseline minus Universal High Income (UHI) mean Gini changes from −0.002635257 to +0.000285507.
That small reversal contradicts the literal no-ranking-change statement, but does not establish a statistically meaningful difference or invalidate the main mortality finding.
Cross-type trade reductions span 58.211–93.101%, clarifying the prose's approximate 60–90% range.
Fresh welfare simulations are still running; deposited-data consistency checks are not counted as a fresh replication or completed negative study.

## Transfer-multiplier validation

`audit_uhi.py SWEEP BENCHMARK PROVENANCE NEW_OUTPUT` requires the complete sixty-run grid and reconciles all fifteen two-times settings with canonical results.
It checks the common base transfer rate, mortality accounting inputs, and each five-seed comparison against wealth-funded means-tested redistribution.
[Deposited-data results](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/deposited-uhi-audit-2026-10-15/multiplier-audit.json) reconcile all fifteen canonical rows.
All twelve speed/multiplier means have higher mortality than the means-tested benchmark, with ratios from 1.541 to 1.844.
These are descriptive means, not significance tests; the fresh sweep must pass its own source-output and interpretation audits.

## Fresh transfer-multiplier replication

[All sixty native runs](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/multiplier-2026-10-15/comparison.json), plus both calibration runs, complete with exit status zero.
All 360 output cells match the author deposit, and the complete CSV is byte-identical.
The independent fresh audit reconciles all fifteen two-times settings with the canonical sweep.
All twelve speed/multiplier mean mortality ratios remain above the means-tested benchmark, spanning 1.541–1.844.
Native source and benchmark hashes, exit status, log, both CSVs, and both audits are retained.
Other robustness studies remain outstanding, so this component does not complete the full paper.

`run_reports.py ENGINE COMPLETED_CANONICAL NEW_OUTPUT` regenerates the author's nine canonical reports in an isolated directory.
It requires a successful full canonical exit, preserves the four fresh input CSVs, verifies the pinned source and environment, and compares every generated report byte-for-byte with its deposit.
This author-analysis replay complements the independent numerical audits; it does not replace them.

## Complete canonical replay and original reports

[The full canonical sweep](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/full-canonical-2026-10-15/comparison.json) completes 205 experiments and both original calibration runs with exit status zero.
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

[Bundled report verification](https://github.com/Metta-AI/sugarscape/tree/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/fork-reports-2026-10-15) regenerates all nine reports identically to the separate original analysis.
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
[Deposited-data results](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/deposited-composition-audit-2026-10-15/table-c1.json) match all 126 printed values.
The baseline has highest mortality and the two pure means-tested policies lowest mortality in all nine composition/speed settings.
There are nevertheless two distinct full mortality orderings, so that narrower result must not be restated as complete rank invariance.
Seven of nine tested inequality ranks rise from slow to fast automation when the displacement levy is included.
The two exceptions are low-composition levy, fifth-to-first, and high-composition wealth/means-tested, seventh-to-fifth.
The prose's explanation that those ranks were already fixed at extremes does not match these unrounded rankings.
These are reporting checks on deposited data; fresh composition runs remain pending and no whole-paper negative verdict is assigned.

## Bundled simulation verification

[The bundled Part A](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/fork-static-2026-10-15/comparison.json) completes all 25 static runs and produces a byte-identical CSV to the independent author replay.
The full bundled canonical process continues; this component does not imply a successful final exit.
`compare_fork.py REFERENCE_REPLAY FORK_RUN NEW_OUTPUT` requires successful complete canonical runs, matching pinned model provenance, the full four-file output ledger, and all 206,010 cells.
Its report-only rejection was exercised through the public command: nine valid generated reports are insufficient simulation evidence.
The full comparison remains pending native completion.

## Independent static and Universal High Income table audit

[Tables 1 and 6](https://github.com/Metta-AI/sugarscape/tree/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/static-uhi-2026-10-15) match all 56 printed numeric values against fresh canonical simulations.
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

[A traced native run and independent repeat](https://github.com/Metta-AI/sugarscape/tree/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/levy-events-2026-10-15) use fast automation, D=50, seed zero, and 300 steps.
All per-step outputs are byte-identical with and without the observer.
Final inequality, cumulative mortality, tax revenue, and redistribution match the corresponding fresh canonical run.

All 60 observed levy events violate transfer conservation: owners lose 762.5 units, but the treasury receives 180.0583142.
The original code deducts `W * min(1,L/W)` but credits `L * min(1,L/W)`, where W is incoming owner wealth and L the nominal levy.
Equation 4 specifies the same capped amount, `min(L,W)`, deducted and credited.
No observed event reaches the owner-wealth cap in this run; the manuscript's roughly-quarter claim is not supported by this diagnostic.

The [declared correction study](LEVY_DIAGNOSTIC.md) retains a separate accounting patch and specifies a paired 75-run sweep.
Original and bundled source remain unchanged for faithful replay.
The defect establishes a code/specification discrepancy; its impact on policy conclusions remains unmeasured.

## Corrected levy execution check

[The isolated correction](https://github.com/Metta-AI/sugarscape/tree/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/conserving-levy-events-2026-10-15) passes all 60 fast-automation levy events at D=50, seed zero.
Owner deductions total 762.5000000000001 and treasury credits total 762.5, equal within floating-point tolerance.
No event violates the 1e-9 transfer-conservation check.
All 300 per-step outputs are byte-identical with and without the observer.
The source manifest verifies the accounting patch is the only changed source file.

`run_corrected_levy.py ENGINE NEW_OUTPUT` launches the declared original 75-case sweep against this isolated source.
Its complete paired comparison remains pending; the single checked run does not establish robustness of corrected policy outcomes.
The original and forked unmodified experiments continue independently.

## Fresh composition sweep completed

[All 210 alternative-composition runs](https://github.com/Metta-AI/sugarscape/tree/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/composition-2026-10-15) complete successfully with a byte-identical CSV to the pinned author deposit.
Every one of its 5,040 cells matches, including identifiers, ordering, and missingness.
Combined with 105 fresh canonical runs, the independent audit reproduces all 126 printed Table C.1 values.
The previously documented ranking qualifications therefore also hold in fresh execution: two full mortality orderings and seven of nine increasing inequality ranks.
The highest/lowest mortality claim still holds in all nine composition/speed settings.
The native queue has proceeded to the original levy sweep; its later per-seed threshold study and corrected-levy comparisons remain incomplete.

## Fresh figure reconstruction

[Both manuscript figures](https://github.com/Metta-AI/sugarscape/tree/21435a64e27678120fd395c848b1ed7814bf86de/replications/dogan_2026/results/figures-2026-10-15) regenerate from the completed fresh main-sweep CSV using the unchanged author plotting script.
The manuscript references the two deposited PNGs directly.
An independent observer checks all 42 plotted ordinates against five-seed means computed with Python's standard-library CSV and statistics modules.
All values agree within 1e-12, and observing the plot calls leaves both generated PNGs byte-identical to their unobserved versions.

The generated images are not pixel-identical to the deposit: original height is 880 pixels and fresh height is 877, with widths differing by one pixel.
Both original and fresh images are retained; visual inspection finds the same curves, legends, and labels.
This establishes numerical plot reconstruction from fresh simulations, not pixel-exact rendering or validation of the titles' broader claims.
The independently audited Tables 2 and 4 supply the corresponding published numerical targets.

Run `run_figures.py ENGINE COMPLETE_CANONICAL NEW_OUTPUT`, then `audit_figure_series.py FIGURE_OUTPUT NEW_AUDIT`. The [committed figure bundle](https://github.com/Metta-AI/sugarscape/blob/21435a64e27678120fd395c848b1ed7814bf86de/replications/dogan_2026/results/figures-2026-10-15/README.md) now also retains the complete native directory layout, so its audit runs without reconstructing missing input paths.

## Per-seed calibration audit prepared

`audit_perseed.py COMPLETE_ROBUSTNESS COMPLETE_CANONICAL NEW_OUTPUT` checks all 105 per-seed-threshold runs.
It verifies completion, source identity, the full policy/speed/seed grid, finite outputs, death-category accounting, and constant calibration settings within each seed.
It compares every paired result and computes the five-seed means independently of the native analysis scripts.
Rank comparisons retain ties and all pairwise reversals instead of imposing an arbitrary order on equal values.
The report checks the maximum Gini-mean change against the manuscript's printed 0.022 and records whether a sole reversal joins adjacent original ranks.
Both gaps are retained for the manuscript's less-than-0.003 statement.
The actual unfinished queue is correctly rejected; a successful full audit remains pending native completion.
The author repository does not deposit this experiment's output CSV, so no exact deposited-data match is claimed.

## Full bundled replay and remaining native sweeps completed

[Retained complete outputs and audits](https://github.com/Metta-AI/sugarscape/tree/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/completed-sweeps-2026-10-16) cover the bundled canonical run, both 75-case levy sweeps, and the 105-case per-seed calibration study.
The bundled canonical process exits successfully. All four output files are byte-identical to the independent original replay: 206,010 cells match.
This verifies the integrated original-source variant in this fork, not an independently implemented model or equivalence with the DTL engine.

Per-seed calibration preserves all mortality rankings and slow/fast inequality rankings.
Only baseline and Universal High Income exchange adjacent inequality ranks under balanced automation, with gaps below 0.003.
The maximum cell-mean Gini change is 0.0222691, matching the reported 0.022 at three decimals.

All 75 levy pairs pass the declared comparison, including 270 original D=50 values matched against canonical runs.
Under the declared maximum/minimum definition, original fast-automation mortality varies by 6.907%, exceeding the manuscript's less-than-5% claim.
Corrected mortality ranges are 4.946%, 8.443%, and 5.775% for slow, balanced, and fast automation.
At D=200, the corrected fast levy supplies 3.146% of mean redistribution, exceeding the stated 3% bound; the original value is 2.828%.
Both variants retain Gini coefficients of variation below 0.04 across D-level means and equal working counts across D within each seed.
These are descriptive sensitivity results under explicit aggregation choices; full claim interpretation remains required before assigning a paper-level verdict.

## Owner exclusion and population accounting

`audit_owner_exclusion.py SNAPSHOT DECOMPOSITION_AUDIT NEW_OUTPUT` checks the previously validated fresh agent snapshot.
It independently recomputes Gini from pairwise wealth differences after excluding off-grid owners.
[All 105 runs](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/owner-exclusion-2026-10-16/owner-exclusion.json) retain 180 on-grid agents.
Owners number 35, 50, and 80 under slow, balanced, and fast automation; total populations are 215, 230, and 260.
Section 4.2 instead states 200 on-grid agents and totals 235–280.
The simulated counts agree with the stated initial 120/40/20/20 composition, which includes twenty off-grid owners in the initial total.
This is a manuscript counting discrepancy, not evidence of agent loss in the implementation.

Excluding owners preserves the slow-to-fast increase for both pure means-tested policies.
Labor/means-tested Gini rises from 0.266333 to 0.608991, moving from second to sixth among seven policy means.
Wealth/means-tested rises from 0.319608 to 0.657251, moving from fifth to seventh.
Thus owner exclusion preserves deterioration, but wealth/means-tested is not among the lowest-Gini policies under slow automation in this variant.
These descriptive results do not identify the causal contribution of spatial competition.

## Within-type interpretation audit

`audit_within_type.py SNAPSHOT DECOMPOSITION_AUDIT NEW_OUTPUT` reconstructs each agent type's contribution and its separately normalized Gini.
[All 420 type/run records](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/within-type-2026-10-16/within-type.json) reconcile with the previously validated full-population decomposition.
The manuscript's claim that pure means-tested policies reduce within-type contributions at every speed fails in four of six mean comparisons.

| Speed | Baseline within contribution | Labor/means-tested | Wealth/means-tested |
| --- | ---: | ---: | ---: |
| Slow | 0.067764 | 0.043815 | 0.048125 |
| Balanced | 0.060954 | 0.069163 | 0.072393 |
| Fast | 0.061685 | 0.072082 | 0.072742 |

A weighted contribution differs from a type's own Gini; both measures are retained to avoid conflating them.
Fast-automation working-human Gini is also higher: 0.448362 and 0.519557 under the two policies, versus 0.345469 in baseline.
The reported fast-automation shift in the largest within contribution does reproduce: owners in baseline, working humans under either means-tested policy.
The main Table 3 numerical reproduction remains exact. Its prose interpretation overstates within-type equalization.
These comparisons describe the published five-seed outcomes; they do not isolate a causal transfer effect or estimate statistical significance.

## Individual-seed mortality dominance

`audit_mortality_dominance.py CANONICAL ROBUSTNESS NEW_OUTPUT` validates the full grids before comparing paired seeds.
[All 570 available comparisons](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/mortality-dominance-2026-10-16/mortality-dominance.json) show fewer deaths under each pure means-tested policy than its baseline or universal-transfer comparator.
Coverage includes canonical, welfare-specification, initial-composition, per-seed calibration, and 600-step horizon experiments.
The horizon experiment includes only baseline and the two means-tested policies; it cannot establish superiority over untested universal policies at 600 steps.
All observed comparisons are strict, with no ties. They establish robustness over these published conditions, not a significance test or a universal policy theorem.

## Native recurring-tax reach

`audit_tax_reach.py ENGINE COMPLETE_CANONICAL NEW_OUTPUT` repeats the original seed-42 calibration and two full fast-automation seed-zero runs.
It observes native tax calls, verifies every step's total tax accounting, and independently repeats each trajectory without observation.
[Both 300-step trajectories](https://github.com/Metta-AI/sugarscape/blob/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026/results/tax-reach-2026-10-16/tax-reach.json) are byte-identical with and without observation.
Their final Gini, mortality, and tax totals match the fresh canonical runs.

Under labor/means-tested, owners pay 12,130.562880 units across 14,850 positive tax calls.
Under wealth/means-tested, owners pay 35,474.348536 and autonomous agents pay 1,657.743030 units.
All 14,910 autonomous-agent tax calls in the latter run collect positive tax.
The native wealth-tax branch applies to every agent type, and the scheduler invokes it for every living agent each step.
Thus the claim that the tested menu lacks direct recurring taxation of autonomous wealth contradicts the released implementation.
The claim that only the displacement levy reaches the autonomous-owner channel also fails.
This diagnostic establishes implemented tax reach; it does not quantify how much that channel causes any outcome.

The levy-cap claim can also be bounded from the pinned source.
A newly created owner's two endowments each lie in [25,50], giving wealth of at least 50 before the levy.
At D=50 and fast automation, 300 steps permit at most 60 displacement events, making the largest nominal levy 25.
The wealth cap therefore cannot bind in this protocol, consistent with the observed zero capped events.
The manuscript's roughly-quarter assertion cannot be explained by another random seed under these settings.

## Archived raw outputs

[The immutable experiment archive](https://github.com/Metta-AI/sugarscape/tree/82cb45f731d76c985209fac842b857db305320ae/replications/dogan_2026/results) retains raw runs and verbose diagnostics. They remain unchanged in existing local checkouts; summaries, source inputs, and analysis code stay tracked. Restore any required input with `git show 82cb45f731d76c985209fac842b857db305320ae:PATH > /absolute/output/path`, replacing `PATH` with its repository-relative path.

## Archived run records

Primary runners, analysis code, fixed study inputs, source provenance, and study findings remain tracked.
Dated run directories, checkpoint notes, copied runners, and generated source readbacks are preserved in [the experiment archive](https://github.com/Metta-AI/sugarscape/tree/21435a64e27678120fd395c848b1ed7814bf86de/replications/dogan_2026).
Regenerated evidence belongs in the ignored output directories.

Commands and provenance records may reference archived inputs or historical scripts. Restore those dependencies before running the corresponding analysis:

```sh
git restore --source=21435a64e27678120fd395c848b1ed7814bf86de --worktree -- REPOSITORY_PATH
```

Replace `REPOSITORY_PATH` with the required archived file or directory. The restore leaves the index unchanged and the restored evidence ignored. The [original evidence archive](https://github.com/Metta-AI/sugarscape/tree/eaf7d62d991651892e524eda24914c300c1423d7/replications/dogan_2026) retains raw outputs removed in previous cleanups.
