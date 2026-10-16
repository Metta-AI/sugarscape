# Multi-Level Mesa (Pike, 2019)

Status: incomplete study. Native pilots and observer validation do not constitute paper replication.

The [paper](https://arxiv.org/abs/1904.08315) links the author's [Sugarscape](https://github.com/tpike3/SugarScape) and [Multi-Level Mesa](https://github.com/tpike3/multilevel_mesa) implementations.
We select their last pre-publication revisions, respectively `585e53398f4f58e89ec184c83bb20819f0e4c96a` and `99d2091721076df9fff32e8b49a0e33e98c34a6f`.
Chronology does not prove these are the exact paper versions. Both repositories have MIT licenses; simulation sources remain in separate unchanged checkouts.

## Execution and measurements

`run.py ENGINE LIBRARY standard|explicit|network NUMPY_SEED NEW_OUTPUT` runs 1,000 steps with the released 200-agent, 50×50 configuration and Mesa seed 42.
Use Mesa 0.8.5. Historical library requirements specify Mesa >=0.8.5 and NetworkX >=2.2.
Our initial runtime uses Python 3.11.14, NumPy 1.26.4 and NetworkX 3.6.1; it is not claimed to match the historical environment.
Mesa 0.8.4 lacks the required model random generator. Mesa 0.8.8 changes grid containers, breaking the original empty-cell comparison.
The author's 2021 fix is not applied to these historical runs.

The released runners fix Mesa seed 42 but leave NumPy unseeded. Our explicit NumPy seed makes replication possible; original NumPy states are unavailable.
The runner retains source hashes, initial agents, native price records, native model reporters, individual identities and health records.
It reads agent registries after each native step without drawing random numbers or modifying the model.
The network variant's native `survivors` reporter counts scheduled groups/resources, so it must not be interpreted as individual population.
Individual counts instead use `ml.agents_by_type[NetAgent]` and reconcile with native health records.

`audit_observation.py NATIVE OBSERVED NEW_OUTPUT` requires byte-identical native price and reporter outputs, then checks every surviving identity against health records.
Initial standard and explicit pilots each finish with 47 individual agents. Each is one run, not an ensemble estimate.
The standard pilot repeats byte-identically in a separate process. Observer validation covers 1,000 steps and 51,622 standard or 51,642 explicit health records.

## Targets and full scope

[Extracted notebook targets](notebook_targets.json) retain source cells, cached outputs and notebook hashes.
Original raw datasets were omitted from the author's repository; cached outputs are reference evidence, not regenerated results.
Phase I cached mean survivors are standard 46.18, explicit 46.96 and network 46.68.
Common-resource cached means are one-level 94.35 and multi-level 92.83, matching the paper.
The notebooks multiply SciPy's already two-sided `ttest_ind` p-values by two, including a reported value above one.
Report the original analysis and correctly computed p-values separately; nonsignificance alone does not establish equivalence.

Remaining work covers the entire paper's Sugarscape experiments:

- Phase I: three approaches, 100 runs of 1,000 steps each; price convergence, dispersion, trade volume and survivor distributions.
- Phase II: explicit/network groups at thresholds of one, five and ten trades, with 100 runs per configuration.
- Phase III: group movement policies and one-level/multi-level common resources, including threshold comparisons and survival effects.
- Audit price aggregation against the original notebooks and preserve failed runs and undefined statistics.
- Quantify seed uncertainty; identify historical configuration differences before any negative verdict.
- Assess runtime comparisons on a controlled machine; historical wall-clock seconds are not portable targets.

Native ranges also need explicit accounting: `randint(1,6)` and `randrange(25,50)` exclude their upper endpoints, whereas the paper describes inclusive-looking ranges.
No rules or ranges are silently changed to match the prose. This PR establishes the runnable reference study inside the Metta-AI fork; independent model integration and full replication remain outstanding.

[Retained pilot evidence](results/pilots-2026-10-16) now includes all three observer audits and compressed raw records.
The network pilot has 47 individual survivors but a native reporter value of 2,544 at termination.
All three observer replays match their native price and reporter outputs byte-for-byte, covering 3,000 steps and 154,898 health records.
Notebook source excerpts are distributed under the [author's MIT license](AUTHOR_LICENSE).

## Full Phase I launch

[The declared protocol](PHASE1_PROTOCOL.md) specifies 300 runs: all three original approaches, NumPy seeds 0–99, fixed Mesa seed 42, and 1,000 steps each.
`run_phase1.py ENGINE LIBRARY NEW_OUTPUT` freezes the runner and protocol, executes one worker, and records exact commands, file hashes, exit codes and all terminal outcomes.
The live run uses the validated runtime. A free-space guard stops below 2 GiB without deleting evidence.
The ensemble remains incomplete. No inference is made from partial seed coverage, and no failed seed is silently replaced.

### Phase I independent audit

`audit_phase1.py RUN prefix|complete NEW_OUTPUT` checks the ordered seed/variant grid, pinned source hashes, runtime, every raw file, individual identities and native health records.
It reconstructs all 1,000 per-step price measurements per run, preserving missing prices and dispersion rather than imputing zero.
Full mode requires all 300 declared runs; prefix mode produces descriptive records only.

[The first five audited runs](results/phase1-prefix-2026-10-16) cover 259,228 health records and 5,000 price-step records.
Between 829 and 854 steps per run have fewer than two trades, making sample log-price dispersion undefined.
Standard seed 1 has 25 trades during steps 901–1000, each in a different step; its late-window dispersion is wholly undefined.
This is not zero dispersion or evidence of convergence. All raw inputs and derived measurements are retained.
Controls reject both premature complete analysis and a negative transaction price even after its file hash is updated.
These checks validate measurements; aggregate paper comparisons await the full ensemble.

## Released group and shared-resource configurations

The runner also accepts `groups-network`, `policy-explicit`, `common-one` and `common-multi`, mapped to the unchanged author directories in [the source audit](PHASE23_SOURCE_AUDIT.md).
Set `PYTHONHASHSEED=0` before launching Python. The runner records that value and seeds module-level policy randomness with the supplied NumPy seed; Mesa remains seeded at 42.
The already-running Phase I ensemble uses its frozen original runner and remains unchanged.
New observations count retained groups and nested group edges separately from individual population.
These measurements do not alter grouping, policies, thresholds or resource allocation.

The controlled multi-level pilot, branch observer and expanded CLI have byte-identical prices, native reporters, initial agents and health records.
However, numerical validation **fails**: 61,041 of 89,027 health records contain nonfinite holdings, beginning at step 76.
The earlier one-level diagnostic also contains infinite holdings, beginning at step 78.
Operational completion and finite recorded transaction prices do not make these economic outcomes valid.
`diagnose_resources.py NATIVE OBSERVED NEW_OUTPUT` records observer parity and explicitly reports the numerical failure; it does not convert it into a passing audit.

The controlled multi-level pilot makes 71,242 resource-aggregation calls, none with nested-group children.
Independent post-step observation finds nested-group edges on 988 of 1,000 steps, with at most seven edges and eleven retained groups.
Therefore the type-label mismatch is not exercised by the aggregation calls in this pilot and cannot explain its immediate overflow.
Shared-holding aggregation is under investigation. Historical fidelity and all paper-level conclusions remain unresolved.
A second byte-identical passive replay checks object identity in all 71,242 calls and finds no shared holdings objects among direct members.
That rules out direct dictionary aliasing in these calls; it does not rule out reaggregation of distinct copies of a prior shared pool.
No correction has been applied based on either unexercised hypothesis.

### Shared-pool double counting identified

[The passive accounting trace](results/shared-resource-diagnostic-2026-10-16/pool-accounting-proof.json) preserves all native output bytes and verifies 300 commodity sums across 150 calls.
At step 6, agents 100 and 108 initially contribute 59.16017 sugar and 57.83123 spice together.
After agent 108 acts, its holdings represent the updated pool: 62.16017 sugar and 52.24344 spice.
Agent 100 still retains its original contribution of 13.12466 sugar and 37.24246 spice.
The next calculation adds that unchanged contribution again, producing 75.28483 sugar and 89.48590 spice.
Membership is unchanged. This demonstrates reaggregation of stale contributions, rather than direct object aliasing or a nested-group type mismatch.
The model lacks a single authoritative shared balance; repeated accumulation of former contributions explains the resource amplification mechanism.
`analyze_pool_trace.py NATIVE TRACE NEW_OUTPUT` verifies native parity, every recorded sum, and this concrete double-counting event.
A corrective experiment must establish resource ownership and conservation rather than cap infinite values. No simulation correction or paper verdict is included here.

### Separate corrective experiment

`run_corrected.py ENGINE LIBRARY common-one|common-multi SEED NEW_OUTPUT` applies `shared_pool.py` without modifying either author checkout.
The experiment assigns one balance to each connected group hierarchy, sums distinct contributions once, and excludes trading within the same balance.
This changes model semantics. It is not an unchanged author replay or a validated reconstruction of the paper.
The runner measures growth, metabolism, signed balance removal on death, and total resources at every completed timestep.

[Retained corrective pilots](results/corrective-pilots-2026-10-16/summary.json) use seed zero and the existing Mesa 0.8.5 runtime.
The one-level run completes 1,000 steps with 43 survivors and 53,823 finite health records.
Recomputed conservation residuals are at most 1.82e-12 across 2,000 commodity-step observations.
However, 83 health records contain negative holdings; conservation alone does not validate survival or economic semantics.
The multi-level run conserves resources through 65 steps, then crashes at step 66.
The native policy scheduler invokes movement on an agent whose grid position is `None`.
The membership/death lifecycle requires investigation before any additional correction; neither pilot contributes a completed replication.
Compressed raw records, manifests, terminal logs, and hashes preserve both outcomes.

### Deleted groups remain in the native network

[The lifecycle trace](results/lifecycle-diagnostic-2026-10-16/summary.json) reproduces the crash with byte-identical accounting in three passive replays.
Recursive deletion removes group registry entries but leaves their object nodes and incident edges in the network.
The library adds `GroupAgent` objects as nodes, then attempts removal using string group IDs.
Deleted groups `trades_10_0` and `trades_10_2` subsequently join new parent groups.
The latter activates dead agent 163, which has already left the live registry and grid.
The corrective module now removes the actual group object and its incident edges before native recursive cleanup.
This is a separate experimental change; original source and failing evidence remain preserved.
[The combined corrective run](results/lifecycle-correction-2026-10-16/summary.json) completes 1,000 steps with 37 survivors.
Its 2,000 independently recomputed commodity-step residuals remain below 1.82e-12.
All 45,212 health records are finite, but 3,146 contain negative holdings.
Removing stale network nodes resolves this crash; negative balances and starvation timing remain unresolved.
Neither the single seed nor these experimental semantics establish a paper replication verdict.

### Negative balances can recover before death checks

`trace_starvation.py` passively records metabolism and harvesting in the corrective model.
`audit_starvation.py REFERENCE TRACE NEW_OUTPUT` requires byte-identical accounting, health, prices, and terminal population across all 1,000 steps.
[The audited trace](results/starvation-diagnostic-2026-10-16/summary.json) contains 103 shared-balance metabolism events leaving a commodity negative.
In 99 harvesting events, a previously negative balance returns above both death thresholds.
At step 21, agent 133 reduces shared sugar from 4.31772 to -0.68228.
Agent 186 then harvests two sugar, restoring the same pool to 1.31772 before its death check.
The shared pool belongs to agents 43, 133, and 186. Raw events preserve identities and balances.
The author policy checks death before metabolism, unlike the ordinary agent step, which checks afterward.
This permits debt and recovery under the corrected pooling semantics; it is not simply a reporting artifact.
Moving that check changes the model and requires a separately labeled sensitivity experiment.
The current results retain the author order; no negative-replication verdict follows from these diagnostics.
