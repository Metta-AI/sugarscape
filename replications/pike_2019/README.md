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

### Death-order sensitivity

`run_starvation_order.py` changes only the group policy's death-check order, retaining the shared-balance and network-node corrections.
It consumes first, checks the acting member for death, then trades if alive, matching the ordinary agent order.
Its separate `sensitivity.json` records the change, source hash, and runtime versions.
Both seed-zero runs complete 1,000 steps; [raw outputs and comparisons](results/starvation-order-2026-10-16/comparison.json) are retained.

| Configuration | Survivors before → after | Negative health records before → after |
| --- | --- | --- |
| One level | 43 → 45 | 83 → 9 |
| Multi-level | 37 → 46 | 3,146 → 20 |

These are single-seed sensitivities, not ensemble estimates or comparisons against the paper's survival means.
Checking the acting member afterward does not guarantee nonnegative shared balances for every surviving member.
Shared-pool exhaustion still requires an explicit model rule; neither clamping debt nor killing all group members is justified by this experiment.
`audit_corrected.py RUN NEW_OUTPUT` reconstructs accounting, reconciles every timestep's individual identities with population, and checks finite health and positive prices.
All four comparison runs pass those measurement checks; the new runs' maximum accounting residual is 3.64e-12.
A missing-agent control fails population reconciliation. Measurement validation does not establish economic validity or historical fidelity.

## Phase II parameterization

`run_groups.py ENGINE LIBRARY explicit|network THRESHOLD none|movement SEED NEW_OUTPUT` selects the paper's thresholds 1, 5, or 10 and group policy.
It retains the original model and library rules; the explicit threshold comparison and native network threshold argument are declared configuration changes.
Each output includes `configuration.json`; its nested runner manifest also identifies the original source directory.
Do not infer enabled policy from that directory's name alone.
`run_phase2.py ENGINE LIBRARY NEW_OUTPUT` executes [the declared 600-run protocol](PHASE2_PROTOCOL.md) from frozen copies.
Full analysis requires both approaches, all three thresholds, and 100 seeds per condition.

[Default-setting controls](results/group-parameterization-2026-10-16) pass five-file byte parity for both approaches: initial agents, prices, native population, health, and identity/group observations.
The explicit control enables the released movement policy; the network control leaves policy disabled.
The controls cover 2,000 steps and 95,036 reconciled health records, with exactly 1,000 adapter calls per run.
The frozen Phase II ensemble has launched with one worker. Its 600-run result grid remains incomplete; controls do not substitute for those runs.

### Expanded Phase I audit

[The 46-run prefix audit](results/phase1-expanded-prefix-2026-10-16/provenance.json) validates 2,364,707 health records and 46,000 price-step measurements.
It verifies the ordered declared prefix, source and raw-file hashes, individual identities, and notebook price definitions.
The snapshot retains the audit, exact ledger, and derived price records; its provenance identifies the retained full raw evidence directory.
The 300-run ensemble remains incomplete. No aggregate paper comparison or equivalence conclusion is inferred from this prefix.

### Phase II independent audit

`audit_phase2.py RUN prefix|complete NEW_OUTPUT` validates the ordered six-condition grid and every recorded configuration, runtime, source hash, and raw-file hash.
It reconciles per-step identities with finite health records and reconstructs native notebook price measurements without filling undefined dispersion with zero.
Full mode requires all 600 declared runs; prefix mode makes no aggregate comparison.
[The first two conditions](results/phase2-prefix-2026-10-16) cover explicit and network grouping at threshold one, seed zero, without movement policy.
Both complete 1,000 steps; 102,529 health records and 2,000 price-step measurements pass the independent audit.
All raw condition outputs, the frozen ledger, and derived measurements are retained.
Controls reject premature full analysis and a changed policy, even when the changed configuration's recorded file hash is updated.
The ensemble continues from its frozen sources; this prefix does not increase the completed-paper count.

