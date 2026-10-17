# Richmond et al. (2023): FLAME GPU 2 Sugarscape

Status: **incomplete; qualification audited, full native grid running, model fidelity under investigation**.
No completed-study credit. This study adds to the existing replication program.

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

## Full unchanged native benchmark launched

[The frozen full-run protocol](results/full-native-launch-2026-10-17/protocol.json)
runs all 84 original conditions in one process, preserving the native counter
lifecycle. It reuses the verified unmodified executable and checks its hash before
execution. The prior qualification and observer remain separate evidence and are
excluded from this ensemble's coverage.

Command `cmd-8h5jk` has a six-hour outer limit and a 21,300-second native limit.
At the quoted rate, six hours costs at most $24.192, excluding final idle time.
The terminal evidence collector is capped at 100 MiB. Population/resolution values
will be compared with the archive; timing comparisons remain descriptive across
different hardware. No acceptance margin is selected after observing differences.
Operational completion alone will not establish full coverage or paper replication.

## Agent-state fidelity: pinned-source findings

The [source audit](results/model-rule-source-audit-2026-10-17/audit.json) identifies
additional rule differences in the exact paper-linked revision. These are static findings;
no new native state trace or effect estimate is claimed.

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
occurrence has not yet been measured.

Hotspot separation uses toroidal distance, whereas sugar influence uses direct coordinates.
The paper's distance norm leaves boundary interpretation insufficiently explicit, so this
is a specification question rather than an established contradiction.

After the full original benchmark finishes, a separate passive state observer must inspect
agent IDs, metabolism, wealth, and movement. Its population trace must match all 100
unmodified qualification observations before interpretation. Observer timings cannot count
as benchmark timings. No source correction is applied to the ongoing historical replay.
