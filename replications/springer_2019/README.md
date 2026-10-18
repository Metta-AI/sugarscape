# DynaSOAr Sugarscape benchmarks (Springer and Masuhara, 2019)

Status: three native implementations complete debug execution qualification after declared compiler-portability changes. The paper replication remains incomplete.

The [ECOOP paper](https://doi.org/10.4230/LIPIcs.ECOOP.2019.17) benchmarks a Sugarscape model with movement, resource consumption, ageing, and mating. Its [official artifact](https://doi.org/10.4230/DARTS.5.2.2) contains the model, allocator implementations, dependencies, and archived reproduction instructions. The artifact is the source of truth for this study; the framework's other applications are outside its Sugarscape scope.

[Source audit](results/source-2026-10-18/audit.json): archive MD5 matches the publisher's checksum; SHA-256 is `75421734305809c5999904082616996a904a19a5e43466cf076ec10660e559a1`. All archive files have recorded hashes. Four Sugarscape implementation files, configuration, build script, and benchmark driver match current GitHub revision `a4f956cd13160eb566e8a0caef6aad1e59c26da9` exactly. This comparison does not assert equality of the entire allocator library.

## Complete Sugarscape targets

- Figure 10: total and enumeration timing for DynaSOAr, mallocMC, Halloc, BitmapAlloc, CUDA allocation, and static array-of-structures/structure-of-arrays baselines.
- Figure 11: maximum Sugarscape problem size at equal allocator heap sizes, excluding enumeration arrays as the paper does.
- Sections 6.1–6.2: assess the Sugarscape performance and memory-efficiency interpretations against reproduced measurements.

Original defaults are a 1,700×1,700 grid, seed 42, and 10,000 iterations. The benchmark driver requests five repeats. The paper uses a Titan Xp, CUDA 9.1, Ubuntu 16.04.4, and an 8 GiB allocation heap for timing comparisons. Contemporary GPU results must state their hardware/toolchain differences. Historical absolute seconds cannot be transferred to a different GPU.

The source driver requests `sugarscape_no_cell`, while its archived CMake target is `sugarscape_soa_no_cell` and shell-build output is `sugarscape_dynasoar_no_cell`. Execute verified source paths rather than treating a missing executable as a failed paper result.

## Qualification protocol

Before full benchmarking, build the unchanged archived static-cell DynaSOAr implementation and both static baselines in debug mode. Use a 32×32 qualification grid, the original 10,000 iterations and seed 42, and two executions per binary. Preserve compilation logs, exit status, native checksum, timing, source hashes, and device/toolchain identity. Debug assertions and successful execution are prerequisite evidence, not independent model validation or paper replication.

The original CUDA 9.1 Docker tag is unavailable. Qualification therefore uses the pinned CUDA 11.8 Ubuntu 20.04 image recorded in the protocol, with compute-6.1 PTX for driver compilation. This changes compilation/runtime provenance; model sources remain unchanged. No timings from this small qualification grid count toward Figure 10.

Full-grid timing, matched-heap capacity searches, independent state/conservation checks, published-bar extraction, and claim-level analysis remain outstanding. Keep source defects, failed builds, allocator failures, and hardware differences visible before assigning any verdict.

## Native qualification and preserved failures

The artifact-library attempt fails because the archived CUB conflicts with CUDA 11.8's Thrust. Selecting the toolkit's matching CUB/Thrust exposes missing dependent-template syntax. The author's [2021 fix](https://github.com/prg-titech/dynasoar/commit/2bede5fc9ec715e13be6a77e12f758a4549c815b) supplies four `template` keywords for existing allocator calls. Two bitmap member-function pointers additionally require explicit `<S>` template arguments with this compiler. Both allocator edits are recorded separately from the unchanged Sugarscape model files.

The final qualification uses the matching toolkit libraries and these syntax edits. All three builds and six 10,000-iteration executions exit zero. These are compiler/runtime qualification repeats on one 32×32 input, not independent scientific seeds. The native checksum sums agent type codes only; it does not validate the complete state or economic trajectories.

```sh
python qualify.py NEW_OUTPUT --cub toolkit --source-mode portable-syntax
```

Use `--cub artifact --source-mode archived` to preserve the initial artifact-library attempt. Every attempt remains retained; a failed build is not a negative replication. Independent model validation and all full-size paper targets remain outstanding.

## Heap accounting before paper comparisons

[The archived-source audit](results/heap-source-audit-2026-10-18/audit.json) shows that the nominal heap parameter does not mean equal allocations across implementations. BitmapAlloc allocates `3*kMallocHeapSize/4`: 6 GiB at the nominal 8 GiB default. DynaSOAr uses object capacity divided by 64, multiplied by its compiled block size; its allocator metadata is additional. The CUDA 11.8 qualification reports 6,208-byte blocks. Applying that layout to the archived default capacity implies a 1,627,389,952-byte data buffer, not 8 GiB. This is a source-derived extrapolation, not a full-capacity execution measurement.

The artifact’s Figure 11 instructions include DynaSOAr allocator metadata in its reference budget. Their worked example uses the reported total memory usage, then passes that byte budget to mallocMC. The paper separately excludes enumeration arrays. Consequently, capacity comparisons must record heap, metadata, enumeration and static-cell allocations separately. Preserve native-default results alongside explicitly matched-budget controls; neither successful compilation nor matching nominal flags establishes equal memory budgets.

## Published capacity targets

[Figure 11 targets](results/published-capacity-targets-2026-10-18/targets.json) come from the six Sugarscape vector bars on publisher PDF page 23. The retained compressed SVG preserves the source geometry; `extract_capacity_targets.py` verifies its hash and extracts each bar relative to DynaSOAr. The rendered legend and adjacent bar order were visually checked.

| Allocator | Maximum problem size relative to DynaSOAr |
| --- | ---: |
| DynaSOAr | 1.000 |
| mallocMC | 0.745 |
| Halloc | 0.724 |
| BitmapAlloc | 0.939 |
| Baseline SOA | 0.641 |
| Baseline AOS | 0.621 |

These are digitized graphical targets, not recovered raw measurements or newly replicated capacity results. Coordinate precision does not establish an experimental acceptance tolerance. The archived worked example varies one wa-tor dimension; Sugarscape exposes a square-grid side length. Resolve the paper’s problem-size convention before comparing side-length or cell-count ratios. Figure 10 timing targets are recorded below.

## Published timing targets

[Figure 10 timing extraction](results/published-capacity-targets-2026-10-18/timing-targets.json) uses seven axis grid lines and the colored bars plus white enumeration caps. The CUDA bar exceeds the axis; its printed 857.1-second annotation supplies the total. Its separate enumeration time cannot be recovered from this clipped bar.

| Implementation | Total seconds, published Titan Xp |
| --- | ---: |
| DynaSOAr | 85.7 |
| mallocMC | 128.3 |
| Halloc | 128.3 |
| BitmapAlloc | 93.8 |
| CUDA Allocator | 857.1 |
| Baseline SOA | 62.6 |
| Baseline AOS | 253.2 |

The extracted bars qualify Section 6.1’s general statement that baseline versions are faster: SOA is faster than DynaSOAr, but AOS is slower in this Sugarscape chart. Preserve this distinction in claim-level comparisons. These historical totals are graphical targets, not measurements on the qualification H100. Native benchmark runs must report enumeration and total timing separately and retain hardware provenance.

## Full-size native-default batch

[The registered batch](results/full-native-defaults-2026-10-18/protocol.json) uses the original 1,700×1,700 grid, 10,000 iterations and seed 42. One DynaSOAr debug execution records allocator layout and assertions; five release executions each measure DynaSOAr, AOS and SOA. Every input source hash is checked against the successful qualification. No size or capacity macros override archived defaults.

Command `cmd-7k3hf` is registered on the owned H100 with a 45-minute execution bound and $5 budget. It exited after the full-size debug process hit its 600-second limit, before any release run started; the failure is retained below. Four allocator variants remain outside this first batch; all seven variants, independent model validation and capacity searches remain required. New-hardware timings cannot establish historical absolute timing equivalence.

## Remaining allocator qualification

`qualify_remaining_allocators.py` compiles CUDA, BitmapAlloc, mallocMC and Halloc from a separate copy of the qualified artifact source. External allocator adapters remain unchanged in this first attempt. Successful builds receive two 32×32, 10,000-iteration debug executions. Failed builds remain recorded and prevent a successful qualification verdict.

[The bounded protocol](results/remaining-allocators-2026-10-18/protocol.json) waits for the full-size timing batch to exit and its sealed export to complete. It requires the owned node to remain awake. The qualification has a 20-minute outer limit and $3 budget, including the idle window. Its compiler dependencies and outputs will be retained; scheduling is not evidence of execution.

## Recovered author figure source

[The arXiv source bundle](https://arxiv.org/src/1810.11765) supplies the original plotting scripts and baseline timing CSV. [The retained audit](results/author-figure-source-2026-10-18/audit.json) records every source member hash and reconciles the plotting values with the independently digitized publisher chart.

Figure 10’s source totals are 85.704 s (DynaSOAr), 128.306 s (mallocMC), 128.282 s (Halloc), 93.760 s (BitmapAlloc), 857.074 s (CUDA), 62.597 s (SOA), and 253.198 s (AOS). The CUDA comment recovers 36.435 s of enumeration time, unavailable from its clipped bar.

The five baseline repeats reveal that plotted AOS/SOA values are their minima, not medians. Their medians are 253.369 s and 62.805 s respectively. Future batch audits retain every repeat and report both minimum and median; the historical baseline comparison uses the evidenced statistic. Raw dynamic-allocator repetition identities remain unestablished.

The capacity script contains unnormalized arrays and commented-out divisions for all series except AOS. Explicitly normalizing its Sugarscape values by 1.6099131 reconstructs the published ratios to graphical precision. Executing the script unchanged would not reproduce Figure 11. This is a recovered plotting-source discrepancy, not evidence against the allocator result. The original square-grid problem-size convention remains unresolved.

## Full-size debug timeout

[The first full-size batch](results/full-native-defaults-timeout-2026-10-18) compiled successfully but its debug process exceeded the 600-second limit. No execution completed and no release timing started. The sealed failure archive matches its export hash and preserves the executed runner, binary, log, compiler/device provenance and source manifest.

This is incomplete execution, not a 600-second timing measurement or negative paper replication. The native program prints no per-step progress; slow execution and a stalled kernel remain unresolved. A bounded progress-observed control is needed before extending run limits or interpreting hardware performance. The remaining-allocator qualification started separately as `cmd-89573` after this failure’s evidence export.

### External allocator compiler failures

[All four archived adapters](results/remaining-allocator-failures-2026-10-18) fail compilation under CUDA 11.8; no simulation starts. Diagnostics identify dependent-template calls in the shared adapter. The complete failure archive and four compiler logs are retained.

A separate attempt inserts eight `template` keywords into existing shared-adapter calls, recording original and effective hashes. This is a local syntax correction, not an authenticated historical revision. Use `qualify_remaining_allocators.py QUALIFICATION NEW_OUTPUT --adapter-source archived` for the unchanged adapter, or `--adapter-source portable-syntax` for the declared correction. Model source and allocator algorithms remain unchanged.

### Bounded host-progress diagnostic

`diagnose_progress.py` adds host-side stderr records around initialization and simulation phases. It preserves model rules, random calls, kernel ordering, synchronization calls and the original 10,000-step horizon. Logs cover the first two iterations and every hundredth thereafter. Post-launch host records do not alone prove kernel completion; the next record after an existing synchronization supplies that boundary.

[Command cmd-9vcwk](results/progress-diagnostic-2026-10-18/protocol.json) first checks the observer on the qualified 32×32 input, then probes full-size debug and release builds for 120 seconds each. It has a ten-minute outer bound and $2 budget. It is diagnostic instrumentation, not a timing benchmark or independent state-validation claim.

### External allocator runtime audit

[All four corrected builds](results/remaining-allocator-runtime-2026-10-18) pass compilation. CUDA and BitmapAlloc each complete two debug executions. mallocMC fails twice with a `Cell_leave` occupancy assertion (exit 198); Halloc segfaults twice (signal 11). The complete native archive, source-change reconstruction, per-file hashes, binary hashes and all eight execution records are audited. These failures require implementation/toolchain investigation before any paper verdict.

The initial progress diagnostic failed before compilation because its Python runner used syntax unsupported by Python 3.8. Its sealed failure remains retained. The runner now passes Python 3.8 grammar validation; corrected command `cmd-cyq9u` uses the same bounded protocol.


### Initialization and architecture diagnostics

[The corrected compute-61 diagnostic](results/progress-compute61-2026-10-18) completes its 32×32 debug control through 10,000 steps. Both 1700×1700 builds time out after 120 seconds. Their final host record follows the agent-creation launch; neither returns from the subsequent existing CUDA synchronization. No simulation timestep starts. This localizes the full-size failure to initialization, without proving its underlying cause.

[The compute-90 comparison](results/progress-compute90-2026-10-18) changes only the target architecture in the diagnostic compilation. Its 32×32 control fails during agent creation with the allocator's `__activemask() == active` assertion. The gate prevents full-size probes. This is evidence of a target-dependent allocator failure, not proof that it explains the compute-61 timeout. Synchronization assumptions require investigation before any algorithm change or performance comparison.

`audit_progress.py` verifies both sealed archives, original qualified source hashes and compiled binary hashes. Removing the declared observer restores the original statement sequence. Logs, source differences, exact compile flags and failures remain archived. The first auditor's line-diff check misclassified an unchanged synchronization statement because of diff alignment; the statement-sequence check resolves that without changing simulation code.

Use `diagnose_progress.py QUALIFICATION NEW_OUTPUT --architecture 61 --control-mode debug` or `--architecture 90 --control-mode debug`. Both diagnostics retain seed 42 and 10,000 steps; the full-size probes retain the original 1700×1700 grid and object capacity. Instrumented timings cannot count toward published benchmark claims. The owned GPU was stopped after both exports completed and downloaded archives passed audits.


### Separate release-mode control

[NVIDIA's warp-primitive documentation](https://developer.nvidia.com/blog/using-cuda-warp-level-primitives/) does not guarantee active-mask equality across instructions under independent thread scheduling. The author allocator checks that equality before synchronized shuffles. Its failure may therefore reflect a debug assumption; this remains distinct from the compute-61 initialization timeout.

[The bounded release-control protocol](results/release-control-2026-10-18) uses `--architecture 90 --control-mode release` without changing allocator or model code. Completing a release control would establish execution only, not correctness after assertions are disabled. The author benchmark already uses release builds. The full-size debug probe remains in the diagnostic sequence and retains its failures.

The first resumed attempt failed before simulation because the container reset removed system Python. Its exit-127 archive is preserved and hash-checked. Command `cmd-3ga3h` explicitly restores Python before execution, with a 20-minute outer limit including setup and a $3 budget. Its sealed-evidence collector is active; pending outputs receive no completion credit. The auditor records observed outcomes without requiring the earlier timeout to recur; both earlier archive audits reproduce byte-identically.


### Completed native release control

[The complete release-control audit](results/release-control-complete-2026-10-18) confirms a successful 32×32 release run, the full-size debug active-mask assertion, and a full-size release timeout during agent creation. Disabling debug assertions in the author’s release mode does not resolve the initialization failure. All 511 qualified source hashes and three binary hashes pass.

The small control reduces both grid size and allocator capacity. Those factors still need separating before attributing the timeout to population, allocator size, scheduling or an implementation error. No benchmark or paper-completion claim follows from these diagnostics.