## Released high-focus policy selects the wrong extreme

The paper says high-focus groups move using the member with the highest sugar or spice holding.
Both released `step_high` methods instead replace their selected member when the next member's maximum holding is smaller.
Their syntax trees are identical despite differing surrounding files.

`trace_movement_policy.py` passively records original member holdings and the values perceived during movement.
`audit_movement_policy.py NATIVE TRACE NEW_OUTPUT` requires five-file byte parity and independently checks every selected holding.
[The network threshold-ten, seed-zero trace](results/movement-policy-diagnostic-2026-10-16/audit.json) completes 1,000 steps with 4,319 high-focus calls.
Every call selects the member with the smallest maximum holding; all 4,319 differ from the largest member maximum.
Initial agents, identities, health, population, and price outputs match the uninstrumented run byte-for-byte.
The original data, passive trace, source hashes, and audit are retained.

This is a confirmed released-code/paper-description discrepancy, not a verdict on the unidentified historical experiment version.
Movement-policy ensembles must identify the released selector explicitly and keep any corrected-highest experiment separate.
The Phase II no-policy ensemble does not invoke this policy and continues unchanged.

### Highest-holding correction experiment

`run_high_focus.py ENGINE LIBRARY APPROACH THRESHOLD SEED NEW_OUTPUT` reverses only the high-focus comparator.
It saves the original and corrected methods; syntax-tree comparison verifies exactly one `>` to `<` change.
Author checkouts remain unchanged. No shared-resource corrections are loaded.

[The network threshold-ten, seed-zero experiment](results/highest-correction-2026-10-16/comparison.json) completes 1,000 steps with 31 survivors, versus 35 under the released selector.
The corrected passive replay verifies all 260 high-focus calls select the largest member maximum.
Five complete output files match byte-for-byte, and 44,742 health records reconcile with surviving identities.
This single-seed difference does not estimate the ensemble effect or establish historical fidelity.

An initial observer launcher incorrectly omitted the correction after lint removed its side-effect import.
Its selection audit rejected the run despite its configuration label; the failed trace and executed source are preserved.
The replacement launcher asserts that the corrected function is installed before execution.
The audit checks actual selections rather than trusting labels. Both released and corrected selector modes remain available.

## Full movement-policy ensemble

[The Phase III movement protocol](PHASE3_MOVEMENT_PROTOCOL.md) declares 1,200 trajectories: 100 paired seeds, both grouping approaches, thresholds 1/5/10, and released versus corrected-highest selectors.
`run_phase3_movement.py ENGINE LIBRARY NEW_OUTPUT` freezes all six source/protocol files, runs one worker, and records commands, exits, completions, and hashes.
The original shared-resource model and its corrective experiments are outside this ensemble.
Each corrected run retains its original and modified high-focus function, making the selector distinction reviewable.
The ensemble has launched; full-grid independent analysis and all aggregate comparisons remain pending.
The first seed and known pilots remain included without outcome-based selection.

The highest-selector audit now also pins the original method's syntax tree to both author source files in `high_focus_source.json`.
This prevents matching altered original/corrected files from passing merely because they differ by one operator.
The syntax-tree hash uses the declared Python 3.11 runtime; other interpreter versions are explicitly rejected for this check.
[Source-validation evidence](results/highest-source-validation-2026-10-16/audit.json) retains the passing full pilot and two rejected controls.
Changing both saved methods or adding an extra consumption call to only the corrected method fails before output comparison.

## Restored-session prefix audits

