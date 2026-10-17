# Raimbault et al. (2019): Space Matters

Paper: [Space Matters: Extending Sensitivity Analysis to Initial Spatial Conditions in Geosimulation Models](https://www.jasss.org/22/4/10.html).
Scope: Sugarscape results; Schelling experiments are excluded.
Status: **24/24 Table 4 values reproduced from archived data; fixed-reference and generated-landscape ensembles remain unfinished**.
This is not yet a completed paper replication.

## Sources and exact reanalysis

Author code: [JusteRaimbault/SpaceMatters](https://github.com/JusteRaimbault/SpaceMatters),
revision `270cc7f112b3a999b10e02b0f9525038d6d4754d`.
Data: [Harvard Dataverse, doi:10.7910/DVN/9JI57U](https://doi.org/10.7910/DVN/9JI57U), CC0-1.0.
The embedded NetLogo model has a separate CC BY-NC-SA 3.0 notice; the dataset license does not replace it.

The independent Python analysis follows the authors' `distancesToRef` definition:
twice the squared Minkowski distance divided by the sum of sample variances of the two phase diagrams.
Reference Gini values are averaged across replicates before comparison.
Missing grid/parameter combinations are excluded from the paired comparison, as in the released R code;
every exclusion is counted in the result manifest.

All six summaries at each of q=1,2,3,10 match Table 4 at published precision.
The Euclidean mean, median, minimum, and maximum are 1.29594, 1.52272, 0.08909, and 2.98273.
[Full comparisons and coverage](results/archive-2026-10-15/results.json) preserve every grid distance and input hashes.

Run with Python and NumPy 1.26.4:

```sh
python3 replications/raimbault_2019/fetch_sources.py --output /absolute/new/data
python3 replications/raimbault_2019/analyze_archive.py \
  /absolute/new/data/reference.csv /absolute/new/data/generated.csv --output /absolute/new/analysis
```

The downloader verifies immutable file contents against `sources.json`.
The approximately 30 MB source data remain in the chosen directory instead of being duplicated in the Git repository.

## Design details requiring fidelity

The archived reference contains 55,000 simulations: 1,100 parameter combinations with 50 repeats each.
Population takes 11 values (10 through 510 in steps of 50), not the ten bins described in the paper.
The generated-grid archive contains 54,560 aggregated combinations across 50 grids, rather than a complete 55,000.
Thirty-two grids have all 1,100 points; fourteen lack 20 points each, and four lack 40 each.
These facts explain the source dimensions; they do not themselves establish an incorrect substantive conclusion.

The `.source` file for the fixed reference includes an incorrect link to the generated-grid data.
The correct fixed-reference artifact is Dataverse file 3596481, persistent identifier `doi:10.7910/DVN/9JI57U/NIJ2BN`.
Its original CSV format is fetched explicitly.

The NetLogo model replaces dying agents, so population remains fixed while wealth evolves.
The current model averages Gini over the last 1,000 steps; its configured run length is also 1,000.
Historical revisions ran 10,000 steps, so the archive horizon needs verification.
Model setup also draws continuous metabolism and sugar endowments, with integer vision and lifetime.
The released OpenMOLE script requests 100 repeats, whereas the archived reference has 50.
New runs must follow the validated experiment rather than silently using a mismatched current script.

## Fresh simulation pilot and provenance investigation

The first archived reference input completes 1,000 steps with constant population under NetLogo 5.3.1.
Its terminal Gini is 0.3942307692 versus archived 0.2445487365.
Its moving-window Gini is 0.2939769248 versus archived 0.3017667641.
[Trajectory and comparison](results/replay-pilot-2026-10-15/comparison.json) retain this unresolved mismatch.
**This was a horizon mismatch, not a negative replication.** The 10,000-step replay below resolves this input.

The archive filename is dated March 28, 2017; that date does not prove which revision generated its contents.
Commit `b71d1cf73f036749a83335b6a13cabf345599039` added explicit seeding and corrected resource initialization on April 3, 2017.
Commit `74ade6eaa77af4caa65183a2eba6a3ded4708e0f` changed the horizon from 10,000 to 1,000 on September 27, 2018.
The model header identifies NetLogo 5.1.0, while this pilot uses 5.3.1; the original execution runtime remains unverified.
The historical horizon is confirmed for the first input by exact replay; additional input checks remain in progress.

The Java adapter invokes the released setup and records each step without editing the model.
Place `NetLogo.jar` before the wildcard classpath: `NetLogoLite.jar` otherwise shadows full workspace classes in this installation.
The initial compilation failure is preserved with the successful execution log.

```sh
/path/to/jdk/bin/java -Djava.awt.headless=true \
  -cp '/path/to/netlogo/app/NetLogo.jar:/path/to/netlogo/app/*' \
  replications/raimbault_2019/Replay.java \
  /path/to/SpaceMatters/sugarscape/HEADLESS_Sugarscape.nlogo \
  /path/to/reference.csv 0 10000 /absolute/new/trajectory.csv
```

Run from the author model directory, using absolute paths for the adapter and artifacts.
The adapter requires an explicit choice between the two documented horizons, 1,000 and 10,000 steps.
It changes only `total-time-steps` after the released setup and records every simulated tick.

## Historical horizon validated

At 10,000 steps, the first archived input reproduces terminal Gini **0.24454873646209388**
and last-1,000-step mean Gini **0.3017667640537167**, both exactly equal to the archive's recorded NetLogo outputs.
Independent Python recomputation of the window mean differs by 2.22e-16 from NetLogo's summation.
The first 1,000 trajectory rows are identical to the earlier pilot.
[Raw trajectory, execution log, and comparison](results/horizon-validation-2026-10-15) preserve the successful replay.
Thus the initial mismatch is explained by the later horizon change, without changing seed, behavior, parameters, or runtime.
Rows 1 and 54,999 also reproduce both archived NetLogo Gini outputs exactly.
[Additional comparisons](results/horizon-validation-2026-10-15/additional-comparisons.json) include complete trajectories and independently recomputed window means.
These three inputs validate the corrected replay path; they do not complete the spatial ensemble.

## Remaining work

1. Run the original NetLogo 5 model and morphology extension against archived seeds.
2. Validate and implement the study-specific simulation behavior in this fork.
3. Recreate the spatial layouts, reference ensembles, and generated-grid ensembles with declared uncertainty criteria.
4. Reproduce the phase-diagram contrasts and distance summaries from fresh simulations.

Archived-data reanalysis alone does not satisfy these simulation requirements.

## Full fixed-landscape reference replay

`run_reference.py ENGINE NETLOGO JDK REFERENCE_CSV NEW_OUTPUT` runs all 55,000 archived reference inputs at 10,000 steps each.
It pins the author revision and original dataset hash, records model/runtime/dependency hashes, and preserves native exit status.
The adapter flushes each completed row with its seed, population, horizon, terminal Gini, and moving-window Gini.
It checks fixed population at every simulated step and rejects incomplete or nonfinite runs.
Full per-step trajectories remain available from `Replay.java`; the ensemble retains the two native measurements used in the source archive.

The headless setup creates turtles without clearing the previous run.
`BatchReplay.java` explicitly clears the workspace before each original seeded setup, preventing cross-run population contamination.
It does not edit the author model or change the historical 10,000-step rule execution.
[The three-row batch pilot](results/batch-pilot-2026-10-15/comparison.json) completes 30,000 steps and matches all six archived native Gini measurements exactly.
The full 55,000-input replay is now running. Generated-grid ensembles and fresh spatial contrasts remain required afterward.

## Independent reference audit

`audit_reference.py REFERENCE_CSV RUN prefix|complete NEW_OUTPUT` reads the original hashed archive independently of the runner's copied comparison columns.
It checks row order, original seeds, population, full horizon, finite measurements, source hashes, and both native Gini values.
Complete mode requires a successful native exit and every row in the requested interval.
Only an interval covering all 55,000 rows sets `complete_reference` to true.
Prefix mode saves an immutable snapshot and never represents a completed ensemble.

[The first audited prefix](results/reference-prefix-2026-10-15/audit.json) contains 15 simulations and 30 exact native measurement matches.
A deliberately altered copy of one Gini value is rejected with exactly one reported mismatch; this negative control is labeled separately from scientific results.
The full reference continues running. This prefix does not establish parameter-space coverage or the generated-landscape conclusions.

## Interrupted reference recovery

The first full replay stopped without a recorded exit status. Its cause is unknown.
An [independent audit](results/process-recovery-2026-10-16/recovered-audit.json) validates all 2,399 preserved rows: 4,798 exact native Gini matches.
The original directory and partial execution log remain intact.

The runner accepts `--start ROW --stop ROW` with an exclusive stop, using the original archive row indices.
A fresh two-row run spanning the restart boundary reproduces all four archived measurements exactly.
[Its complete interval audit](results/process-recovery-2026-10-16/resume-proof-audit.json) explicitly reports that the full reference remains incomplete.
The continuation starts at row 2,399 and requests the remaining 52,601 rows in a new directory.
The two-row validation overlaps the continuation and must not count as additional ensemble coverage.

## Partitioned continuation

The sequential continuation was deliberately stopped after 847 additional validated rows.
Together, the preserved runs cover original indices `[0,3246)` with 6,492 exact native measurement matches.
The remaining inputs run in five disjoint intervals using the same adapter, seeds, model, and 10,000-step horizon.
Their requested intervals cover `[3246,55000)` without gaps or overlaps.

[Initial independent audits](results/sharded-reference-2026-10-16/coverage.json) validate another 72 rows across all five processes, with zero measurement mismatches.
Total unique audited coverage is 3,318 of 55,000 inputs; gaps remain between these partial shard outputs.
The launch manifest, preserved sequential prefix, and five immutable snapshots retain the partition boundaries and exact evidence.
Neither partitioning nor matching partial outputs completes the paper replication.

## Later shard audit

[The second shard snapshots](results/shard-progress-2026-10-16/coverage.json) validate 2,175 completed simulations across the five processes, with zero mismatches.
Together with the preserved contiguous prefix, unique audited coverage is 5,421 of 55,000 inputs: 10,842 exact native Gini measurements.
These snapshots supersede the earlier shard snapshots for coverage counting; overlapping rows are counted once.
The processes continue. Fixed-reference completion and generated-landscape conclusions remain pending.

## Machine-crash recovery

All five old shard processes were absent after the machine restart. Their complete saved prefixes passed independent audits with zero mismatches.
The original contiguous prefix plus these preserved shard outputs cover 5,773 unique inputs.
Fresh directories resume the remaining original intervals at indices 4,445; 14,077; 24,282; 34,589; and 44,874.
No saved completed row is rerun or dropped. Seeds, adapter, model, horizon, and memory limits are unchanged.

[Initial resumed-prefix audits](results/crash-recovery-2026-10-16/coverage.json) add 13 exact matches across all five workers.
Total unique audited coverage is 5,786 inputs and 11,572 native Gini measurements, with zero mismatches.
Immutable saved and resumed snapshots, their checksums, and launch commands are retained. The full reference and generated-landscape studies remain incomplete.

## Resumed-prefix validation

[Five fresh snapshots](results/resumed-prefix-2026-10-16/coverage.json) independently validate 193 resumed inputs, including 180 beyond the recovery snapshot.
Both Gini measurements match exactly for every input.
Replacing the earlier overlapping prefixes gives 5,966 unique validated inputs and 11,932 exact measurements.
Compressed native snapshots, hashes, and disjoint interval accounting are retained.
All five workers remain active; the full 55,000-input reference and generated-landscape study remain incomplete.

## Linux portability and bounded CPU handoff

[Three full-horizon portability probes](results/linux-parity-2026-10-16/comparison.json) reproduce rows 0, 1, and 54,999 on Ubuntu 22.04 with Java 11.0.32.1.
All six native Gini values match the archive exactly; result CSVs are byte-identical to the macOS package proof.
The downloaded archive was checksum-verified and compared independently against the original reference CSV.
These repeated validation rows add **zero** unique ensemble coverage.

The first packaging attempt omitted three nested `.nls` files and failed before simulation.
Recursively including those unchanged author sources fixes packaging; model rules and parameters remain unchanged.
The retained Linux artifact includes manifests, dependency hashes, source hashes, raw results, native logs, and complete interval audits.
Probe timings are retained for capacity planning, but concurrent machine workloads prevent a controlled speed comparison.

After parity passed, the owned local fifth shard was deliberately terminated and its exit confirmed.
Its 142 completed rows, `[44874,45016)`, passed an independent audit with 284 exact measurements.
Local execution resumes `[45016,54600)` in a new directory.
Eight remote workers receive disjoint 50-row intervals covering `[54600,55000)`.
[The handoff record](results/linux-parity-2026-10-16/handoff-confirmed.json) preserves the terminal checkpoint and commands.
The remote batch is bounded to one hour and stops its CPU node afterward; its results remain pending and uncounted here.
The full reference, generated landscapes, and paper replication remain incomplete.

## Generated-landscape source and executable replay

The [original per-run archive](https://dataverse.harvard.edu/api/access/datafile/3596486?format=original)
contains 1,180,976,826 bytes and matches Dataverse's MD5 `7b554774a9d293b2c2ce3169c9d48dbe`.
Its SHA-256 is `1a2cdf93167571ab2943d488017ace08945e7afd3cd8ac4d1410fb214c79c8f5`.
The source remains outside Git, compressed losslessly; replay verifies the decompressed hash before execution.

[Full archive reconstruction](results/generated-source-2026-10-16/raw-audit.json) verifies **2,727,994 runs** across 54,560 parameter groups and 50 landscape parameter sets.
There are 54,554 groups with 50 repeats and [six groups with 49](results/generated-source-2026-10-16/underfilled-groups.json).
No group repeats a seed. All rows request generated landscapes (`setup=1`).
All 54,560 reconstructed moving-window Gini means agree with the released aggregate within 8.33e-16.
The five averaged generator parameters agree within 1.01e-11; the audit's explicit aggregate tolerance is 1e-10.
This validates the provenance of the aggregate used for Table 4, without substituting reanalysis for simulation.

The author model seeds its random generator before generating each landscape and creating agents.
Therefore, a landscape parameter set identifies a family of seeded maps, not one map reused for every repeat.
The replay preserves every recorded seed and regenerates the corresponding map before running the original agent rules.

`GeneratedReplay.java` streams the gzip archive instead of retaining its 2.7 million rows in memory.
`run_generated.py` pins the model revision, source/dependency hashes, full raw archive, interval, Java version, and exit status.
It records both Gini metrics and all ten native spatial morphology outputs at the validated 10,000-step horizon.
The existing fixed-reference runner and its live simulations are unchanged.

```sh
python3 replications/raimbault_2019/audit_generated_archive.py \
  /absolute/generated-raw.csv.gz /absolute/generated.csv /absolute/new/archive-audit
python3 replications/raimbault_2019/run_generated.py \
  /absolute/SpaceMatters /absolute/netlogo /absolute/jdk \
  /absolute/generated-raw.csv.gz /absolute/new/generated-pilot --start 0 --stop 2
```

The first command reconstructs the published aggregate; `generated.csv` is the aggregate from `fetch_sources.py`.
The second command runs the original model through the public runner; row intervals use exclusive stops.

[The two-row generated-landscape pilot](results/generated-source-2026-10-16/pilot-comparison.json) completes 20,000 simulated steps with native exit zero.
Both Gini outputs match exactly for both rows. Across all 24 output values, 23 match exactly.
Row 1's population-distribution R² is `0.8963279972950365`, versus archived `0.8963279972950364`: one floating-point step.
The strict exact comparison fails on that value; its discrepancy is retained, with no relaxed pass criterion.
A repeated execution through the public runner produces byte-identical output.
These validation probes add zero unique ensemble coverage. The full generated ensemble and fresh spatial conclusions remain pending.

## Generated-landscape diversity probes

[Six input-selected probes](results/generated-diversity-2026-10-16/summary.json) cover landscape parameter sets 16 and 23 at populations 10, 260, and 510.
Selection took the first recorded input in each category without consulting output values.
Five inputs are new probes; original row 0 is a repeated control. These probes add zero production-ensemble coverage.
Every run preserves its archived seed, full 10,000-step horizon, native model, and terminal status.

Both Gini measures match exactly for all six inputs. Of 72 output values, 66 match bit-for-bit.
The six deviations occur in regression slope or R², with maximum absolute error 4.44e-16.
Before these runs, the campaign declared exact Gini matching and a 1e-12 absolute tolerance for morphology outputs.
That tolerance was chosen after the initial exploratory discrepancy; it does not change the earlier strict-exact failure.
Every deviation and the original strict comparison remain available in the evidence.

Bytecode inspection traces the regression to the unchanged extension's Apache Commons Math `SimpleRegression` methods.
This identifies the implementation being executed; it does not establish the exact historical cause of floating-point differences.
An independent pass through the original archive verifies all six selected indices and all 72 output comparisons.
The full generated-landscape ensemble and spatial conclusions remain incomplete.

## Remote reference validation and complete checkpoint handoff

[The first remote production batch](results/remote-reference-2026-10-16/batch-400-independent-validation.json) completes original rows `[54600,55000)`.
All 400 runs finish 10,000 steps, and all 800 native Gini measurements match the original archive exactly.
Downloaded evidence verifies successful native exits, row identities, source/dependency hashes, interval completeness, and independent output comparisons.
The node stops automatically after the batch; its files remain intact and were retrieved for the audit.

After that audit, the five owned local reference workers were deliberately stopped and their terminal states verified.
[The consolidated checkpoint](results/remote-reference-2026-10-16/handoff-confirmed.json) independently validates **7,933 unique runs and 15,866 exact Gini measurements**.
Original files remain intact. The retained checkpoint snapshots include all covered rows, manifests, logs, and available terminal records.
Earlier overlapping snapshots and validation probes are excluded; the remote 400-row interval is counted once.

The remaining **47,067 original rows** are assigned to 473 disjoint intervals of at most 100 rows on eight CPU workers.
The queue validates the frozen runtime bundle before execution and audits each completed interval against the original reference.
A native or audit failure prevents pending intervals from starting; already-running intervals preserve their outputs.
The launch wrapper enforces a 24-hour limit, preserves evidence, and stops the task-owned node afterward.
A two-interval native queue proof passed before this handoff; its raw results and audits are retained with the plan.
The production queue is running, so its unfinished outputs are not included in the checkpoint count.

The full 55,000-row reference, generated-landscape ensemble, and paper replication remain incomplete.

## First running-queue checkpoint

[Independent validation](results/remote-reference-checkpoint-2026-10-16/checkpoint-002-independent-validation.json) checks 14 completed chunks covering `[5120,6520)`.
All 1,400 runs finish 10,000 steps; all 2,800 Gini measurements match the original reference exactly.
The downloaded archive retains native outputs, successful exits, manifests, and per-chunk audits.
Independent checks verify original seeds, populations, row identities, source/dependency hashes, and complete disjoint intervals.
These intervals belong to the reserved production plan and do not overlap the earlier 7,933-row checkpoint.
Combined validated coverage is **9,333 of 55,000 reference runs**; unfinished chunks are excluded.
This remains partial reference evidence, not completion of the paper replication.

## Audit fresh generated intervals

`audit_generated.py` checks fresh output against the full, hash-pinned original raw archive.
It verifies source/dependency hashes, requested bounds, original identifiers/seeds/populations, the horizon, and all 12 measurements.
Complete mode requires a successful native exit and every requested row; prefix mode labels partial coverage explicitly.
The audit preserves an immutable output snapshot and records every non-exact measurement, including differences within tolerance.
Gini comparisons always require exact equality. The morphology tolerance must be supplied explicitly and cannot exceed `1e-12`.

```sh
python3 replications/raimbault_2019/audit_generated.py \
  /absolute/generated-raw.csv.gz /absolute/native-run complete /absolute/new/audit \
  --morphology-absolute-tolerance 1e-12
```

[Real two-row workflow evidence](results/generated-auditor-2026-10-16/validation.json) exercises the existing public-runner pilot.
Strict zero tolerance fails on its known R-squared difference; the previously declared `1e-12` morphology tolerance passes.
Both reports retain 23 exact comparisons out of 24, with both Gini metrics exact for each input.
This verifies the audit workflow and adds no simulation coverage or completed-paper claim.

## Linux generated-landscape portability

[Independent downloaded-artifact validation](results/generated-linux-2026-10-16/independent-validation.json) checks all six previously selected probes on the task-owned Linux CPU node.
All three sequential two-row native processes exit successfully, completing the original 10,000-step horizon.
Frozen model, extension, dependency, adapter, input, and criteria hashes are verified before comparing outputs.

**All 72 Linux measurements match the original archive exactly**, including both Gini outputs and all ten morphology outputs for every input.
Linux and macOS agree exactly on 66 of 72 measurements; six regression outputs differ by at most `4.440892098500626e-16`.
Every cross-platform difference remains within the previously declared `1e-12` morphology tolerance; Gini comparisons remain exact.
The original macOS strict-exact failure is preserved and is not relabeled as an exact match.
These observations narrow the numerical discrepancy to differences between the tested runtime environments; they do not isolate OS, architecture, or JDK effects.

The three pairs took 93.41, 318.77, and 457.18 seconds on one low-priority worker sharing the eight-core reference node.
These selected probes are not a representative throughput sample for the 2,727,994-row generated ensemble.
The full generated ensemble and fresh spatial comparisons remain unstarted; these repeated probes add no production coverage.

## Stratified generated-ensemble sizing run

[Input selection](results/generated-sizing-launch-2026-10-16/selection.json) fixes one original input for each of 50 landscape IDs and 11 population levels.
Reservoir sampling uses seed `20261016`, independently within each stratum, before executing the selected runs.
A second full-archive pass verifies every selected field, all original indices, and the stratum counts summing to 2,727,994 runs.
Original stratum sizes will weight timing estimates; an early prefix cannot substitute for the complete sample.

A separate eight-core CPU node runs the 550 selected inputs with a six-hour limit, captures evidence, and stops automatically afterward.
Each native process retains wall time, CPU time, peak memory, commands, outputs, exit status, and all twelve output comparisons.
Native or measurement failures stop pending work; already-running outputs remain intact.
This benchmark leaves the existing fixed-reference queue unchanged.

[Downloaded initial evidence](results/generated-sizing-launch-2026-10-16/prefix-independent-validation.json) independently verifies eight completed inputs and 96 exact archived measurements.
These early inputs establish execution, not a representative cost estimate or completion of the generated ensemble.
The initial snapshot was partial; the complete sizing audit below supersedes it. No full generated-production queue has been launched.

### Independent sizing audit and projection gate

`analyze_sizing.py` validates the frozen input selection, completed native outputs, timings, and output hashes independently of the producer's audit verdicts.
The [223-input snapshot](results/generated-sizing-audit-2026-10-16/analysis.json) matches all 2,676 archived measurements exactly.
This snapshot includes the eight initially reported inputs; the counts are not additive.
Running `--require-complete` against this real snapshot fails before creating output, because 327 selected strata remain absent.

The analyzer emits a projection only when all 550 selected strata have valid results.
It weights CPU time and elapsed time by original stratum size, then reports an ideal eight-CPU estimate and an eight-worker elapsed-time estimate.
A supplied hourly price is an assumption, not a live quote or guaranteed budget.
Both estimates retain per-input Java startup costs and exclude setup, retries, transfer, and idle time.
One sampled input per stratum does not estimate within-stratum timing variance; no confidence interval is claimed.
The complete projection path is now exercised by the full sizing audit below.

```bash
python replications/raimbault_2019/analyze_sizing.py /downloaded/sizing-run /new/sizing-analysis --hourly-node-price 0.4824 --require-complete
```

### Second remote reference checkpoint

The [sealed checkpoint audit](results/remote-reference-checkpoint-2026-10-16/checkpoint-003-independent-validation.json) verifies 53 completed chunks, containing 5,300 original inputs.
All 53 recorded source and dependency files match the frozen local runtime.
Combining these chunks with the 7,933-row local baseline yields 13,233 unique simulations and 26,466 exact archived Gini comparisons.
The earlier 1,400-row cloud snapshot is contained in this checkpoint and is not added again.
The native archive and independent validation script are retained beside the report.
The 55,000-row reference ensemble remains incomplete; this checkpoint makes no generated-landscape or whole-paper replication claim.

### Third remote reference checkpoint

The [71-chunk audit](results/remote-reference-checkpoint-2026-10-16/checkpoint-004-independent-validation.json) verifies7,100 remote inputs against the original reference archive.
Together with7,933 frozen local inputs, coverage reaches15,033 unique simulations and30,066 exact Gini comparisons.
All53 source/dependency hashes match the frozen runtime; every sealed chunk exits successfully and completes its declared interval.
This adds1,800 rows beyond checkpoint003; previous cloud checkpoints are contained here and are not added again.
The55,000-row reference ensemble remains incomplete, and generated landscapes and fresh spatial comparisons remain separate requirements.

### Complete generated-landscape sizing sample

The [complete audit](results/generated-sizing-complete-2026-10-16/analysis.json) validates all 550 selected inputs and 6,600 exact archived measurements.
The retained native archive includes timings, outputs, commands, and frozen selection for independent replay of this audit.
This supersedes the 223-input snapshot; their counts are not additive.

Stratum-weighted timing projects 19,831.91 CPU-hours, or 2,494.73 elapsed hours on one eight-worker node, for all 2,727,994 inputs.
At an assumed $0.4824 per node-hour, the elapsed projection costs $1,203.46.
This includes per-input Java startup and excludes setup, retries, transfer, and idle time.
One observation per stratum provides no within-stratum variance estimate or confidence interval; this is not a guaranteed budget.
The full generated ensemble remains unstarted. Benchmarking repeated inputs within one Java process is a possible next efficiency check, subject to exact-output validation.

### Bounded batched sizing benchmark

The [frozen bootstrap package](results/batched-sizing-launch-2026-10-17/plan.json) partitions the same 550 selected inputs across eight native Java processes.
`GeneratedReplay.java` is unchanged: each input resets the model and its original random seed within a reused workspace.
All 6,600 outputs must match their archived measurements exactly before a successful result is reported.
The simulation limit is one hour; bootstrap setup and execution are bounded separately.
Official NetLogo and Commons Math downloads match the pinned runtime hashes, and every packaged member passes byte-for-byte readback.
The queued-node end-to-end bootstrap remains unverified until it executes.
This measures sample throughput; batch-level timing does not identify per-stratum CPU costs, so it cannot alone replace the weighted full-ensemble cost projection.

### Fourth remote reference checkpoint

[Independent validation](results/remote-reference-checkpoint-2026-10-16/checkpoint-005-independent-validation.json) checks 197 sealed chunks containing 19,594 remote inputs.
Combined with the retained 7,933 local inputs, coverage is **27,527/55,000 unique simulations**, with 55,054 exact Gini comparisons.
All 53 source and dependency files match their pinned hashes.
Earlier remote checkpoints are contained in this snapshot and are not added again.

The complete 1,506,165-byte checkpoint archive is retained in this PR.
Its SHA-256 is `8847b24c02ded37e190060ccf2d681c901de94c0a163642a0756cde65cbe30bc`.
The native worker remains active; incomplete chunks were excluded from the export.
This checkpoint protects completed evidence after a different provider host failed.
Generated landscapes, fresh spatial comparisons and paper-level replication remain incomplete.

```sh
python replications/raimbault_2019/results/remote-reference-checkpoint-2026-10-16/validate_checkpoint_005.py \
  /path/to/remote-reference-queue-001 /new/checkpoint-validation.json
```

The evidence root includes the retained local baseline, extracted checkpoint and production plan.
The pinned runtime files remain in its sibling `remote-cpu-pilot-001/local-package-proof-002` directory.

### Fifth remote reference checkpoint

[Independent validation](results/remote-reference-checkpoint-2026-10-16/checkpoint-006-independent-validation.json)
checks 287 sealed chunks containing 28,556 remote inputs. Together with the retained
7,933 local inputs, coverage is **36,489/55,000 unique simulations**, with **72,978
exact Gini comparisons**. All 53 pinned source and runtime files match.

This adds 8,962 unique simulations and 17,924 exact metric comparisons. Every prior
checkpoint-five chunk's results, manifest, and independent audit remains byte-identical
in this snapshot: 591 files checked. Earlier checkpoints are contained, not added again.

The 2,192,693-byte archive retains completed chunks only. Its export exited successfully;
the eight-worker simulation queue continues. The remaining reference inputs and generated
landscape ensembles still prevent a whole-paper replication verdict.

```sh
python replications/raimbault_2019/results/remote-reference-checkpoint-2026-10-16/validate_checkpoint_006.py \
  /path/to/remote-reference-queue-001 /new/checkpoint-validation.json
```
