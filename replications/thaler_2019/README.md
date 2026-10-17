# Thaler and Siebers (2019): parallel Sugarscape

Status: **partial: Figure 5b reproduced, archived analysis and native execution verified**. No full-paper completion credit.

Paper: [A tale of lock-free agents](https://doi.org/10.1186/s40294-019-0067-9),
Complex Adaptive Systems Modeling 7, 5, published December 26, 2019.
[Original implementation](https://github.com/thalerjonathan/haskell-stm-sugarscape)
uses BSD3 licenses in each project. The paper is CC BY 4.0.

## Scope and outstanding work

Reproduce the paper's Sugarscape case study: Figure 5 population dynamics;
Tables 6–9 and Figures 6–7 covering timing, scaling, and transaction retries.
The separate SIR epidemic case study is outside this Sugarscape study.

The native model uses a 50×50 toroidal landscape, initial population 500,
endowment 5–25, metabolism 1–5, vision 1–6, and growback one per step.
Agents die from starvation, without ageing. Sequential execution shuffles agents;
concurrent execution delegates ordering to the scheduler. The sequential implementation
shuffles the environment behavior together with agents. Concurrent implementations
run growback synchronously after the population. Performance runs use 1,000 steps and seed 42.
The scaling experiment replaces dead agents and varies initial population from
500 to 2,500 in increments of 500. Preserve the released landscape and random initialization.

Required fresh experiments remain:

- Figure 5a agent/environment state checks and concurrent population comparisons.
  Figure 5b sequential population replay now passes, as documented below.
- Sequential reference plus Lock-Based, TVar and TArray timing across 1–8 capabilities.
- Four implementations across all five rebirthing populations, with four capabilities for concurrent variants.
- TVar/TArray retry ratios across 1–8 capabilities, measured separately from timings.
- TArray carrying-capacity and rebirthing performance/retries at 16, 32 and 64 capabilities.

The paper's local machine was an i7-8550U laptop, Ubuntu 19.10, with GHC 8.4.3
and Stack resolver lts-12.4. Hardware changes prevent treating identical elapsed
seconds as an appropriate fresh-run criterion. Before confirmatory runs, freeze
hardware topology, resource isolation, repetitions, ordering and confidence-interval
comparisons for the paper's relative-performance claims. Do not infer physical core
counts from Haskell capabilities. No fresh-run acceptance criteria are finalized yet.

## Source fidelity

Use timing revision `f5851488bf2369e2bbdc3f2499ed69c142de9fec`.
All 61 model/build files match revision `b6c4aeccdc153f26edef9709764e055e4e36b806`,
which contains the completed local experiments.

Revision `6a79b8b2e623c288c087b91aff400ac2c4d95510` enables TArray retry instrumentation.
Its source explicitly warns of reduced performance. It is suitable for toolchain
validation and instrumented measurements, not the uninstrumented timing comparison.
Latest revision `2bf138a8b5f1d020f09781932e110091802f6dcc` additionally replaces the
sequential benchmark entry point with population CSV export.
[Revision hashes](results/archived/revision-fidelity.json) retain these distinctions.

The pinned `stm-stats-0.2.0.0` library computes retries divided by commits,
not retries divided by attempts. Its counters persist within the process;
record process boundaries and cumulative counts when interpreting repeated benchmarks.

## Reproduced archived analysis

The audit reads 53 complete author Criterion HTML reports, checks their SHA-256
hashes, and independently fits ordinary least squares to 212 raw measurements.
All regression slopes match within 1.99e-13 seconds. All 51 printed timing cells
in Tables 6, 8 and 9 match after rounding to three significant digits.
All 53 archived sample standard deviations also reproduce from the raw per-iteration timings.
Of 45 printed standard deviations, 30 match rounding to the nearest hundredth; 15 differ.
The largest absolute difference is 0.008984 seconds. These reporting differences remain explicit;
no alternative tolerance or negative paper verdict is assigned. Table 9 parentheses are retry ratios,
which cannot be reconstructed from these timing samples and remain unvalidated.

These are author archival measurements, not fresh simulation runs, independent
engine validation, or a hardware performance replication. The separate native
execution proof below verifies full original-model runs, without a timing verdict.

From this checkout, with Python 3.11, NumPy 1.26.4 and Poppler `pdftotext` installed:

```bash
python replications/thaler_2019/audit_archive.py \
  /path/to/haskell-stm-sugarscape \
  /path/to/s40294-019-0067-9.pdf \
  /path/to/new-audit-directory
```

The author checkout must contain the pinned report files, available at latest
revision above. Download the publisher PDF from
`https://link.springer.com/content/pdf/10.1186/s40294-019-0067-9.pdf`.
The command requires a new output directory and rejects changed paper/report bytes.
Committed results retain individual raw-report paths, recomputed slopes, paper
cells, and limitations. Full raw HTML remains in the pinned original repository.

## Population target fixed before native execution

Figure 5b contains a raster curve rather than vector coordinates or raw measurements.
The pinned PDF embeds a 1412×830 image on page 18. We visually checked the plot,
calibrated both axes from tick centers, and extracted the blue curve separately
from axes and labels. The resulting 50 targets span times 0–49, falling from
approximately 500 to 206 agents.

The [frozen protocol](results/population-target/target-protocol.json) accepts a maximum
absolute difference of two agents at every time point. This allows raster line width,
antialiasing and axis calibration uncertainty. It was fixed before any fresh native
population output. These targets are digitized measurements, not author raw data.
The caption does not specify a seed; the released population exporter uses seed 42.
A mismatch requires checking revision, seed, time indexing and model semantics.
The fresh Figure 5b result below now passes this unchanged protocol.

Recreate the target with Python, PyMuPDF 1.26.5 and NumPy 1.26.4:

```bash
python replications/thaler_2019/extract_population_target.py \
  /path/to/s40294-019-0067-9.pdf /path/to/new-target-directory
```

The output includes the original embedded figure, every extracted pixel-column
measurement, interpolated population targets, calibration and artifact hashes.

## Scheduling and population measurement audit

The [source audit](results/archived/scheduling-audit.json) checks 11 files against the
pinned timing revision. Sequential `Init` inserts the environment as behavior ID 0;
`Simulation` shuffles that behavior with agents. Concurrent `Main` sets `envConc=False`,
and `Simulation` waits for all agents before stepping the separate environment.
Thus the released variants do not share the same growback schedule. Preserve this
difference for faithful replay; investigate its effect before attributing performance
changes solely to synchronization.

Sequential agents consume metabolism and die, if necessary, before moving and
harvesting. Surviving agents emit observables; the environment emits none. The released
population exporter counts those observables. Its times 0–999 label post-step outputs
using the pre-increment clock. Do not prepend an initial-state row or shift times when
comparing the first 50 rows with Figure 5. These source findings establish measurement
semantics, not a fresh simulation result or a negative replication verdict.

## Native execution proof

All four unmodified timing-revision implementations built with GHC 8.4.3 and
completed one full 1,000-step, 500-agent, seed-42 execution. Concurrent variants used
one Haskell capability; the sequential executable is not threaded.
[Retained evidence](results/native-workflow-2026-10-17/provenance.json) includes all
four zero exit statuses, commands, binary hashes, compiler versions and output logs.
All 61 model/build source hashes were checked again after execution.

Execution used emulated amd64 Linux on an ARM Mac with other experiments running.
Elapsed times are diagnostic records, not performance replication evidence.
Concurrent population comparisons, scaling and retry measurements remain outstanding.

The build used Ubuntu 22.04, Stack 2.3.3, GCC, make, libgmp-dev, libtinfo5 and
freeglut3-dev. Use an isolated Stack root with the retained
[global configuration](results/native-workflow-2026-10-17/stack-global-config.yaml).
It updates retired download/cache locations and root signing keys without changing
the pinned compiler or packages. Three-signature verification and expiry checks remain enabled.

From Linux with the timing revision checked out and Python 3.10 or later:

```bash
python replications/thaler_2019/run_native.py \
  /path/to/haskell-stm-sugarscape \
  replications/thaler_2019/results/archived/revision-fidelity.json \
  /path/to/new-native-output
```

The command checks source hashes, builds each executable, verifies its exact benchmark
name and compiler, and records each full execution. Its total budget is 1,800 seconds;
each simulation has a 600-second limit. Provision the historical compiler and dependencies
first on slow machines. A successful run proves execution, not the full paper's claims.

## Fresh Figure 5b replication

Two full native 1,000-step exports from population revision
`2bf138a8b5f1d020f09781932e110091802f6dcc` are byte-identical.
All 50 Figure 5b points pass the predeclared two-agent tolerance; the maximum
absolute difference from the raster target is 0.655956 agents. No seed, time shift,
model rule or tolerance changed after viewing the native output.
Population is 500 at output time 0, 206 at time 49, and 192 at time 999.
The paper only plots the first 50 points; later points are additional native output.

The [independent audit](results/population-replay-2026-10-17/independent-audit.json)
rechecks both raw CSVs, all timestamps, all 50 errors, and all 27 source files.
[The overlay](results/population-replay-2026-10-17/population-comparison.png) was visually
inspected against the extracted published curve. The complete trajectories, binary
hash, compiler, commands' output logs and fixed target protocol are retained.
This reproduces Figure 5b only; it does not establish Figure 5a state agreement,
concurrent dynamics, performance, scaling or retry claims.

Use a separate checkout of the population revision and the same Linux toolchain.
Copy `source-manifest.json` from `results/population-replay-2026-10-17/` into that
checkout's root. Copy `population-target.csv` and `target-protocol.json` from
`results/population-target/` there too. Then run:

```bash
python replications/thaler_2019/run_population.py \
  /path/to/population-checkout /path/to/new-population-output
```

The runner checks source hashes before building, requires GHC 8.4.3, checks both
1,000-row exports and their byte identity, and reports the frozen Figure 5 comparison.
It requires a new output directory and preserves a failed comparison rather than
changing the tolerance. Allow 1,800 seconds total after dependencies are installed.

## Figure 5a state comparison remains unresolved

The [frozen image protocol](results/state-comparison-2026-10-17/protocol.json)
extracts 201 occupied cells from Figure 5a. The grid and color thresholds were fixed
before native position export; five pixel-count thresholds identify the same cells.
The extraction overlay was visually inspected.

An observational entry-point patch exports existing states at output times 49 and 50.
All other 26 archived files remain byte-identical, and the full 1,000-step population
CSV exactly matches the unmodified exporter. Both states contain 206 distinct agents;
all 2,500 cell coordinates and resource bounds pass, and occupier IDs match agents exactly.

The [comparison](results/state-comparison-2026-10-17/audit.json) does not match the image:
67 occupied coordinates agree at time 49 and 57 at the primary time 50.
The published caption does not specify the screenshot's implementation or seed.
This is an unresolved screenshot comparison, not a negative paper verdict.
Figure 5b's successful population comparison is unchanged.

Reproduce the observer by applying the retained `observer.patch` to `Main.hs` in a
separate population-revision checkout. Build and run that checkout's sequential exporter
using the same GHC 8.4.3 toolchain. The patch only writes existing simulation outputs;
it does not change initialization, update rules, step count or scheduling.
Then audit its output, using PyMuPDF 1.26.5 and NumPy 1.26.4:

```bash
python replications/thaler_2019/audit_state.py \
  /path/to/s40294-019-0067-9.pdf \
  /path/to/observer-checkout/criterion/sugarscape-seq /path/to/new-state-audit
```

The committed directory also contains all raw CSVs, allowing the audit to run directly
against `replications/thaler_2019/results/state-comparison-2026-10-17`.

## Fresh timing ensemble

The [frozen protocol](timing/protocol.json) specifies all 45 Table 6 and Table 8
conditions. It preserves the original Criterion defaults, GHC 8.4.3, and timing
revision `f5851488bf2369e2bbdc3f2499ed69c142de9fec`.
Conditions run serially on a dedicated provider node with eight reserved physical cores.
This differs from the paper's four-core/eight-thread laptop; absolute seconds are
hardware-dependent, and any resulting comparison must identify that difference.

Each condition permits at most three attempts, retaining every report and selecting
the first with regression R-squared at least 0.99. Raw iteration counts must match
the author's four measurements: 1, 2, 3, and 4. A failed check stops the run;
unaccepted conditions remain unresolved. Completed conditions receive sealed checkpoints.
The measurement budget is ten hours, with a twelve-hour outer command limit.

The initial command failed during setup; the replacement is building as of October 17,
2026, 21:00 UTC. No fresh timing result is claimed. The driver has passed syntax and
lint checks, but its full ensemble has not run yet. The four original native executables passed the execution proof above.
With the retained Stack configuration installed and eight reserved cores available:

```bash
python replications/thaler_2019/timing/run_timing.py \
  /path/to/timing-revision-checkout /path/to/new-timing-output
```

The driver requires the provider's `GMN_CPU_LIMIT` and `GMN_MEMORY_LIMIT_BYTES` resource
metadata. It records topology, affinity, source hashes, executable hashes, commands,
raw reports, fit decisions, and missing conditions. Table 9, retry instrumentation,
and concurrent population dynamics remain separate outstanding targets.

## Timing allocation recovery

[The original allocation failed before execution](timing/provisioning-retry-2026-10-17)
when the provider exhausted its reserved eight-core CPU slots. The provider reports
that nothing was created or billed. A replacement allocation uses the same node
name, unchanged protocol and bootstrap, and a four-hour queue hold.
Its bounded boot command is registered; no timing result is claimed.

The dedicated-core requirement remains intact. GPU-host CPU quotas are shared
and would change the timing conditions. Historical failed allocation and command
identifiers remain in the recovery evidence alongside the replacement identifiers.

## Instrumented retry counters: complete native workflow check

[Four complete 1,000-step runs](results/retry-instrumentation-2026-10-17)
validate the original TVar and TArray instrumentation with GHC 8.4.3 and
`stm-stats-0.2.0.0`. Each executable runs two iterations in one process, with
seed 42, 500 initial agents, no rebirth, and one Haskell capability.
The only model-source change enables the existing instrumentation flag.

| Implementation | Iteration | Commits during iteration | Retries during iteration | Retries / commits |
| --- | ---: | ---: | ---: | ---: |
| TVar | 1 | 190,679 | 850 | 0.004458 |
| TVar | 2 | 194,010 | 848 | 0.004371 |
| TArray | 1 | 193,587 | 671 | 0.003466 |
| TArray | 2 | 191,446 | 739 | 0.003860 |

All four native reports print `0.00`, despite nonzero retry counts. The second
report in each process contains cumulative counters; the table subtracts the first
report to recover the second iteration. A rounded zero cannot establish zero retries.
Fresh retry experiments must retain integer counters and process boundaries.

The independent auditor verifies all pinned baseline files, the exact flag changes,
binary hashes, commands, successful exits, report counts, and ratio rounding.
Extracting the retained archive reproduces the complete audit byte-for-byte.
An initial build failed because the source subset omitted LICENSE and ChangeLog.md;
restoring and hashing those original files resolved it. Failed attempts remain retained.

These runs used x86 emulation and establish instrumentation behavior, not the paper's
multicore ratios, timing, or scaling claims. Instrumented timings remain excluded from
the uninstrumented performance experiment.

```sh
python replications/thaler_2019/audit_retries.py EXTRACTED_ARCHIVE EXTRACTED_ARCHIVE/baseline NEW_AUDIT.json
```

## Source-download failure recovered

[The recovered command log](timing/source-recovery-2026-10-17/failed-command-log-002.txt)
shows that command `cmd-gjm6m` exited 128 while cloning the author repository:
GitHub hostname resolution failed. No build or simulation had started.
The original output directory and failure log remain retained.

The replacement uses a local `git archive` of the same timing revision. Its SHA-256
is checked on the node before extraction; an independent local audit verifies all
61 declared model/build file hashes inside the archive. No model or timing protocol
changed. The retained bootstrap uses a fresh output directory and preserves terminal
logs and evidence on success or failure. Compiler and package provisioning still
require network access.

Command `cmd-if8u9` has a 43,200-second outer limit and the original ten-hour
measurement budget. At the observed $0.0096/minute rate, the outer limit costs at
most $6.912, excluding final idle time. A collector exports its sealed terminal
archive to task-owned storage with a 256 MiB transfer cap. Export completion will
require separate download and hash verification before analysis.

### Native timing prefix: 13 of 45 conditions

The sealed [checkpoint and independent audit](results/native-timing-prefix-2026-10-17/audit.json)
cover 13 completed conditions and 52 raw Criterion measurements. All 13 first attempts pass the frozen
R-squared threshold of 0.99. Independent least-squares slopes differ from reported values by at most
1.07e-14 seconds; recomputed R-squared values agree exactly. Sample standard deviations also agree.
The auditor checks the full 45-condition schedule, pinned source manifest, benchmark commands,
exit statuses, report hashes, attempt ledger, and missing conditions. Binary hashes record provenance;
they do not independently prove binary/source equivalence.

The original job continues. These results do not establish the full timing tables or their relative rankings.
The reserved CPU differs from the paper's hardware; absolute runtime comparisons need that qualification.

Reproduce the audit in a new output directory:

```sh
tar -xzf replications/thaler_2019/results/native-timing-prefix-2026-10-17/checkpoint-12.tar.gz -C /path/to/checkpoint
python replications/thaler_2019/timing/audit_native.py /path/to/checkpoint /path/to/new-audit
```

### Native allocation verification

[The allocation-aware audit](results/native-timing-prefix-2026-10-17/allocation-audit.json)
reprocesses the same 13-condition checkpoint without adding replication coverage.
It verifies affinity and effective CPU set both equal CPUs 88–95; `cpu.max` is
`max 100000`, so this captured container has no additional CPU-time quota.
The operating system reports an AMD EPYC 9R45 and one thread per core.
The auditor now requires eight allocated CPUs, matching affinity, no quota below
eight CPU-equivalents, and the recorded single-thread-per-core topology.

These observations substantiate the captured eight-core allocation. They do not
prove exclusive use of shared host resources or fixed clock frequencies.
The original laptop used four cores/eight threads, so capability scaling still
compares different hardware topologies. No same-hardware performance claim follows.

### Complete native Table 6 comparison

[All 25 conditions](results/native-table6-2026-10-17/comparison.json) now have
independently audited native results: 100 raw Criterion measurements, all first
attempts passing the frozen R-squared threshold. The sealed checkpoint's SHA-256 is
`abe70597f24a56d46d756930e27e73d0fe4cadde2906a4e9a5f0a7c0e440900a`.
The independent slope reconstruction differs by at most 1.43e-14 seconds.

| Capabilities | IO seconds | TVar seconds | TArray seconds |
| --- | --- | --- | --- |
| 1 | 12.5528 | 12.9017 | 19.1334 |
| 2 | 9.4504 | 10.2913 | 10.2671 |
| 3 | 7.9804 | 9.3582 | 7.6942 |
| 4 | 7.0376 | 8.5640 | 6.6783 |
| 5 | 6.7951 | 8.3352 | 6.3319 |
| 6 | 6.6431 | 8.3051 | 6.0826 |
| 7 | 6.4741 | 8.3541 | 5.5347 |
| 8 | 6.6730 | 8.4662 | 5.8688 |

The sequential baseline is 13.9448 seconds. Within each capability count, 26 of 27
pairwise point-estimate rankings agree with the paper. The exception is TArray versus
TVar at two capabilities: 10.2671 versus 10.2913 seconds, with overlapping reported
intervals. This descriptive ranking count is not a statistical replication criterion.

From one to eight capabilities, IO improves from 12.5528 to 6.6730 seconds and TVar
from 12.9017 to 8.4662. The paper instead reports IO rising from 21.0 to 31.2 seconds
and TVar from 21.1 to 49.0. TArray improves in both settings. The native fastest
TArray point is seven capabilities, versus four in the paper. Hardware topology
and scheduling differ; these measurements do not establish an implementation bug
or a same-hardware negative replication.

The comparison retains Criterion's original slope confidence bounds. TVar at eight
capabilities has a null lower bound in its native HTML report; it remains explicitly
undefined. The initial comparison failed on this actual null value; the revised
reader preserves undefined bounds and excludes affected pairs from overlap judgments.
No run was removed or repeated because of this missing bound. The predeclared fit
rule concerns R-squared, not completeness of bootstrap intervals.

Four increasing iteration-count samples are not four independent experiment repeats.
The bootstrap confidence bounds have not been independently reconstructed; interval
overlap is descriptive and speedup ratios have no derived uncertainty intervals.
Twenty Table 8 conditions, Table 9, retry scaling, and concurrent dynamics remain
separate requirements. This Table 6 result does not complete the paper.

```sh
python replications/thaler_2019/timing/audit_native.py EXTRACTED_CHECKPOINT NEW_AUDIT_DIRECTORY
python replications/thaler_2019/timing/compare_table6.py EXTRACTED_CHECKPOINT NEW_AUDIT_DIRECTORY NEW_COMPARISON.json
```

### Deferred multicore retry experiment

[The frozen protocol](results/retry-scaling-launch-2026-10-17/protocol.json) covers
all 16 Table 7 implementation/capability combinations plus the two reported
2,500-agent rebirth comparisons at four capabilities. Each condition receives five
fresh processes, each running one complete 1,000-step simulation with original seed 42.
The paper's historical retry repetition count remains unspecified; five is our declared
replication design, not a recovered historical setting. Thread scheduling remains nondeterministic.

Command `cmd-35frc` waits for `cmd-if8u9`'s terminal receipt before building or executing.
It uses a separate extraction of the pinned source archive and enables only the existing
instrumentation flags, with the same verified patches as the earlier workflow check.
Original model code, compiler 8.4.3, and runtime capabilities remain pinned.
No retry measurements or observer timings enter the uninstrumented timing experiment.

The 90-process schedule is shuffled before execution. Raw integer commits, retries,
printed ratios, commands, exits, and hashes are retained for every completed process.
Each process starts counters afresh. The measure is retries divided by commits;
it is not the fraction of all attempted transactions that retry.
The analysis must retain every declared condition and report incomplete runs separately.

Execution after the bounded wait is capped at 3,300 seconds, costing at most $0.528
at the quoted $0.0096/minute rate, excluding final idle time. A 32 MiB collector
exports the terminal archive after execution; download and independent verification
remain required. This launch adds no completed simulation or paper coverage yet.