Fresh process checks confirmed all three existing ensemble workers; no simulation was restarted.
[Retained audit snapshots](results/restored-prefix-audits-2026-10-16) validate 90/300 Phase I runs and 18/600 Phase II runs.
These cover 4,722,197 and 936,904 health records, respectively, plus 108,000 price-step records in total.
Each audit rechecks configuration, runtime/source pins, raw-file hashes, agent identities and price definitions.
The snapshots include compressed audit reports, completed-run ledgers, reconstructed price measurements and manifests.
Raw simulation files remain in the explicit evidence directories recorded in each provenance file; they are not duplicated in these snapshots.
Both ensembles remain incomplete, and these prefix audits establish no aggregate paper result.
Phase III has no completed grid condition at this snapshot; its new auditor remains unpublished pending end-to-end validation.

## First completed movement-policy condition

[The first grid condition](results/phase3-first-condition-2026-10-16) completes 1,000 steps for explicit grouping, threshold one, seed zero and the released selector.
`audit_phase3_movement.py RUN prefix|complete NEW_OUTPUT` validates all 43,026 health records and reconstructs 1,000 price-step records.
There are 37 final individual survivors; the native reporter is a different quantity and is not used as individual population.
Four steps have undefined sample price dispersion because they contain fewer than two trades; they remain missing.

The retained archive contains the complete condition, frozen sources/protocol, manifest, completion-ledger snapshot and execution logs.
Every archived file was read back and verified against its original bytes.
The auditor rejects the incomplete grid in complete mode and rejects an altered policy even when the configuration hash is updated.
At this first-condition snapshot, the full workflow had validated only the released-selector path.
Earlier corrected-pilot/source audits remain separate evidence and do not substitute for that pending grid validation.
One of 1,200 conditions is complete at this snapshot. No selector comparison or paper-level result is inferred.

## First completed movement-policy pair

[The first pair audit](results/phase3-first-pair-2026-10-16) now validates both released and corrected-highest grid paths for explicit grouping, threshold one and seed zero.
Both trajectories complete 1,000 steps; the combined audit checks 80,809 health records and reconstructs 2,000 price-step records.
The corrected trajectory ends with 32 individual survivors, compared with 37 in the released trajectory.
It has four steps without trades and 34 steps without defined sample price dispersion; missing measurements remain missing.
This single pair establishes no ensemble-level selector effect.

The corrected-condition archive retains raw outputs, frozen sources, original and modified methods, configuration, hashes, execution logs and the two-run ledger.
The earlier first-condition archive supplies the released raw outputs. Every new archive member was verified against its original bytes.
An unaltered relocated copy passes the full auditor. Adding an extra consumption call to the corrected method fails despite an updated file hash.
Changing the saved original method also fails its pinned-source check despite an updated hash. Both rejected controls fail before producing audit output.
The complete 1,200-condition grid and paper-level comparisons remain pending.

## Disk-stop checkpoint and portable segment audits

All three ensemble workers exited at their existing 2 GiB free-space guards.
[Independent checkpoint audits](results/disk-stop-and-segments-2026-10-16/provenance.json) validate 194/300 Phase I runs, 61/600 Phase II runs, and 29/1,200 movement-policy runs.
They reconcile 14,775,821 health records and 284,000 price-step records; earlier published prefixes are included, not added again.
The remaining ordinal ranges are `[194,300)`, `[61,600)`, and `[29,1200)`, totaling 1,816 conditions.
Source manifests and original completion-ledger hashes bind the [remaining-work plan](results/disk-stop-and-segments-2026-10-16/remaining-plan.json).
No cloud continuation has launched at this checkpoint.

Each auditor now accepts `--start-index` for a contiguous portion of its original declared grid.
`--recorded-root` validates original command paths when evidence is audited from a different location, without rewriting historical records.
Full-ensemble mode still requires ordinal zero and every required condition.
Real final conditions from all three stopped runs pass as relocated nonzero segments, covering 166,767 health records and 3,000 price-step records.
These validation replays add no simulation coverage.
Six controls reject incorrect starting ordinals and incomplete full-ensemble claims before creating audit output.

```bash
python replications/pike_2019/audit_phase1.py /downloaded/segment prefix /new/audit --start-index 194 --recorded-root /original/execution/segment
```
