# Richmond et al. (2023): FLAME GPU 2 Sugarscape

Status: **incomplete; full native grid audited, model fidelity under investigation**.
No completed-study credit. This study adds to the existing replication program.
[Complete native benchmark](results/full-native-complete-2026-10-18): **84/84 conditions**; all **6,600 population records** and **162 resolution rows** match the author archive exactly.
[The complete state audit](results/state-observer-complete-2026-10-18) reconciles 893,017 observations after resolving a cross-toolchain initializer mismatch.
It confirms lost wealth/metabolism transfers and unresolved agents omitted from reported population.

Paper: [FLAME GPU 2: A framework for flexible and performant agent based simulation on GPUs](https://doi.org/10.1002/spe.3207).
Scope: the complete Sugarscape case study, Section 4.3 and Figures 6/11.
The paper's separate Boids experiments are outside this Sugarscape study.

## Pinned sources

The paper explicitly links the [benchmark v1 release](https://github.com/FLAMEGPU/FLAMEGPU2-submodel-benchmark/releases/tag/v1).
Its annotated tag object is `89eff8e11f28d20533b69b274be088f0a7045933`;
the peeled source commit is `290702073492677f2fc9164419e9d5900d119e02`.
The benchmark selects engine tag `v2.0.0-rc`, whose peeled commit is
`19136c18629af0a52ac4355ff705596b22bedac1`.
Keep the benchmark and engine in separate pinned checkouts; no simulation source
is copied or modified in this study directory.

The published release retains raw data, plotting scripts, figures, and machine notes.
Use `sample/data/v100-515.65.01/2.0.0-rc-v100-11.0-beltsoff` for Figure 11.
Older V100 and A100 directories represent different experiment versions.
The machine notes name a V100-SXM2-32GB, CUDA 11.0, and GCC 9.3.0, but list an
older driver than this data directory. Record that provenance difference explicitly.

## Archived numerical audit

[The audit](results/archive-2026-10-17/audit.json) checks every expected condition and
step, unique keys, finite timings, population bounds, and all native aggregate means:

| Experiment | Conditions | Per-condition observations |
| --- | ---: | ---: |
| Scaling, widths 256 through 4096 in increments of 256 | 48 | 100 steps |
| Occupation, six densities at width 512 | 18 | 100 steps |
| Conflict resolution, six densities at width 512 | 18 | Nine stored bins |

All 6,600 step records reconcile with 132 population/timing means.
The comparison bounds account for independent decimal rounding of each native CSV
value and aggregate; population observations are exact integers. No statistical
acceptance threshold or published effect criterion is inferred from these errors.
All 162 resolution rows have unique expected keys and valid bounds.
Raw inputs remain in the pinned author repository; their hashes are retained.

```sh
python replications/richmond_2023/audit_archive.py PINNED_BENCHMARK NEW_OUTPUT
```

This reproduces archived aggregation only. It does not rerun a simulation, verify
historical plot pixels, or establish a fresh performance result.

## Source discrepancies to preserve and investigate

- The README describes widths 64–4096 at increments of 64. The actual benchmark
  and selected data use 256–4096 at increments of 256.
- `MovementExitCondition` increments its counter before writing to
  `step_unresolved_count[counter]`. Index zero remains zero, but CSV labels start
  at one. Thus the first reported bin is an unused zero; the second records
  unresolved agents after the first resolution iteration.
- The counter writes only while its value is below nine. The ninth iteration
  is not measured before forced exit. Its successful conflict resolution cannot
  be inferred from the stored histogram alone.
- Resolution sums use unsigned integers and divide by three in place. Fractional
  mean unresolved counts are truncated before the plotting script divides by
  mean population. The archived audit does not recover the omitted fractions.
- Source maxima are metabolism four and sugar capacity four. The paper's prose
  lists metabolism five and gives inconsistent sugar maxima. Preserve source
  behavior in the native replay; label any alternative configuration separately.

These findings identify measurement and specification questions. They are not a
negative paper verdict. Fresh state observations must establish collision freedom,
resolution completion, and the consequences of these differences.

## Required native replication

Run the complete original 84-condition experiment: seeds 0–2; 48 scaling and
18 occupation conditions at 100 steps; 18 resolution conditions at three steps.
Freeze engine/source hashes, compiler/CUDA versions, GPU identity, clocks, build
flags, runtime environment, and raw outputs. Preserve original seatbelts-off
benchmark timing; run additional instrumented state checks separately.

Recompute Figure 11A population means, Figure 11B resolution summaries, and
Figure 11C scaling from all native records. Retain original and corrected bin
interpretations separately. Reconstruct the three visualisation states for
Figure 11D–F and audit the movement dependency graph against Figure 6.

Before performance interpretation, specify hardware comparisons and seed-level
uncertainty. Historical absolute seconds are not portable acceptance criteria.
A bounded toolchain and full-workflow qualification precedes the complete benchmark;
shortened runs receive no full-study credit. Existing study ensembles remain unchanged.

## Bounded GPU qualification

[The frozen launch](results/native-qualification-launch-2026-10-17) uses one H100,
CUDA 11.8.0, architecture 90, and the pinned benchmark/engine sources without edits.
The engine's own architecture configuration explicitly supports CUDA 11.8/Hopper.
[NVIDIA's compatibility guide](https://docs.nvidia.com/cuda/archive/12.8.0/hopper-compatibility-guide/index.html)
confirms that CUDA 11.8 supports native Hopper kernels. This differs from the
published V100/CUDA 11.0 environment and cannot recover its absolute timings.

Command `cmd-yjge7` started October 17, 2026, at 21:08:52 UTC. The 92-minute
provider limit bounds cost to $6.1824 at the quoted $0.0672/minute, excluding idle time.
An inner timeout bounds native execution to 600 seconds after configuration/build.
It invokes the unchanged complete benchmark; any prefix left at the timeout is
qualification evidence only. A timeout is retained as exit 124, not relabeled success.

The launch records all 522 tracked source-file hashes, toolchain/GPU details, build
logs, binary hash, and raw CSV/log outputs. Source modifications cause failure.
A bounded collector exports terminal evidence to task-owned storage, capped at
100 MiB; exported data still require download and independent hash verification.
The initial launch claimed no build or native result. The first successful native
population comparison is documented below; no performance verdict is assigned.

The remote source manifest now matches an independently reconstructed local
manifest byte-for-byte by SHA-256, covering all 522 tracked files. A failed file
export and a truncated read response remain recorded; neither triggered a model
restart. The complete manifest and verification receipt are retained with the launch.

## First native population comparison

The pinned benchmark built and executed on the H100. An immutable snapshot covers
seven complete scaling conditions: seed zero, widths 256–1792, and all 100 steps
per condition. [All 700 native population observations](results/population-prefix-2026-10-17/population-local-audit.json)
match the published V100 archive exactly. Timings are excluded from this comparison.

The 49,143-byte snapshot archive was downloaded and SHA-256 verified. A separate
local auditor checks the complete reference grid, exact prefix keys, population
bounds, both input hashes, and every population difference. Its report matches
the native comparison. Raw native/reference CSVs and the command receipt are retained.

```sh
python replications/richmond_2023/compare_population.py EXTRACTED_SNAPSHOT NEW_AUDIT.json
```

This establishes population replay for seven of 48 scaling conditions only.
It does not validate individual state, the other conditions, resolution statistics,
visualisation, scaling claims, or the whole paper. The bounded native run continues.

## Resolution-counter lifecycle investigation

The global `exit_condition_iterations` increments in `MovementExitCondition`.
The histogram loop resets it before each timestep; the scaling and occupation
loops reset only `occupied`. The reset inside the exit condition is commented out.
The continuation check requires the counter to remain below nine. Therefore
condition splitting cannot assume a fresh host counter reproduces the original
sequential experiment. No split continuation is launched on that assumption.

[A separately frozen observer](results/resolution-observer-launch-2026-10-17) logs
the counter immediately before and after each step, then returns after the first
complete 100-step, seed-zero, width-256 condition. It changes no model rule or
random draw. All 100 population observations must match the unmodified prefix
before interpreting the counter trace. Instrumented timings remain excluded.

Command `cmd-k4iae` waits for the original qualification's terminal receipt before
building or simulating. Its total bound is 1,800 seconds including the wait; native
execution is limited to 120 seconds. The original source checkout remains intact
and the observer uses a separate worktree. At the quoted rate, the command's bound
is $2.016, excluding idle time and overlapping wait time already billed to the
qualification run. No diagnostic outcome is yet claimed.

`instrument_resolution.py ORIGINAL_MAIN NEW_OUTPUT` produces the exact observer,
patch, and protocol after checking the original source hash. The published launch
passed shell syntax and Python lint checks; native parity remains to be measured.

## Sealed qualification outcome

The original native command ended with its declared timeout, exit 124, at
21:20:23 UTC. [The complete qualification evidence](results/native-qualification-complete-2026-10-17)
contains ten completed scaling conditions, seed zero at widths 256–2560.
The width-2816 condition started but produced no recorded timestep before timeout.
It is retained as unfinished and receives no completed-condition credit.

All 1,000 native step records pass the independent receipt, source-manifest,
coverage, finite-timing, population-bound, and aggregate-reconstruction audit.
Every recorded population matches the author archive exactly. This covers ten
of 84 total conditions; occupation and resolution grids remain unexecuted.
No timing-equivalence, individual-state, or whole-paper verdict follows.

The 51,504-byte terminal archive was downloaded from task-owned storage and
verified against SHA-256 `51e69cbd7de87c97b349d8e3137896da3c3071fb695baa5f7fba7e0ca5d8ed31`.
It retains raw outputs, GPU/toolchain details, build logs, the source manifest,
execution exit code, and the native receipt. The public auditor preserves the
failed completion status rather than converting operational timeout to success.

```sh
python replications/richmond_2023/audit_native.py EXTRACTED_EVIDENCE NEW_AUDIT
```

The passive counter observer started building only after this command's terminal
receipt appeared. Its population-parity and counter results remain pending.

## Counter trace confirmed with population parity

[The complete native diagnostic](results/resolution-observer-complete-2026-10-17/audit.json)
exited successfully. All 100 population observations exactly match the unmodified
qualification. The counter persists without reset through all 100 steps and ends
at 106. Starting at step 3, its value is already at least nine; each of the remaining
97 steps executes exactly one resolution iteration.

This confirms the counter behavior in the released scaling experiment. It does
not demonstrate that every remaining movement conflict is resolved in one pass.
No counter correction or whole-paper negative verdict is assigned.
The downloaded 11,934-byte archive retains the observer source, native logs and
outputs, patch, build logs, and exit code. Its hash and independent audit are retained.

```sh
python replications/richmond_2023/audit_resolution.py EXTRACTED_OBSERVER UNMODIFIED_PREFIX NEW_AUDIT
```

## Full unchanged native benchmark

[The frozen full-run protocol](results/full-native-launch-2026-10-17/protocol.json)
runs all 84 original conditions in one process, preserving the native counter
lifecycle. It reuses the verified unmodified executable and checks its hash before
execution. The prior qualification and observer remain separate evidence and are
excluded from this ensemble's coverage.

Command `cmd-8h5jk` has a six-hour outer limit and a 21,300-second native limit.
At the quoted rate, six hours costs at most $24.192, excluding final idle time.
The terminal evidence collector is capped at 100 MiB. Population/resolution values
match the archive exactly; timing comparisons remain descriptive across
different hardware. No acceptance margin is selected after observing differences.
Operational completion alone will not establish full coverage or paper replication.

## Agent-state fidelity: pinned-source findings

The [source audit](results/model-rule-source-audit-2026-10-17/audit.json) identifies
additional rule differences in the exact paper-linked revision. The subsequent
[complete native state audit](results/state-observer-complete-2026-10-18) validates transfer defects and diagonal movement.

The most consequential finding is in `movement_response` (lines 145–180).
The winning request updates its ID and priority, but never copies sugar or metabolism
from the incoming message. Both local values start at `-1`. Successful movement therefore
stores metabolism `-1` and sugar equal to destination sugar minus one. The request carries
the original values, but this handler does not read them. Exact population replay does
not establish preservation of these agent attributes.

The movement search uses the pinned engine's eight-neighbor `wrap(x,y)` iterator,
including diagonals. Section 4.3 describes four cardinal directions. The engine also
provides `vn_wrap`, which this benchmark does not use. Separately, death checks equality
to zero; the paper describes removing agents with nonpositive wealth. Negative wealth
occurs after movement in the native capture; no negative-wealth-after-metabolism survivors were observed.

Hotspot separation uses toroidal distance, whereas sugar influence uses direct coordinates.
The paper's distance norm leaves boundary interpretation insufficiently explicit, so this
is a specification question rather than an established contradiction.

After the full original benchmark finishes, a separate passive state observer must inspect
agent IDs, metabolism, wealth, and movement. Its population trace must match all 100
unmodified qualification observations before interpretation. Observer timings cannot count
as benchmark timings. No source correction is applied to the ongoing historical replay.

### Deferred passive state observer

[The frozen observer launch](results/state-observer-launch-2026-10-17) records the
initial state and all 100 post-step active-agent states for seed zero, width 256.
Command `cmd-trijm` waits for the full benchmark's terminal receipt before building
or executing. Its post-wait limit is 30 minutes, including a five-minute native limit.
At the node's quoted rate, the added execution is bounded by $2.016, excluding idle time.
The bounded wait overlaps the existing full run; it launches no concurrent GPU work.

The observer uses the engine's population download API and changes no rule or random draw.
It records IDs, positions, statuses, sugar, metabolism, and local resource values.
A subtle measurement distinction is retained: original CSV population counts only
status `OCCUPIED`, whereas the observer also records unresolved agents.
Parity must compare the same status subset; total active population is a separate statistic.
The job completed successfully; [state findings and the corrected initializer control](results/state-observer-complete-2026-10-18) are now audited.
The storage collector is capped at 100 MiB.

## Figure 6 dependency-structure comparison

[The pinned-source comparison](results/figure6-structure-2026-10-17/audit.json)
checks Figure 6 on printed page 11, physical PDF page 12, by visual inspection and source extraction.
The parent model orders metabolism/growback before the movement submodel.
Its four submodel layers match the diagram: output cell status, request movement, respond to requests, then transact movement.
All six message input/output links across the three named channels match the diagram.
The agent mapping and registered exit condition are retained with source locations and hashes.

This establishes structural correspondence only. The exit predicate increments a global counter and tests unresolved agents only below nine.
At nine or above it returns without testing whether unresolved agents remain.
The existing passive trace establishes counter carryover; the completed state observer records 3,065 unresolved agents at the final step.
The figure caption's all-resolved guarantee is therefore not established by a matching dependency graph.

The complete study also still requires native Figure 11A–C comparisons and Figure 11D–F visual states.
The queued observer records active agents only; it does not retain the full unoccupied-cell landscape needed for Figure 11D.
Full-landscape capture or independently verified reconstruction remains necessary, along with the declared movement/state checks.
A completed 84-condition timing grid alone will not complete this study.

## Extracted host initialization for the full landscape

[The standalone initialization evidence](results/initial-state-extraction-2026-10-17)
contains all 65,536 cells for seed zero and width 256, including 11,025 occupied agents.
`prepare_initial_state.py PINNED_MAIN_CU NEW_OUTPUT` extracts the original hotspot-spacing helper,
constants, random draws, loop order and landscape arithmetic; engine storage writes become local integers and CSV output.
No simulation step or GPU engine is replaced by this extraction.
GNU C++ 16.2.0 builds the extracted host program without warnings on this Mac.
The compiler/library differs from the GPU benchmark, so native-state parity remains unverified.

`audit_initial_state.py STATE_CSV HOTSPOT_LOG NEW_OUTPUT` checks every cell position,
initial agent identifier, wealth/metabolism bound and empty-cell record.
It independently reconstructs the landscape from 54 retained hotspot coordinates using NumPy.
All 65,536 capacity values match exactly; minimum wrapped hotspot separation is 20 cells.
Hotspot spacing wraps, while the source's resource-distance calculation does not; both behaviors are preserved.
Adding coordinate logging leaves the entire state CSV byte-identical to the first extracted execution.

The rendered landscape and complete compressed state table are retained, with compiler, source, binary and data hashes.
This prepares the missing full-landscape evidence. It does not yet establish Figure 11D parity:
compare its occupied initial records against the pending unmodified-engine state capture before accepting that interpretation.
The first and fiftieth simulation states and remaining paper claims are still outstanding.

```sh
python replications/richmond_2023/prepare_initial_state.py \
  /path/to/pinned-benchmark/src/main.cu /new/extracted
# Run inside a new evidence directory; retain the exact compiler version.
g++-16 -std=c++17 -O2 -Wall -Wextra /new/extracted/initial.cpp -o initial
./initial > state.csv 2> hotspots.log
python replications/richmond_2023/audit_initial_state.py state.csv hotspots.log /new/audit
```

## Released initial image: compiler-sensitive reproduction

[The image comparison](results/initial-image-comparison-2026-10-17/image-comparison.json)
matches all 65,536 initial landscape cell color classes using Apple Clang/libc++.
The same extracted source and seed under GNU C++/libstdc++ matches 13,579 classes.
Both host reconstructions pass the independent capacity audit; their occupied counts differ: 11,171 versus 11,025.
This demonstrates runtime-sensitive initialization without changing the model, seed, or random-draw order.

`compare_initial_image.py IMAGE GNU_CSV CLANG_CSV NEW_JSON` samples the released image at cell centers.
It normalizes RGB intensity and selects the closest of five Viridis classes, using the original coordinate orientation.
No crop, seed, palette, or model parameter is fitted.
The original image entered the repository in February 2022.
The January 2023 benchmark update retains a byte-identical host initialization body; hashes and commit IDs are preserved in `provenance.json`.
Compiler output, dynamic library identities, complete compressed Clang states, hotspot coordinates, and independent audit accompany the comparison.

This reproduces the initial landscape's categorical appearance, not every rendered pixel or the historical compiler identity.
It does not establish occupied-agent image parity, GPU-state parity, or the first and fiftieth simulation states.
The active quantitative benchmark retains its original initialization; matching an older illustration does not justify changing it.
The original-engine observer remains necessary, and this study remains incomplete.

## Full benchmark scaling prefix: 31 of 48 conditions

[The sealed live snapshot](results/full-scaling-prefix31-2026-10-18)
contains 3,100 steps from 31 complete scaling conditions in the original full benchmark.
These cover repetition zero at all 16 widths and repetition one at widths 256–3840.
All 3,100 integer population observations exactly match the pinned author archive.
All 62 population and timing means reconcile with their raw rows within decimal CSV rounding bounds.
The auditor requires complete 100-step conditions and consistent keys across both files.
Files were copied sequentially while the benchmark continued; their exact alignment passed before analysis.

The first 1,000 population values also match the earlier qualification run exactly.
That overlap receives no additional grid coverage: this snapshot adds 21 unique conditions and 2,100 unique condition observations.
Seventeen scaling conditions, all occupation and resolution conditions, and the individual-state checks remain outstanding.
Timing values describe the H100 run; they do not establish equivalence with the paper's V100.
The original command remains active. This snapshot supplies neither a terminal-success receipt nor whole-paper completion.

```sh
python replications/richmond_2023/audit_scaling_snapshot.py \
  replications/richmond_2023/results/full-scaling-prefix31-2026-10-18 \
  replications/richmond_2023/results/full-scaling-prefix31-2026-10-18/reference.csv \
  /path/to/new-audit.json
```

The public snapshot retains both raw native CSVs, the pinned reference, file hashes,
the download receipt, and every recomputed mean with its rounding bound.

## Prepared passive-state audit

`audit_agent_states.py CAPTURE GNU_INITIAL_CSV BENCHMARK_CSV NEW_REPORT` validates the completed 100-step observer.
It requires the exact observer source and protocol, terminal success, the pinned GNU host initialization,
and the immutable scaling-prefix CSV published above.
It compares all initial active fields and all 100 occupied-population counts before reporting state diagnostics.
Each captured cell retains its host landscape capacity; resource bounds include the original occupied-cell sentinel of minus one.

The report separates occupied, requested, and unresolved statuses; counts nonpositive wealth and altered metabolism;
and records duplicate IDs and wrapped displacement between consecutive unique-ID records.
Duplicate IDs remain visible and are excluded from displacement pairing.
Multiple resolution rounds can produce displacement greater than one, so that alone is not classified as a rule violation.
Matching population counts cannot prove that instrumentation leaves every internal state unchanged.

The [complete native capture and readback](results/state-observer-complete-2026-10-18) pass the audit after matching the initializer toolchain.
All 893,017 observations are validated for the stated checks; whole-study completion remains outstanding.

## Full benchmark scaling prefix: 47 of 48 conditions

[The next sealed snapshot](results/full-scaling-prefix47-2026-10-18)
adds sixteen complete conditions and 1,600 observations to the earlier prefix.
It covers all widths in repetitions zero and one, and widths 256–3840 in repetition two.
All 4,700 integer population observations exactly match the pinned author archive.
All 94 timing and population means reconcile with the raw rows within CSV rounding bounds.
Both files contain complete matching condition keys; their sequential capture passes the same alignment audit.
Every row overlapping the previous snapshot is identical, including recorded timings.
The downloaded 45,616-byte archive matches its remote SHA-256 receipt.
Auditing the public copy reproduces the complete audit byte-for-byte.

One scaling condition, eighteen occupation conditions, eighteen resolution conditions,
and the queued individual-state observer remain outstanding.
The H100 timings do not establish equivalence with the historical V100 hardware.
The original full-grid command remains active, so this is not terminal-success evidence
or a whole-paper verdict. Original source-rule and Figure 11 provenance questions remain open.

## Complete population, resolution and scaling plots

[The reconstructed Figure 11 A-C data](results/native-figures-2026-10-18) use the full original benchmark.
Population and resolution curves agree exactly with the author archive.
H100 timing scales approximately linearly across all sixteen widths: descriptive R² 0.999705,
versus 0.999422 in the archived V100 data. Seed ranges and all fit residuals are retained.
Different hardware/toolchains prevent interpreting this as historical absolute-timing reproduction.
Earlier partial-prefix sections preserve their acquisition-time status; they are superseded by the complete audit.

## Native initial, first and fiftieth image comparisons

[The fixed-grid comparison](results/native-image-comparison-2026-10-18) reconstructs all three views
from the audited native capture. It matches 13,579, 14,295 and 16,454 of 65,536 released image classes
at initialization, iteration one and iteration fifty respectively.
The initial landscape differs before simulation; historical visualization provenance remains unresolved.
The quantitative benchmark remains unchanged. Empty-cell resource reconstruction and renderer limits
are explicit, and these differences do not yet constitute a completed negative paper verdict.
