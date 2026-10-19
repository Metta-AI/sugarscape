# Blueprints for Machine Ethics (2024)

**Incomplete replication. Original configurations recovered; the paper explicitly names the v2024.1 release used here.**

All **2,000/2,000 original homogeneous configurations** are complete and audited, with 5,063,268 observations.
[The complete union](results/homogeneous-complete-2026-10-18) validates all 500 seeds for each model without double counting.
All four Table 3 rows match the published counts exactly under the released plotter's classification.
All four models now have complete published-curve comparisons; [Bentham](results/bentham-figures-2026-10-18) adds 24,229 vertices across five figures.
Figure 6 matches all-cause deaths for all four models, while the released plotter counts only starvation and combat.
[The pre-submission v2024.3 plotter](results/plotting-history-2026-10-18) adds aging deaths and matches all 19,970 Figure 6 vertices across four models.
This explains a released definition consistent with the paper; the exact historical plotting revision remains unidentified.
[The Bentham released-parser check](results/bentham-parser-2026-10-18) also matches all 30,006 independently aggregated values.

Latest deposited-runtime coverage is **873/1,200 inputs and 2,800,520 observations**.
[The terminal Bentham audit](results/runtime-bentham-terminal-2026-10-18) retains the six-hour timeout and excludes the interrupted input.
[The restored-environment continuation](results/runtime-environment-recovery-2026-10-18) has passed setup and started both native workers.
The selfishness and mixed-society sweeps, longer horizons, remaining figure analysis beyond the homogeneous curves, and historical runtime claims remain incomplete.
[The corrected remaining-input inventory](results/supplement-inventory-complete-controls-2026-10-18) contains 99,992 original inputs after excluding eight audited inputs. It includes two paired-runtime controls missed by the earlier inventory. No new sweep jobs have been dispatched.
Earlier sections retain dated execution history and superseded checkpoint counts.

[Published paper, author-hosted PDF](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2024:blueprints-for-machine-ethics.pdf)
(DOI 10.1109/ACCESS.2024.3519139). [Numeric targets](published_targets.json) were visually checked against PDF pages 12 and 15.

## Original experiment inputs

The authors' separate [datasets repository](https://github.com/digital-terraria-lab/datasets)
contains `blueprints-homogeneous.zip`, introduced June 12, 2024 in commit `9e78c44ca9cffefbb3593a0d490f1631da3239f2`.
The [retained archive and audit](results/archive-audit-2026-10-15) pin repository revision
`0b50404c2529aa0ab08ce14c7f7abfe30fab837e`, preserve its Unlicense, and validate:

- Exactly 2,000 configurations: four decision models and 500 identical shared seeds.
- Every paired input differs only in decision-model name and output filename.
- Every configuration key and nonoperational default matches the May 28, 2024 release `Glucose/v2024.1`,
  commit `b9ca671ab7591c7b3606f2d76c33eda344d626d1`.

The archive contains inputs, not result trajectories. Section IX on PDF page 20 explicitly identifies v2024.1.
The live `Glucose/v2024.1` tag resolves to our pinned commit `b9ca671ab7591c7b3606f2d76c33eda344d626d1`.
[Release evidence](results/release-and-runtime-audit-2026-10-17/release.json) corrects earlier notes that inferred the release solely from schema.
Historical producer manifests remain unchanged; full results and runtime equivalence remain to be validated.

The original decision models are `rawSugarscape`, `altruisticHalfLookaheadBinary`,
`egoisticHalfLookaheadBinary`, and `benthamHalfLookaheadBinary`.
The released model dispatch selects the half-lookahead behavior from these names.
The 500 original seeds are retained in the audit, with no substitutions.

## Correction to provisional runs

Our earlier runner used v2024.4 and the plain `altruist`, `egoist`, and `bentham` names.
Those names do not select the archived decision semantics. The later release also changes the configuration schema and model code.
All four provisional seed-1-through-500 batches were intentionally interrupted after this discovery, each exiting 130.
Their complete and partial outputs remain in the external evidence directory; no run is counted as paper replication.
The seed-zero pilots and storage check retained below remain operational evidence for the old setup only.
The old runner and protocol are preserved in Git history through commit `96c7221`; current commands use original archived inputs.

## Reproduce an archived input

Requires Python 3.11 and Pydantic 2.12.3. Use the pinned release in a separate checkout.
`run.py` verifies archive and source hashes, checks the complete configuration schema, and changes only the logfile path.
The original config bytes and effective configuration are both retained.
The complete horizon is 5,000 steps or extinction; the runner checks every timestamp, seed, finite metric, and terminal state.

```sh
python replications/blueprints_2024/run.py /path/to/v2024.1 \
  replications/blueprints_2024/results/archive-audit-2026-10-15/blueprints-homogeneous.zip \
  altruisticHalfLookaheadBinary158402133555746433.config /new/pilot
```

`run_batch.py` selects the original seed list in numerical order and retains complete lossless trajectories.
It verifies decompression byte-for-byte before removing only its own newly generated redundant raw copy.
The full protocol is in [ENSEMBLE_PROTOCOL.md](ENSEMBLE_PROTOCOL.md).

## Required comparisons

Table 3 reports extinct / worse-or-equal / better counts: Raw 348/5/147; Altruist 344/10/146;
Egoist 331/5/164; Utilitarian 0/0/500. Classification uses terminal population relative to the initial 250.
Compare original-input counts directly, preserving all seeds and investigating every mismatch.

Table 4's printed altruist row is internally inconsistent: 68.8% + 5.0% + 29.2% = 103%.
Its 5.0% worse category also conflicts with Table 3's 10/500 = 2.0%.
The target file preserves the printed values. This arithmetic inconsistency does not establish a simulation result.

The complete study also requires homogeneous time trajectories, the 101-factor selfishness sweep,
heterogeneous societies, computational-horizon checks, and a historical-versus-fork behavior audit.
The authors also publish `blueprints-selfishness.zip`, `blueprints-heterogeneous.zip`, and `blueprints-runtimes.zip`.
These must be inspected before constructing their experiment protocols.
No unexplained discrepancy or operational pilot counts as a completed replication.

## Current execution evidence

Two original-input pilots are running as independent processes, using the same first archived seed.
Their first 908 completed observations pass timestamp, population, and scalar/array finite-value checks.
This is partial execution evidence; neither full-run completion nor deterministic replay has been established yet.
Two earlier original-input attempts were intentionally stopped after discovering the old release's three array-valued log fields.
The validator now checks those arrays and all scalar metrics explicitly; the model was not modified.
All interrupted outputs remain preserved. Full batches await the complete pilot and repeat checks.

The supplementary archive audit confirms 50,500 selfishness configurations, 49,500 mixed-society configurations,
and 1,200 runtime configurations covering 100 seeds at 500, 5,000, and 50,000 timesteps.
The selfishness archive supplies the older singular `agentDecisionModel` field alongside a default plural field.
The original release explicitly normalizes the singular field into the plural field before simulation (`sugarscape.py:958–961`).
Ignoring that native normalization would incorrectly classify all selfishness configurations as raw agents.

## Corrected original-input pilot completed

Both [independent runs](results/original-pilot-2026-10-15/repeatability.json) of original seed 158402133555746433 complete all 5,000 steps.
The 5,001 observations are byte-identical, with final population 1,219.
Both original configurations, compressed raw trajectories, source hashes, execution logs, and independent full-trajectory audits are retained.
Each run took approximately 28 minutes on this machine while other studies were running.

The author's `plots/plot.py` counts equal initial/final population with the better category.
The earlier runner grouped equality with worse; this boundary is now corrected before full ensembles start.
The pilot's population increases, so its grouping is unaffected.
`audit_batch.py` independently verifies original seed intervals, input hashes, effective configuration, compressed trajectories, every observation, and the author's classification rule.

All four original 500-seed homogeneous ensembles have now started using the corrected model names and archived inputs.
Each model runs the complete sorted original seed schedule, including a fresh first seed; pilot evidence remains separate.
The batches retain every completed trajectory and check available storage before each next simulation.
No full-ensemble outcome is claimed until all required intervals pass the independent audit.

## Utilitarian batch recovery

The first full utilitarian batch stopped at the disk-space guard after four completed original seeds; no fifth run had begun.
[Retained recovery evidence](results/bentham-prefix-recovery-2026-10-15) preserves the failure log, original manifests, native trajectories, and independent audit.
All 20,004 observations pass configuration, trajectory, and outcome checks.
The audit explicitly marks the declared 500-seed interval incomplete; these four successes cannot establish the paper's aggregate result.

`audit_batch.py ARCHIVE BATCH NEW_OUTPUT --allow-prefix` validates a contiguous completed prefix without changing its original manifest.
The default still requires the entire declared interval.
The resumed batch uses the unchanged runner with `--start 4 --stop 500` in a fresh directory, preserving the original remaining 496 seeds.
The first four and resumed interval must be reconciled together before any full-schedule conclusion.

## Recovery after filesystem exhaustion

[Four additional prefix audits](results/disk-recovery-2026-10-15/summary.json) validate 99 completed runs: raw 65, egoist 17, altruist 16, and one resumed utilitarian run.
The previously audited four utilitarian runs remain separate, yielding five completed utilitarian seeds overall.
All original configurations, hashes, timestamps, finite metrics, and terminal conditions pass.
These are incomplete intervals, not estimates of the paper's full outcomes.

Native processes exited 120 while the filesystem was exhausted; their empty stderr does not independently identify the cause.
Failure logs, manifests, ledgers, and audits are retained here; complete and partial trajectories remain in the recorded external evidence directory.
Recovery retries interrupted seeds at sorted indices 65, 17, 16, and 5, respectively, without skipping or replacing them.

## First interrupted seeds recovered

[Raw and altruist retries](results/disk-retry-2026-10-15) both finish 5,000 steps and pass the full-interval independent audit.
Both retain the original interrupted seeds, with 10,002 total observations and final populations above the initial count.
Original partial outputs remain preserved. Neither retry is counted twice in the seed schedule.
Raw resumes from index 66 and altruist from index 17 in fresh directories; egoist and utilitarian retries are still running.
All recovered prefixes and remaining intervals require reconciliation before comparing the full 500-seed outcomes.

The egoist retry also completes all 5,000 steps, ending with population 495.
Its 5,001 observations pass the independent full-interval audit and are retained with the other recovered seeds.
The remaining egoist batch resumes at index 18; the utilitarian retry is still running.

The utilitarian retry completes all 5,000 steps, ending with population 1,264.
Its 5,001 observations pass the independent audit; the remaining interval resumes at index 6.
All four interrupted seeds have now been recovered and their remaining original schedules resumed.
Utilitarian evidence spans original indices 0–3, the earlier resumed index 4, recovered index 5, and the running interval 6–499.
No full 500-seed model ensemble is yet complete.

## Process-restart recovery

All four batch processes were absent on revalidation, with their original tool handles unavailable.
[Independent prefix audits](results/process-recovery-2026-10-16) validate 104 further completed runs and 191,425 observations.
The stop cause is not inferred from missing handles. Complete and partial native outputs remain in the external evidence directory.
Fresh batches resume original indices 143 (raw), 29 (altruist), 28 (egoist), and 11 (utilitarian).
No completed seed is rerun or dropped; interrupted seeds are retried in new directories.
Full 500-seed conclusions still require reconciliation of every interval.

## Audited storage and machine-crash recovery

[Four further prefix audits](results/storage-recovery-2026-10-16) validate 212 completed simulations and 368,833 observations.
Raw and utilitarian batches stopped at the 1 GiB free-space guard. Altruistic and egoistic runs failed with incomplete diagnostics during disk pressure.
The failed altruistic trajectory is invalid JSON and is excluded. Exact child-process failure causes remain unestablished.
All complete and partial files remain preserved.

`reconcile_coverage.py ARCHIVE NEW_OUTPUT AUDIT...` checks intervals against original sorted seeds and requires repeated records to agree.
[Reconciled coverage](results/storage-recovery-2026-10-16/coverage.json) contains 423 unique simulations and 757,511 observations.
Two repeated pilot records match and are counted once. A conflicting repeated trajectory hash is rejected before output creation.

| Model | Audited original indices | Completed / required | Resume index |
| --- | --- | ---: | ---: |
| Raw | [0,263) | 263 / 500 | 263 |
| Altruistic | [0,74) | 74 / 500 | 74 |
| Egoistic | [0,66) | 66 / 500 | 66 |
| Utilitarian | [0,20) | 20 / 500 | 20 |

After the machine crash, process inspection found no surviving task workers. All four retained prefixes passed the full trajectory audit again.
The unchanged original schedules resumed from these exclusive-stop boundaries in fresh `-005` directories after storage recovered.
[The launch record](results/storage-recovery-2026-10-16/crash-resume.json) identifies commands, hashes, retained evidence, and new outputs.
Partial counts do not establish full homogeneous results; selfishness, heterogeneous studies, and historical-code alignment remain incomplete.

## Post-crash continuation audit

[The expanded coverage audit](results/post-crash-prefix-2026-10-16/coverage.json) adds 47 completed original configurations without seed substitution.
It validates 470 unique simulations and 872,046 observations across the four homogeneous models.
Two overlapping pilot records remain counted once. No partial trajectory contributes a completed seed.

| Model | Audited original indices | Completed / required |
| --- | --- | ---: |
| Raw | [0,283) | 283 / 500 |
| Altruistic | [0,88) | 88 / 500 |
| Egoistic | [0,76) | 76 / 500 |
| Utilitarian | [0,23) | 23 / 500 |

Each added trajectory passes original configuration, seed order, file hash, finite metrics, and terminal-horizon/extinction checks.
The snapshot retains interval audits, manifests and exact audited ledgers; provenance identifies the preserved full raw trajectories.
All four continuation workers remain active. These partial outcome counts do not establish Table 3 or the full paper's conclusions.

## Later checkpoint and raw-model resumption

[Reconciled coverage](results/late-prefix-and-raw-resume-2026-10-16/coverage.json) validates 508 unique simulations and 980,090 observations.
The audited original-index intervals are raw `[0,299)`, altruistic `[0,98)`, egoistic `[0,84)`, and utilitarian `[0,27)`.
Earlier pilot overlaps are counted once; the two excluded duplicate records agree.
The snapshot retains independent audits, source manifests, audited ledger prefixes, and raw-evidence locations.

The raw-model batch exited at its existing 1 GiB disk guard after index 298; its terminal status and log were inspected.
After free space recovered to 12 GiB, a new `-006` directory resumed at index 299 with the unchanged source and original seed order.
The three other workers remained active and were not restarted.
No previous complete or partial evidence was removed.
These remain partial homogeneous results; no Table 3, selfishness, mixed-population, or full-paper completion is claimed.

## Source verification and relocated evidence

The batch auditor now checks every recorded Python source hash against all nine files extracted from the pinned release’s Git objects.
It also verifies archive identity, hash-seed setting, command/configuration paths, declared logfile changes, and result input identity.
`--recorded-root ORIGINAL_BATCH_DIRECTORY` audits relocated evidence without rewriting its historical paths.
The simulation producers are unchanged.

[Fourteen new raw-model runs](results/source-audit-2026-10-16/raw006-audit.json) pass these checks across16,847 observations, extending that model’s validated interval to[0,313).
A copied batch produces an identical audit report with its original execution root.
Changing one recorded source hash rejects the copied evidence before an output report is created.
[Reconciled coverage](results/source-audit-2026-10-16/coverage.json) now contains522 unique runs; two agreeing pilot duplicates remain excluded.
The other model counts remain98 altruistic,84 egoistic,27 Bentham in this checkpoint.
Earlier audits have not all been rerun under the new source checks, and neither the2,000-run homogeneous grid nor the full paper is complete.

## Complete checkpoint source re-audit

[All24 original-seed batches](results/source-reaudit-2026-10-16/coverage.json) now pass the strengthened auditor, including earlier retained prefixes and two repeated pilots.
Every recorded Python source hash matches the pinned release; all archived configurations and compressed trajectories pass integrity and outcome checks.
The reconciled checkpoint contains529 unique runs and1,022,241 observations, excluding two agreeing duplicate records.
Validated prefixes are313 raw,99 altruistic,89 egoistic,28 Bentham runs, each from its original seed schedule.
No gaps or conflicting duplicates were found.
This supersedes the earlier limitation that old batches had not received source-hash checks.
It does not establish that the pinned release is the paper’s exact historical revision or complete the2,000-run homogeneous experiment.

## Runtime experiment inputs

[The runtime archive audit](results/release-and-runtime-audit-2026-10-17/runtime-inputs.json) checks all 1,200 configurations.
It contains 100 shared seeds per model at 500, 5,000 and 50,000 steps; none overlaps the homogeneous archive’s 500 seeds.
Within each model and seed, only the horizon and logfile differ.
Paper page 19 describes the same 500 seeds, and every Table 6 group totals 500.
[All 36 Table 6 counts](published_targets.json) are now transcribed from the rendered page 20.
Replaying the deposited runtime archive alone cannot establish the claimed 500-seed comparison.
Keep that archive separate from a declared reconstruction using the homogeneous seeds and changed horizons.
The archived runtime grid is incomplete; a first condition is recorded below. The reconstructed 500-seed experiment remains unstarted.
Earlier historical-release caveats above are superseded by the paper’s explicit release statement.

## First deposited runtime execution

[The original runtime input](results/runtime-pilot-2026-10-17/audit.json) uses raw Sugarscape, seed 1071049487305188627, and 500 steps.
The filename was selected lexicographically before outcomes; only its logfile path changed.
The paper-named v2024.1 release completes all 500 steps with 431 agents, retaining 501 observations.
All nine source files, original/effective configuration, finite metrics, timestamp sequence, seed and trajectory hashes pass independent checks.
The run took 7.83 seconds on this machine; that is execution provenance, not a historical runtime comparison.
This contributes one of the deposited runtime archive's 1,200 configurations, not a completion of Table 6 or its claimed 500-seed experiment.
The archived runner has a 1,800-second timeout and 2 GiB preflight disk guard. Compressed output is retained alongside its audit and native logs.

## Runtime batch continuation

The remaining 99 original raw-model 500-step inputs run sequentially in lexicographic filename order, excluding the completed pilot.
[The frozen launch and first audit](results/runtime-batch-2026-10-17) retain the two-hour batch budget and 2 GiB disk guard.
`audit_runtime_batch.py ARCHIVE RUN NEW_OUTPUT` requires all 99 conditions; `--allow-prefix` explicitly audits partial coverage.
The auditor checks archived inputs, source/runner hashes, configuration changes, completion order, all native file hashes and finite trajectories.
Ten new conditions pass across 3,087 observations; with the earlier pilot, runtime coverage is 11/1,200 configurations and 3,588 observations.
A full-mode invocation against the incomplete live batch rejects before creating output.
Only the ten audited native directories are archived here; active partial runs are excluded.
The complete-batch success path remains unexercised until the producer finishes. This does not establish Table 6.

## Complete archived raw-model 500-step group

[Full-mode auditing and reconciliation](results/runtime-raw500-complete-2026-10-17/reconciliation.json) now cover all 100 deposited raw-model 500-step inputs.
The 99-condition producer exited zero; full validation passes, superseding the earlier unexercised-success-path limitation.
The earlier pilot is counted once, giving 100 unique seeds and 29,004 observations without gaps or overlaps.
Outcomes are 65 extinctions, six surviving populations below 250, and 29 above 250; none ends at exactly 250.
The final native archive contains only the 89 conditions absent from the earlier ten-condition archive.
This completes one group in the deposited 1,200-input runtime archive; the other groups remain unstarted.
The archive's 100 seeds differ from the paper's claimed 500-seed schedule, so these counts are not a direct Table 6 replication verdict.

## Runtime groups and bounded intervals

`run_runtime.py ENGINE ARCHIVE MODEL STEPS NEW_OUTPUT --start START --stop STOP --seconds BUDGET` runs original archived configurations in lexicographic filename order.
It supports the four archived models and horizons of 500, 5,000 and 50,000 steps, with immutable source snapshots and a 2 GiB disk guard.
Only the logfile changes. The supplied budget bounds the entire interval; timeout or native failure preserves partial evidence and stops execution.
`audit_runtime.py ARCHIVE RUN NEW_OUTPUT` independently validates the declared interval; `--require-group` additionally requires all 100 inputs from index zero.
`--allow-prefix` explicitly marks partial intervals. A completed short interval never becomes a completed group.
[An original altruistic 500-step pilot](results/runtime-runner-2026-10-17/audit.json) reaches extinction at step 134; all 135 observations pass.
Full-group mode rejects this one-condition interval before output creation. The source and native outputs are retained.
The 5,000/50,000-step paths and complete-group success path remain unexercised for this new runner.

## Linux portability and longer archived horizons

[Two native Linux runs](results/linux-portability-2026-10-17/comparison.json) match the corresponding local raw and altruistic trajectories byte-for-byte across 636 observations.
Both use original 500-step inputs, Python 3.11.14, and the pinned v2024.1 model. Independent source/configuration/raw-output audits pass.
These are deliberate portability repeats, adding no ensemble coverage and proving no universal platform equivalence.
The auditor accepts `--recorded-root ORIGINAL_PATH` for relocated evidence without changing historical configuration paths.
Re-auditing the existing local altruistic pilot produces the identical report after this change.

The same two-core node now runs the previously unstarted raw and altruistic 5,000-step groups: 100 original configurations each, two workers.
Each interval has a six-hour budget; the outer command is bounded at 21,720 seconds and preserves evidence on disk.
The original 500-step local assignments remain disjoint. The launch is retained; full outputs and audits are still pending.
After normal completion, the wrapper archives the evidence and leaves the node’s ordinary idle window for retrieval.

A [second two-core launch](results/runtime-long5000-second-launch-2026-10-17/summary.json) assigns the remaining egoistic and Bentham 5,000-step groups, 100 original configurations each.
Both worker manifests are read back from the active node; original runner, source and archive hashes pass setup verification.
Each worker has a six-hour limit, with a seven-hour bound covering setup and execution.
The first bootstrap failed before simulation because the image uses an unprivileged account; the corrected bootstrap uses its persistent home directory.
Both launch records are retained. These assignments are disjoint from all earlier 500-step and 5,000-step groups.
All four archived 5,000-step groups are now assigned, but execution and independent full-output validation remain incomplete.

## Complete archived altruistic 500-step group

[Fresh native audits and reconciliation](results/runtime-altruistic500-complete-2026-10-17/reconciliation.json) validate all 100 original altruistic 500-step inputs across 26,212 observations.
The 99-condition producer exited zero; its complete-interval audit and a fresh pilot audit cover indices `[0,100)` without duplicates or gaps.
Outcomes are 71 extinctions, one surviving population below 250, and 28 above 250; none ends at exactly 250.
The new native archive retains all 99 batch conditions, while the earlier pilot remains in its original evidence location.
This brings audited runtime-archive coverage to 200 of 1,200 inputs across two complete groups.
The deposited 100-seed schedule differs from the claimed 500-seed paper schedule, so no Table 6 replication verdict follows from these counts.

## Complete archived egoistic 500-step group

[The full-group native audit](results/runtime-egoistic500-complete-2026-10-17/audit.json) validates all 100 original egoistic inputs and 26,129 observations after the producer exits zero.
The generic auditor's `--require-group` success path now passes on a complete real group, superseding the earlier unexercised-success-path limitation.
Outcomes are 69 extinctions, two surviving populations below 250, and 29 above 250; none ends at exactly 250.
All original native files, the completion ledger and archive checksum are retained.
Audited runtime-archive coverage is now 300 of 1,200 configurations across three complete 500-step groups.
The Bentham group remains active. These archived 100-seed results do not establish the paper's claimed 500-seed Table 6 results.

## Bentham runtime prefix

The [sealed 33-condition prefix](results/runtime-bentham500-prefix-2026-10-17/audit.json) adds 16,533 independently checked observations from the original 500-step runtime archive.
Every retained run reaches step 500 with population above 250; none equals the initial population.
The native files, frozen ledger, configurations, source hashes, and runner are retained in a portable archive.
A second audit after extraction verifies the archived evidence against its original execution paths.

The runtime archive now has 333 of 1,200 conditions audited, totaling 97,878 observations.
The Bentham producer remains active for the remaining conditions; this prefix does not establish a full-group or Table 6 verdict.

## Complete raw 5,000-step runtime group and disjoint continuations

[The full native raw-Sugarscape group](results/runtime-raw5000-complete-2026-10-17/audit.json) passes all 100 original 5,000-step conditions and 186,504 observations. Outcomes are 65 extinctions, four surviving populations below 250, and 31 above 250; none equals 250. The 31,269,889-byte archive retains complete native files, original configurations, hashes, and terminal receipts. Linux paths are preserved in the manifest and explicitly supplied to the portable audit.

The Bentham 500-step predecessor reached its two-hour cap with exactly 87 complete conditions and a partial condition at index 87. Its [terminal receipt, traceback, and fresh prefix audit](results/runtime-continuations-2026-10-17) are retained. All 87 completed runs reach step 500 above the initial population, covering 43,587 observations. After confirming both predecessor processes absent, a new bounded output directory continues only indices `[87,100)`. The interrupted original files are untouched.

These latest audits cover 487 unique runtime-archive configurations and 311,436 observations: three complete 500-step groups, the 87-condition Bentham prefix, and the complete raw 5,000-step group. Earlier prefixes are included, not added twice. These remain the deposited 100-seed groups, not the paper’s claimed 500-seed Table 6 ensembles.

The freed cloud worker now runs the previously unstarted raw 50,000-step group `[0,100)`, one worker with a six-hour native cap and bounded outer command. The original altruistic 5,000-step worker continues on the same two-CPU node. The other two 5,000-step groups remain active on their existing node. The new 50,000-step launch, frozen source hash, and artifact paths are recorded above; no completion is inferred from launch.

## Complete archived Bentham 500-step group

[The completed-group reconciliation](results/runtime-bentham500-complete-2026-10-17/reconciliation.json) covers all 100 deposited Bentham inputs and 50,100 observations.
The continuation exited zero after completing indices `[87,100)`; the original 87-run prefix is counted once.
The interrupted predecessor’s unfinished index 87 remains preserved outside the completed evidence archive.
All runs reach step 500 above the initial population of 250; final populations range from 683 to 1,273.

The 19,902,440-byte native archive contains every completed condition, original configuration, frozen source hash, ledger, and run receipt.
Fresh audits of both extracted segments reproduce the original audit JSON byte-for-byte.
The prefix remains honestly marked incomplete as a standalone interval; reconciliation proves the full group through disjoint ordinal coverage.

| Archived 500-step model | Extinct | Surviving below 250 | Above 250 |
|---|---:|---:|---:|
| Raw | 65 | 6 | 29 |
| Altruistic | 71 | 1 | 28 |
| Egoistic | 69 | 2 | 29 |
| Bentham | 0 | 0 | 100 |

None of these 400 outcomes equals 250.
Together with the raw 5,000-step group, current audited runtime coverage is 500 unique inputs and 317,949 observations.
These are the deposited 100-seed groups. The mismatch with the paper’s claimed 500-seed Table 6 schedule remains unresolved.
The other 5,000-step groups and raw 50,000-step group continue; no whole-paper completion is assigned.

## Complete supplementary controls

[Six original-input controls](results/supplement-controls-2026-10-17/verification.json) now complete all 5,000 steps, with 30,006 observations independently audited.
The [protocol](SUPPLEMENT_PROTOCOL.md) fixes the smallest original seed, 158402133555746433, and preserves every scientific configuration field.
Only the logfile changes; native singular-to-plural decision-model normalization is retained.

| Experiment | Original setting | Final population |
| --- | --- | ---: |
| Selfishness | 0.0 | 1,219 |
| Selfishness | 0.5 | 478 |
| Selfishness | 1.0 | 759 |
| Heterogeneous | 1 utilitarian entry / 100 | 1,128 |
| Heterogeneous | 50 utilitarian entries / 100 | 1,376 |
| Heterogeneous | 99 utilitarian entries / 100 | 1,249 |

`run_supplement.py ENGINE AUTHOR_ARCHIVE selfishness|heterogeneous ENTRY NEW_OUTPUT` executes one unchanged original input against the pinned paper release.
`audit_supplement.py AUTHOR_ARCHIVE RUN NEW_OUTPUT` independently checks archive/source/configuration hashes, every timestamp, seed, population, finite metric and terminal result.
The [lossless native artifact](results/supplement-controls-2026-10-17/native.tar.gz) contains all six trajectories, configurations, manifests, receipts and logs.
Its [export receipt](results/supplement-controls-2026-10-17/export.json) records the verified SHA-256 and 2,682,746-byte size.

[Endpoint parity](results/supplement-controls-2026-10-17/homogeneous-parity.json) matches all 5,001 trajectory records byte-for-byte against the earlier homogeneous runs.
Selfishness 0.0, 0.5 and 1.0 match altruistic, utilitarian and egoistic configurations respectively at this seed, including the local/cloud runtime difference.
Native dispatch assigns these effective factors; the utilitarian default negative factor becomes 0.5.
These three matches do not add independent homogeneous seeds or establish parity for unexecuted seeds.

The deposited selfishness and heterogeneous sweeps still contain 50,500 and 49,500 required inputs.
These six controls establish execution and measurement fidelity; they do not estimate either sweep's population curve or complete the paper.
Measured control runtimes range from 302 to 1,848 seconds on shared CPU capacity, so expansion requires explicit scheduling and duplicate exclusion.

## Alternate-runtime fidelity controls

[Six complete PyPy controls](results/runtime-controls-2026-10-17) reproduce all 30,006 retained CPython observations byte for byte.
The unchanged v2024.1 engine replayed selfishness 0, 0.5 and 1, plus heterogeneous Bentham counts 1, 50 and 99.
All six use original seed 158402133555746433 and 5,000 steps.
Only output paths changed; source hashes and original configuration values were independently checked.

The alternate runtime is PyPy 7.3.20, Python 3.11.13; the reference is CPython 3.11.14.
This environment change is explicit and is not an author-specified runtime.
`audit_runtime_controls.py PYPY_EXTRACTED CPYTHON_EXTRACTED NEW_REPORT` independently verifies the complete archive against the previously audited supplementary controls.
The published archive retains all six raw outputs, configurations, logs and completion records.

Elapsed times came from different workloads sharing the same host, so they are not controlled speedup estimates.
One seed across six configurations does not establish universal runtime equivalence.
Two additional paired runtime checks were interrupted by provider host loss; snapshot inventory is queued before continuation.
No production runtime or completion status changes here.
These replays add no independent scientific seeds and do not complete either sweep or the paper.

## Sequential runtime and memory comparison

[Eight completed sequential controls](results/sequential-runtime-complete-2026-10-18) reproduce all 40,008 original-control observations byte for byte.
At selfishness 0 and 0.5, PyPy mean elapsed times are 398.89 and 85.46 seconds, versus CPython's 1,248.79 and 280.27 seconds.
The measured mean speedups are 3.13× and 3.28×; maximum resident memory ranges from 168,280–356,764 KiB for PyPy, versus 34,240–87,052 KiB for CPython.
Each condition has two repetitions per runtime, ordered CPython / PyPy / PyPy / CPython on the same two-CPU allocation.

```sh
python audit_sequential_runtime.py \
  results/sequential-runtime-complete-2026-10-18/native.tar.gz \
  results/supplement-controls-2026-10-17/native.tar.gz /path/to/new-audit.json
```

These results support bounded supplementary scheduling, with the measured memory increase accounted for.
They are not universal runtime equivalence or historical-paper timing claims.
The archive is preserved locally and in external storage; the completed owned node is stopped.
These are repeated inputs, so the remaining supplementary worklist stays at 99,992.

## Runtime checkpoint preserved after provider host loss

[The surviving node’s checkpoint](results/runtime-surviving-checkpoint-2026-10-17) independently validates 67 egoistic and 19 Bentham 5,000-step inputs.
All 221,631 observations pass original-input, command, source, file-hash, finite-value and terminal-condition checks.
These disjoint prefixes bring audited runtime coverage to 586/1,200 inputs and 539,580 observations.
The native worker remains active; these prefixes are not complete groups.
The complete 51,728,473-byte raw archive is retained outside Git at the path and SHA-256 in `provenance.json`.

The provider declared the first runtime node lost on October 17 at 05:26 UTC; its unexported altruistic 5,000-step and raw 50,000-step outputs are unavailable.
The previously exported complete raw 5,000-step group remains retained and is not rerun.
Those lost unexported outputs receive no audit coverage credit.
The main control node has a recoverable disk snapshot; its inventory is queued before resuming incomplete cross-runtime comparisons.
A connection failure alone did not trigger any simulation restart.

## Bounded replacement and durable checkpoint transfer

[The recovery protocol and evidence](results/runtime-recovery-2026-10-17) preserve six original altruistic 5,000-step inputs, with 1,001 independently audited observations.
They occupy indices `[0,1)` and `[12,17)`; repeated recovery controls are counted once.
Audited runtime coverage is now 592/1,200 unique inputs and 540,581 observations.
The five workflow controls were selected for short trajectories known from the completed 500-step group; they supply no ensemble estimate.

The remaining altruistic inputs are partitioned without overlap: `[1,12)` runs locally, and `[17,100)` is assigned to a replacement CPU node.
That node also receives the raw 50,000-step group `[0,100)`.
The previously completed raw 5,000-step group is excluded.
Every native group has a six-hour limit; the cloud workflow has an eight-hour outer limit and at most two workers.
Incomplete intervals remain incomplete at their limits.

`run_recovery.py SOURCE PLAN NEW_OUTPUT` executes the unchanged pinned native runner and seals completed-output checkpoints every 30 minutes.
`collect_recovery.py NODE COMMAND NEW_LOCAL_OUTPUT` copies each sealed archive off the provider and checks its size and SHA-256.
The collector reads only that command; a lost or exited command ends collection without restarting simulations.
Both sides retain manifests and logs; native failures remain visible and do not count as completed simulations.
Collected archives still require `audit_runtime.py` before scientific coverage credit.

The complete recovery workflow was exercised with the real author engine: one input was checkpointed, the parent was terminated, and all owned worker processes exited.
Resuming only the four missing inputs reproduced all five uninterrupted trajectories byte for byte.
Independent audits cover the full run, the recovered prefix, and the continuation.
A live provider export also passed the collector’s full transfer and hash checks; final checkpoints retain native exit metadata and logs.
The original interrupted files remain preserved.

The local assignment is active and the cloud assignment is queued; neither launch establishes completion.
Primary CPython 3.11.14 remains unchanged.

## Second retained runtime checkpoint

[The second checkpoint](results/runtime-surviving-checkpoint-002-2026-10-17) validates 85 egoistic and 20 Bentham 5,000-step inputs, with 243,990 observations.
The earlier 86 records match exactly, including trajectory hashes and manifests; they are replaced in coverage totals, not counted twice.
The 19 additional inputs contribute 22,359 observations, bringing audited runtime coverage to 611/1,200 inputs and 562,940 observations.
Both groups remain incomplete, and the native worker continues. The complete 56,929,748-byte archive is retained off-node at the documented path and SHA-256.
No elapsed-time comparison or completed-paper claim follows from this prefix.

## Additional runtime controls

[Two recovered paired controls](results/runtime-pairs-2026-10-17/audit/audit.json)
use original selfishness inputs 0.37 and 0.73 with seed 175856849482260318.
All 10,002 trajectory observations match byte-for-byte between CPython 3.11.14
and PyPy 7.3.20 / Python 3.11.13. Final populations are 1,252 and 1,287.

The audit verifies original archive configurations, source pins, both interpreters'
exit receipts, complete ledger membership, and every native trajectory byte. The existing
supplementary auditor independently checks each CPython trajectory and all finite measurements.
Re-extracting the published archive reproduces all audit reports exactly.

These extend the earlier six controls to a second seed and two nonbinary settings.
They do not establish universal runtime equivalence, complete a supplementary sweep,
or add homogeneous seeds. Shared-host elapsed times remain descriptive.

Run `audit_runtime_pairs.py EXTRACTED_ARCHIVE BLUEPRINTS_SELFISHNESS_ZIP NEW_OUTPUT`
to reproduce the audit. The complete native archive and its storage hash are retained.

## Complete raw homogeneous ensemble

The [later audited checkpoint](results/homogeneous-checkpoint-2026-10-17-2019/coverage.json)
validates 1,387 unique original-seed runs and 2,761,461 observations. The three active
batch audits verify source pins, archived configurations, compressed trajectory hashes,
and every retained observation. Coverage reconciliation excludes two duplicate records.

| Model | Validated original seeds | Required |
| --- | ---: | ---: |
| Raw Sugarscape | 500 | 500 |
| Altruistic | 424 | 500 |
| Egoistic | 345 | 500 |
| Bentham | 118 | 500 |

The published checkpoint contains audit reports and their hashes. Raw trajectories
remain in the retained evidence directories named by those reports. The earlier
completed intervals remain referenced in the coverage manifest. These partial counts
do not establish the remaining Table 3 proportions or complete the paper.

[The complete raw comparison](results/homogeneous-checkpoint-2026-10-17/raw-table3-comparison.json) covers all 500 original seeds and 819,456 observations.
The final resumed interval exited successfully; earlier intervals and the losslessly recovered disk-interrupted seed complete the original schedule without substitution.
Released plotting semantics reproduce Table 3’s numerical counts exactly: 348 extinct, 5 surviving below 250, and 147 at or above 250.
One run ends at exactly 250. Applying the paper’s prose categories instead gives 348 extinct, 6 worse-or-equal, and 146 strictly better.
The boundary trajectory and its hash are retained; this reporting mismatch is not silently corrected.
The three other homogeneous ensembles, temporal comparisons and broader experiments remain incomplete. This result does not complete the paper.

## Complete raw time-series reconstruction

[The raw time-series evidence](results/raw-timeseries-2026-10-17) reconstructs all 500 original inputs and 819,456 observations.
The unmodified v2024.1 parser and an independent NumPy aggregation agree on all 30,006 scalar values across 5,001 timesteps.
Population agrees exactly; maximum floating-point error is 5.83e-11, from summation order in total wealth.
The source parser pads missing post-extinction timesteps with zeros and divides by all 500 seeds.
Normalized deaths and wealth divide ensemble means; they do not average per-seed ratios.

At timestep 5,000, mean population is 242.964, mean time to live is 4.87384, total wealth is 35,906.5932,
and wealth per population is 147.785652. These describe the complete raw ensemble, not the other models.
[The six-panel figure](results/raw-timeseries-2026-10-17/timeseries.pdf) retains this limited scope.
The raw curves are compared with the paper below. Other models’ curves and cross-model comparisons remain unvalidated until their full ensembles are available.

```sh
python replications/blueprints_2024/audit_timeseries.py /path/to/coverage.json /path/to/v2024.1 rawSugarscape /new/timeseries
python replications/blueprints_2024/plot_timeseries.py /new/timeseries
```

The first command requires a complete audited 500-seed interval, its referenced raw evidence, NumPy and the pinned author checkout.
It stages lossless inputs for the original parser, retaining them outside Git, with a 4 GiB free-space guard.
The plot command requires Matplotlib. Full parser logs, input hashes, numerical series and plots are retained.

## Raw curves compared with published vector figures

[The vector audit](results/raw-figures-2026-10-17) extracts the black Raw Sugarscape paths from PDF pages 13–14.
Axes, legends and panel bounds were visually checked. Integer timesteps are recovered from the horizontal coordinates.
The comparison tolerance is 0.005 PDF points, fixed before the initial comparison and retained for the diagnostic below.
Figures 4, 5, 7, 8 and 9 match all 24,370 extracted vertices; maximum ordinate error is 0.004318 PDF points.
This covers population, time to live, age at death, total wealth and wealth per population for the complete raw ensemble.

Figure 6 exposes a measurement-definition difference. The released plotter uses only starvation and combat deaths.
That definition fails at 4,936 of 4,996 vertices, with maximum ordinate error 45.6583 PDF points.
Adding the already-recorded disease and aging deaths reproduces all 4,996 vertices within the unchanged tolerance;
maximum error is 0.003699 PDF points. No simulation inputs, trajectories or models were changed.
At timestep 5,000, the rates are 0.00124298 for starvation plus combat and 0.01555786 for all four causes.
Aging contributes 3.478 deaths per seed, explaining the gap from the original plotter's 0.302 starvation deaths.
The broader death definition was investigated after observing the mismatch; it is reported as a diagnostic, not a preregistered confirmatory result.
Both the failing comparison and the matching diagnostic are preserved.

```sh
python replications/blueprints_2024/audit_raw_figures.py /path/to/paper.pdf /path/to/raw-timeseries /new/figure-audit
```

Requires PyMuPDF 1.26.5 and NumPy 1.26.4. The command checks the paper and audited input hashes,
then reconstructs the additional death counts from all 500 retained trajectories.
Compressed CSVs retain every extracted coordinate, reproduced value and initial residual.
Only the raw homogeneous model is covered; this does not complete the paper.

## Completed local runtime recovery interval

The recovered altruistic 5,000-step interval `[1,12)` completed all 11 assigned inputs
with zero exit status. The [full-interval audit](results/runtime-local-recovery-complete-2026-10-17/audit.json)
validates 30,869 observations: five extinct populations and six at or above initial population.
The earlier two- and eight-input prefixes are contained exactly and receive no additional credit.

[Reconciliation](results/runtime-local-recovery-complete-2026-10-17/coverage.json)
checks duplicate trajectory hashes, observation counts and final populations across
published runtime audits. That checkpoint established **622/1,200 inputs and 593,809 observations**.
This adds 11 inputs and 30,869 observations to the previously published 611-input total.

The sealed 6,870,636-byte checkpoint has SHA-256
`5271402f55099c4f2835f662b2e04271d99823b37a220c5373cd09d41ef594ec`.
Its receipt, native completion marker, supervisor exit status, manifest and audit ledger
are retained. The native completion marker is retained separately because the checkpoint
format seals per-run outputs without that marker. The full audit also checked it directly.
Cloud intervals `[17,100)` and raw 50,000-step `[0,100)` remain separate active work.
This completes the assigned recovery interval, not the full 100-input group or paper.

## Runtime deadline and recovered checkpoint audits

[Independent archive audits](results/runtime-ensembles-2026-10-17) bring unique runtime
coverage to **662/1,200 inputs and 712,954 observations**: 40 new inputs and 119,145 observations.
Every repeated input agrees on raw trajectory hash, observation count, and final population.

The surviving egoistic 5,000-step group completed all 100 inputs: 69 extinct, one below
250 agents, and 30 at or above 250. Its complete trajectories contain 165,629 observations.
The companion Bentham group completed 26 inputs and 130,026 observations before its
six-hour deadline interrupted the next input. That incomplete trajectory is retained
in the original archive but excluded from the audit and completion count.

The first checkpoint from the separate recovery job adds 17 altruistic 5,000-step
inputs, indices 17–33, and two raw 50,000-step inputs. These contain 17,367 and
50,113 observations respectively. This job continues on its existing allocation.

The completed node now runs disjoint remaining work: Bentham 5,000-step inputs 26–99
and previously unstarted egoistic 50,000-step inputs 0–99. Each worker has a six-hour
budget. The supervisor seals completed outputs every 30 minutes and preserves full-group
completion markers. No resumed output is included in the coverage above.
The full paper remains incomplete; deposited runtime inputs are not the complete published sweeps.


### Audited resumed-worker checkpoints

[Two retained cloud checkpoints](results/runtime-checkpoints-2026-10-17) add 22 unique
runtime inputs and 72,640 observations. Reconciliation now covers **684/1,200 inputs
and 785,594 observations**, requiring every overlapping raw-trajectory hash to agree.
The new data include Bentham 5,000-step indices 26–27, seven egoistic 50,000-step
inputs, twelve additional altruistic 5,000-step inputs, and one additional raw
50,000-step input. Every counted trajectory reaches its declared horizon or extinction.
Both cloud jobs continue; checkpoints are incomplete intervals, not full-ensemble results.
The deposited runtime archive remains distinct from the paper's 500-seed Table 6 experiment.


## Second runtime checkpoint reconciliation

[The next two retained checkpoints](results/runtime-checkpoints-second-2026-10-17)
add 11 unique original inputs and 120,931 observations. Independent
coverage now reaches **695/1,200 inputs and 906,525 observations**.
Every overlap agrees on seed, endpoint, outcome, observation count, and raw trajectory
hash. All previous audit hashes were checked before combining the records.

Recovery covers altruistic 5,000-step indices 17–48 and raw 50,000-step indices 0–8.
The second runtime worker covers Bentham 5,000-step indices 26–29 and egoistic
50,000-step indices 0–6. Early extinction is retained as a completed trajectory.
These remain partial archive groups, with no full-paper or Table 6 verdict.

## Third runtime checkpoint reconciliation

[Recovery checkpoint five and round-two checkpoint four](results/runtime-checkpoints-third-2026-10-17)
add 35 unique inputs and 103,941 observations. Verified coverage reaches
**730/1,200 deposited runtime inputs and 1,010,466 observations**.
Every previous audit hash and every overlapping result record matches exactly.
Native archive sizes and SHA-256 hashes match the download receipts.

The new coverage extends altruistic 5,000-step inputs through index 77, Bentham
5,000-step inputs through index 33, and egoistic 50,000-step inputs through index 8.
Raw 50,000-step coverage remains nine inputs. Each trajectory reaches its horizon
or extinction. The four active groups remain incomplete, and these deposited
100-seed groups do not establish the paper's 500-seed Table 6 results.

## Fourth runtime checkpoint reconciliation

[Recovery checkpoint six and round-two checkpoint five](results/runtime-checkpoints-fourth-2026-10-17)
add nine unique inputs and 75,469 observations. Verified coverage reaches
**739/1,200 deposited runtime inputs and 1,085,935 observations**.
All earlier audit hashes and every overlapping result record match exactly.
Downloaded archive sizes and SHA-256 hashes match their receipts.

The added inputs comprise five altruistic 5,000-step runs, two raw 50,000-step
runs, and two Bentham 5,000-step runs. Coverage now reaches altruistic index 82,
raw index 10, and Bentham index 35. Egoistic 50,000-step coverage remains nine inputs.
All counted trajectories finish their configured horizon or become extinct.
These remain incomplete groups, distinct from the paper's 500-seed Table 6 experiment.

## Fifth runtime checkpoint: 759 inputs validated

[Recovery checkpoint eight and round-two checkpoint seven](results/runtime-checkpoints-fifth-2026-10-17)
add 20 distinct deposited inputs and 146,617 observations. Deduplicated coverage is
**759/1,200 inputs and 1,232,552 observations**. Every prior audit hash and overlapping
result row agrees exactly.

All four native trajectory audits pass. Recovery covers altruistic 5,000-step indices
17–95 and raw 50,000-step indices 0–12. Round two covers Bentham 5,000-step indices
26–39 and egoistic 50,000-step indices 0–9. These are incomplete declared intervals.

The two new-input archives retain only newly completed trajectories and current metadata.
Overlaying them on the preceding published checkpoint archives reproduces all four
full audit JSONs exactly. Reconstruction manifests pin both base and new archives;
original full-checkpoint transfer receipts remain separate evidence.

This remains coverage of the deposited 100-seed groups, not the paper's 500-seed
Table 6 experiment. No complete runtime-table or whole-paper verdict is claimed.

## Sixth runtime checkpoint audit

[The latest checkpoint evidence](results/runtime-checkpoints-sixth-2026-10-17/coverage.json)
adds 31 validated original archive inputs and 222,544 recorded states. Total
coverage is 790/1,200 inputs and 1,455,096 states. All overlapping original ledgers
and audit records agree exactly; no repeated prefix is counted twice.

The altruistic 5,000-step group now covers all 100 archived inputs. Seven of twelve
groups are complete. Remaining coverage is Bentham 5,000 steps (52/100), raw
50,000 steps (27/100), egoistic 50,000 steps (11/100), and both altruistic and
Bentham 50,000-step groups (0/100 at this audit).

Four full trajectory audits verify original configurations, native source pins,
commands, hashes, finite recorded values, and terminal outcomes. Compact deltas
plus retained prior archives reconstruct all 1,206 files of both new checkpoints,
including original terminal logs and receipts. Partial timed-out seeds remain
preserved and receive no completion credit.

Both remote batches ended at their six-hour limits. Bounded continuations reuse
the owned nodes: raw indices 27–99, Bentham 5,000-step indices 52–99, egoistic
50,000-step indices 11–99, and altruistic 50,000-step indices 0–99. These are
registered work, not completed evidence. The 100-input deposited archive remains
distinct from the paper's 500-seed Table 6 experiment; no whole-paper credit.

## First direct-storage continuation readback

[The stored checkpoint audit](results/runtime-storage-readback-2026-10-17/audit/audit.json)
validates Bentham runtime indices 52–53: two complete 5,000-step trajectories and
10,002 states. The object-storage download matches the sealed source SHA-256
`dca7f451a6237e00743fe8d69934308b9a9583d35ffa958e48b9702c348f09f6`.
The exact downloaded archive, export receipts, and frozen ledger are retained.

[Reconciled coverage](results/runtime-storage-readback-2026-10-17/coverage.json) is now
**792/1,200 runtime inputs**, with 1,465,098 states. The new records do not overlap
previously audited inputs. Bentham 5,000-step coverage is 54/100; seven other model/horizon
groups remain complete. This does not establish the paper's separate 500-seed timing claim.

Extract the checkpoint, restore each `trajectory.json` from its adjacent gzip, and run
`audit_runtime.py` with `--allow-prefix` and recorded root
`/home/dev/sugarscape/blueprints-runtime-round2-002/runs/benthamHalfLookaheadBinary-5000`.
The expected ordinal interval is `[52,54)`; the active producer continues toward index 100.

## Runtime archive: third restored checkpoints

[The reconciled checkpoint](results/runtime-storage-readback-third-2026-10-17/coverage.json)
contains 804 unique original inputs and 1,541,060 native observations. It adds
12 inputs and 75,962 observations to the prior 792-input checkpoint.

The two downloaded archives contain six raw 50,000-step inputs, one altruistic
50,000-step input, and seven Bentham 5,000-step inputs. Two Bentham records overlap
the prior checkpoint; every retained field and trajectory hash agrees exactly.
They are counted once. The altruistic input ends in extinction at step 134; it
is a completed original input, not a completed 50,000-step survival trajectory.

Both archives pass download SHA-256/size checks and full trajectory audits against
the original configurations, pinned source, seed intervals, native exit receipts,
finite observations, and terminal conditions. Their 10,363,994-byte and
8,615,540-byte raw archives remain in task-owned storage with retrieval metadata
and hashes; compact audits and ledgers are retained here.

`reconcile_runtime.py ARCHIVE PREVIOUS_COVERAGE NEW_OUTPUT AUDIT...` rechecks all
previous audit hashes, reconstructs prior coverage, and rejects conflicting
overlap before adding new records. The complete original grid has 1,200 inputs.
Neither this checkpoint nor full deposited-grid completion replaces the paper's
500-seed Table 6 experiment. The two native continuation jobs remain running.

## Deferred Bentham 50,000-step group

[Two disjoint plans](results/bentham50000-launch-2026-10-17) cover original deposited
Bentham runtime indices `[0,50)` and `[50,100)`. This previously unstarted group
retains all 100 original configurations and seeds. No new horizon or acceptance
criterion is introduced. The known 100-input versus 500-seed paper discrepancy remains.

Commands `cmd-2ypbn` and `cmd-52ges` wait for the existing runtime batch `cmd-byham`
to write its terminal receipt. They then reuse its owned CPU2 node, Python 3.11.14,
pinned original engine, configuration archive, and unchanged validated runners.
Both runner hashes are checked before execution; each shard has a new output root.
The two shards run concurrently after the earlier batch, with one native process each.

Each shard permits six hours of simulation, with a 22,000-second execution bound
including checkpoint completion. At $0.0024 per node-minute, the shared node's added
execution costs at most $0.88, excluding idle time. Each storage collector has a
2 GiB cumulative transfer cap and a ten-hour deadline. Completed seeds are sealed
in half-hour checkpoints; incomplete seeds remain retained without completion credit.

Inputs passed shell syntax checks and remote SHA-256 verification before launch.
The commands are currently waiting: no new completed input or replication is claimed.
Recorded wall times remain hardware/workload-qualified; this launch does not
establish equivalence to the paper's timing experiment.

## Bentham runtime checkpoint six

[The downloaded checkpoint](results/runtime-storage-readback-sixth-2026-10-17)
validates 14 original Bentham 5,000-step inputs, indices `[52,66)`, and 70,014 observations.
Seven inputs overlap previously audited trajectories and agree exactly; seven add 35,007 observations.
Reconciled coverage is **811/1,200 unique runtime inputs and 1,576,067 observations**.
Bentham 5,000-step coverage is now 66/100. Seven other model/horizon groups remain complete.

The 17,215,267-byte storage download matches its sealed SHA-256
`da540b50a75ba63c6c7612e7ea5af2a4b1d950910898732d8c483c4b9169e1dc`.
The existing auditor verifies every raw trajectory, native exit receipt, original configuration,
source pin, and terminal condition. Reconciliation rechecks previous audit hashes and rejects conflicting overlaps.
Compact audits, frozen ledger, export receipts, and retrieval metadata are retained here;
the raw archive remains in task-owned object storage and the local evidence directory.
This checkpoint does not establish the paper's separate 500-seed timing experiment or complete the study.

## Homogeneous checkpoint: 1,489 original inputs

[The frozen checkpoint](results/homogeneous-checkpoint-2026-10-17-2313)
adds 102 unique original inputs and 229,935 observations, bringing coverage to 1,489 inputs and 2,991,396 observations.
The three native batches remain active. Their completed ledgers were frozen before auditing;
active unledgered seeds are excluded and original completed outputs remain untouched.

| Model | Audited inputs | Dead | Worse | Better or equal |
| --- | ---: | ---: | ---: | ---: |
| Raw | 500/500 | 348 | 5 | 147 |
| Altruistic | 475/500 | 328 | 8 | 139 |
| Egoistic | 381/500 | 247 | 5 | 129 |
| Bentham | 133/500 | 0 | 0 | 133 |

These use the released plotting rule, including equality with better; the paper's prose boundary differs.
Incomplete prefixes are not full-ensemble proportions or additional completed studies.
All recorded source pins, original configurations, compressed/raw trajectory hashes, finite observations and terminal conditions pass.
Reconciliation verifies prior audit hashes and original seed ordering; two agreeing duplicate pilot records still count only once.
The retained manifest, frozen ledger, audits and reconciliation command identify every included trajectory.

## Runtime recovery checkpoint seven

[The downloaded recovery checkpoint](results/runtime-storage-recovery-seventh-2026-10-17)
validates 20 original raw 50,000-step inputs, indices `[27,47)`, and three altruistic 50,000-step inputs, indices `[0,3)`.
The checkpoint contains 352,836 observations. Seven inputs overlap prior evidence and match exactly.
The remaining 16 add 301,879 observations, bringing coverage to **827/1,200 unique runtime inputs and 1,877,946 observations**.
Raw 50,000-step coverage reaches 47/100; altruistic 50,000-step coverage reaches 3/100.
Seven other model/horizon groups remain complete.

The 69,593,761-byte archive matches its sealed SHA-256
`c71d02f5a694854a8645c1d2b5cc5ae550a91e7a4efe725218fca743a4f31d01`.
Every completed run passes original configuration, source pin, native exit, full trajectory hash, finite observation and terminal-condition checks.
Reconciliation verifies prior audit hashes and all overlapping record fields, including raw trajectory hashes.
Compact audits, frozen ledgers and export receipts accompany the readback record; full native outputs remain preserved locally and in object storage.
These are completed deposited runtime inputs, not validation of the paper's separate 500-seed timing experiment.
The study remains incomplete.

## Runtime recovery checkpoint ten

[Two sealed checkpoint audits](results/runtime-checkpoint10-2026-10-18)
validate 59 completed trajectories. All 37 overlaps match prior observations,
endpoints, outcomes, seeds and raw trajectory hashes exactly.
The 22 new unique inputs add 296,360 observations, bringing deposited runtime
coverage to **849/1,200 inputs and 2,174,306 observations**.

| Model and horizon | Audited input indices in checkpoint | Total unique coverage |
| --- | --- | ---: |
| Raw, 50,000 steps | `[27,55)` | 55/100 |
| Altruistic, 50,000 steps | `[0,3)` | 3/100 |
| Bentham, 5,000 steps | `[52,75)` | 75/100 |
| Egoistic, 50,000 steps | `[11,16)` | 16/100 |

Seven other model/horizon groups remain complete.
Both archives match producer-sealed hashes: 99,304,134 bytes for the recovery
checkpoint and 48,581,048 bytes for the second node's checkpoint.
Readback receipts retain paths and SHA256 hashes; source manifests, frozen ledgers,
exact audit commands and reconciliation results accompany the compact evidence.
Full native trajectories remain retained locally and at their recorded remote paths.
Every completed trajectory passes original configuration, source pin, native exit,
finite observation, full trajectory hash and terminal-condition checks.
The original processes continue; no incomplete trajectory receives coverage credit.
This does not validate the paper's separate 500-seed timing experiment or complete the study.

### Qualification for parallel homogeneous Bentham execution

[The bounded cloud qualification](results/bentham-parallel-qualification-launch-2026-10-18)
replays one completed original seed and requires an exact full-trajectory hash match.
At qualification launch the local producer remained unchanged; the later handoff is documented below.
A future parallel handoff must freeze disjoint inputs after rechecking the local producer.
The qualification repeat itself adds no coverage or completion credit.

### Prepared parallel-handoff safeguards

The historical `run_parallel_handoff.py` required a typed handoff plan, local stop receipt, sealed completed ledger,
and a successful cloud qualification whose actual compressed trajectory matches the pinned original hash.
It verifies the local completed seed prefix and permits only its exact complement through index 499.
The original single-seed runner and batch runner must match the qualified hashes.
Thirty-two workers write separate one-input batches and preserve every process exit and log.
Nonzero exits remain explicit, and the enclosing workflow fails if any input is unfinished.
Execution receipts alone do not add coverage; existing trajectory auditors must validate every completed batch.

The production launcher must impose an outer deadline before the instance lease expires,
leaving time to seal and collect evidence. The subsequent qualified production launch is documented below.
Ruff and CLI checks passed before launch. Qualification and handoff execution evidence follows below.

### Coverage when parallel inputs finish out of order

`reconcile_coverage.py` reports every `validated_intervals` range and every `missing_indices` entry.
`validated_runs` counts the union; `validated_interval` remains only its contiguous prefix from zero.
`next_seed` identifies the first missing input, including a gap before later completed inputs.
Duplicate inputs still require identical trajectory results and receive no extra credit.
The full-grid flag requires all 500 inputs in each of the four models.

### Qualified parallel Bentham handoff

[The cloud qualification](results/bentham-parallel-handoff-2026-10-18) exactly reproduces all 5,001 reference observations.
After independent audit, the local producer was stopped with its completed ledger preserved.
Its final prefix is 152/500 Bentham inputs, bringing the homogeneous union to 1,592/2,000.
The remaining 348 inputs run on 32 workers with disjoint directories and an outer deadline before lease expiry.
The interrupted local input remains preserved and uncredited; cloud execution alone adds no coverage.

### First audited parallel Bentham outputs

[The sealed partial ensemble](results/bentham-parallel-prefix-2026-10-18)
adds 29 distinct original inputs and 145,029 native observations. Every trajectory
passes configuration, source-pin, exit, hash and outcome checks. Fresh extraction
reproduces all 29 audits byte-for-byte. Union reconciliation raises Bentham
coverage to 181/500 and homogeneous coverage to 1,621/2,000.

Inputs finish out of order; missing indices remain explicit. Five other attempts
(indices 157, 159, 165, 177 and 181) exited 124 at the frozen one-hour limit.
Those are execution failures, receive no simulation or scientific credit, and
remain required. Their partial outputs stay on the original worker disk.
The archive contains the sealed attempt ledger and completed inputs only.
Other workers continue under the existing deadline; no inputs were restarted.

### Second parallel prefix and current Egoist prefix

[The new audited evidence](results/homogeneous-prefix-2026-10-18-002) adds
32 completed Bentham inputs and 41 completed Egoist inputs to the prior union.
Coverage is now 1,694/2,000: Altruist 500, Raw 500, Egoist 481 and Bentham 213.
Overlapping prior prefixes agree exactly and receive no duplicate credit.

The 32 remote inputs each contain all 5,001 observations. Fresh extraction
of their public archive reproduces every audit byte-for-byte. The local Egoist
prefix rechecks 415 completed inputs from its declared interval [66,500),
covering [66,481) and 733,793 observations from retained native trajectories.
Its active next input is excluded.

Eight Bentham attempts have timed out: indices 157, 159, 165, 177, 181, 196,
197 and 203. Their partial trajectories remain retained remotely, and every
index remains required. This checkpoint does not substitute seeds or shrink
the ensemble. Production remains active under the existing deadline; the
full homogeneous grid and whole-paper study remain incomplete.

### Bentham 50,000-step failure and bounded retry

[The retained failure](results/runtime-bentham50k-failure-2026-10-18) shows
`cmd-2ypbn` exited one after its first native process received SIGKILL.
The interval [0,50) completed no inputs. Its 47,608,503-byte partial trajectory
remains on the original node and receives no completion credit. Memory-event
counters were not exposed; this is not a confirmed out-of-memory diagnosis.

The unchanged interval is registered as `cmd-utvgx` on the former Thaler
CPU8 node with 32 GiB memory. An explicit wake request queued that node.
The run is bounded to 390 minutes, about $3.744 of compute at the observed
rate, plus at most the normal 15-minute idle window ($0.144).
Its collector is bounded separately and preserves sealed outputs.
The existing [50,100) command remains live; no intervals overlap.
The retry is pending capacity, so no new scientific outcome is claimed.

### Bentham retry rebuilt after unrecoverable provider disk loss

[The replacement record](results/runtime-bentham50k-replacement-2026-10-18) preserves the provider terminal state and corrects a runner-schema omission found during fresh setup. The original low50,000-step interval now executes on a fresh32GiB node. No completed input is credited before collection and audit.

### Two complete Bentham 50,000-step runtime inputs

[The recovered high-interval checkpoint](results/runtime-bentham50k-high-2026-10-18/README.md) adds 100,002 validated observations from original inputs [50,52). Exact reconciliation reaches 856/1,200 deposited runtime inputs without counting overlapping prefixes twice. The rest of [50,100) remains required.

### Process ownership for new selected-input batches

`run_selected.py` replaces the historical parallel handoff runner after its terminal child-process escape.
It launches each input in its own process group and stops all group members before returning.
[Native workflow controls](results/selected-runner-lifecycle-2026-10-18) cover deadlines, external interruption, and a completed original trajectory.
Its typed JSON plan declares the model, exact original indices, worker count, per-input seconds, and total seconds.
Allocations must be disjoint from live producers and already audited inputs.
Run `python run_selected.py ENGINE ARCHIVE PLAN NEW_OUTPUT`; audit every completed batch before counting it.
An incomplete allocation exits 124 and preserves all partial outputs. Historical code remains in Git and sealed evidence.

[The next disjoint Bentham allocation](results/bentham-remaining-launch-2026-10-18) assigns 152 required inputs to a bounded CPU-only node. It was queued at registration; Linux qualification gates production.

### Additional Raw and Altruist runtime inputs

[Five original inputs](results/runtime-memory-prefix-2026-10-18) add 150,328 independently audited observations. Exact reconciliation reaches 861/1,200 deposited runtime inputs. Two Raw inputs end in natural extinction; the other three complete 50,000 steps. The producer continues, and the full paper remains incomplete.

### Bentham runtime low interval

[Two original Bentham inputs](results/runtime-bentham50k-low-2026-10-18) add 100,002 independently audited observations. Both complete 50,000 steps. Exact reconciliation reaches 863/1,200 deposited runtime inputs; the full paper remains incomplete.

### Two additional original Bentham retries

[Inputs 197 and 203](results/bentham-timeout-retry-2026-10-18-003) add 10,002 audited observations and complete all 5,000 steps. Exact deduplication reaches 1,835/2,000 homogeneous inputs, including Bentham 335/500. All remaining inputs and other paper experiments remain required.

## Ninth original-input timeout recovery

[Input 216](results/bentham-timeout-retry-2026-10-18-004) adds 5,001 independently audited observations over the unchanged 5,000-step horizon.
The deduplicated ensemble now contains 1,836/2,000 inputs, including Bentham 336/500.
All 164 missing Bentham inputs and the remaining paper experiments are still required.

## Further runtime checkpoint

[Five more original inputs](results/runtime-memory-prefix2-2026-10-18) add
100,546 audited observations after exact deduplication. Runtime coverage reaches
868/1,200 deposited inputs and 2,650,189 observations. Three new inputs become
extinct; two complete 50,000 steps. The full paper remains incomplete.

## Further original Bentham retries

[Three further original inputs](results/bentham-timeout-retry-2026-10-18-005)
complete 5,000 steps and add 15,003 audited observations. Exact reconciliation
reaches 1,839/2,000 homogeneous inputs, including Bentham 339/500. The remaining
161 original Bentham inputs and other paper experiments remain incomplete.

Final local retry evidence in `results/bentham-timeout-retry-2026-10-18-006` adds original inputs 232 and 237: 1,841/2,000 homogeneous inputs, Bentham 341/500. The supervisor stopped at its disk-space guard; seven assigned inputs never started. No restart or completion credit for those inputs.

The seven local inputs blocked by disk space are assigned to a separate bounded two-CPU execution in `results/bentham-disk-recovery-launch-2026-10-18`. They are disjoint from the existing 152-input queue. Completion counts remain unchanged pending audited outputs.

Three additional Raw runtime inputs in `results/runtime-memory-prefix3-2026-10-18` raise coverage to 871/1,200 and 2,700,518 observations. One completes 50,000 steps; two end in natural extinction. The verified delta and previous checkpoint reconstruct the full sealed evidence exactly.

## Runtime batch terminal audit

[The final bounded batch audit](results/runtime-memory-terminal-2026-10-18) adds one original 50,000-step trajectory.
Exact coverage reaches 872/1,200 deposited runtime inputs and 2,750,519 observations.
Both workers reached their time limits; partial trajectories receive no credit. Final evidence is exported, and the node is stopped with disk intact.

## Complete homogeneous experiment grid

[All 2,000 original homogeneous inputs](results/homogeneous-complete-2026-10-18) now pass audit, with 5,063,268 observations and no missing seeds.
Bentham reaches at least the initial population in all 500 runs. Every original model retains its full seed schedule and extinction outcomes.
Sweeps, longer horizons, runtime requirements, and remaining figure analysis still prevent whole-paper completion.

## Runtime environment recovery

[The restored-environment recovery](results/runtime-environment-recovery-2026-10-18) preserves the previous missing-Git failure and restores all required command-line dependencies before unchanged simulations. The fresh bounded continuation targets only unfinished original inputs. No new runtime completion is claimed until checkpoint audit.

## Bentham terminal runtime audit

[The final Bentham checkpoint](results/runtime-bentham-terminal-2026-10-18) adds one complete original 50,000-step input. Exact reconciliation reaches 873/1,200 deposited runtime inputs and 2,800,520 observations. The six-hour timeout and unfinished fourth input remain retained without completion credit.

### Bounded 0.37 cohort launched

[The frozen protocol](results/selfishness037-protocol-2026-10-18/README.md) requests the remaining 499 original seeds at selfishness 0.37. Two full CPython/PyPy pairs gate eight-worker bulk execution; all original horizons remain intact. The 9.5-hour simulation budget is bounded to roughly $8. [Both complete runtime qualification pairs](results/selfishness037-pilots-2026-10-18) now pass byte-exact trajectory comparison and local audit. Two new unique inputs add 10,002 observations; the original supplementary sweep has ten completed inputs and 99,990 remaining. No condition aggregate or paper completion is claimed.

### Audited runtime continuation

[Four more original runtime inputs](results/runtime-continuation-prefix-2026-10-18) add 50,468 audited observations: one full 50,000-step trajectory and three native extinctions.
Exact deduplication reaches 877/1,200 deposited inputs and 2,850,988 observations. The bounded producer continues; unfinished inputs receive no credit.
The deposited 100-seed schedule still does not fulfill the paper's 500-seed Table 6 experiment.

## First bulk selfishness-0.37 checkpoint

[The first 25 bulk inputs](results/selfishness037-prefix-2026-10-18) pass independent local audit for all 125,025 observations. All reach 5,000 steps. The archive matches its sealed export hash; all member hashes and producer/local audit pairs match. The reconciled inventory now counts 35 unique completed supplementary inputs and 99,965 remaining. Condition 0.37 has 28 of 500 completed inputs. This completion-order prefix supplies no condition aggregate or paper completion credit; the bounded batch continues.

### Second selfishness-0.37 checkpoint

[Another 25 inputs](results/selfishness037-second-prefix-2026-10-18) pass independent audits covering 120,191 observations. Twenty-four finish 5,000 steps; one ends naturally in extinction at step 166. The inventory now recognizes audited native extinction and verifies contiguous trajectory times and terminal population. The previous inventory and remaining-input CSV reproduce exactly, except for the recorded planner source hash.

Supplementary coverage reaches 60 unique inputs, with 99,940 remaining. Selfishness 0.37 has 53/500 completed inputs. No completion-order aggregate or whole-paper completion is claimed.

### Second runtime continuation checkpoint

[Seven cumulative inputs](results/runtime-continuation-second-prefix-2026-10-18) pass the runtime audit, matching all four earlier inputs exactly. Three new inputs add 100,172 observations. Coverage reaches **880/1,200 deposited runtime inputs and 2,951,160 observations**. The paper’s different 500-seed timing schedule remains unresolved.


### Additional audited supplementary and runtime checkpoints

[The third selfishness-0.37 prefix](results/selfishness037-third-prefix-2026-10-18) adds 25 disjoint inputs and 120,190 observations. Twenty-four reach step 5,000; one ends naturally in extinction at step 165. Supplementary coverage reaches 85 original inputs; condition 0.37 reaches 78 of 500.

[The third runtime prefix](results/runtime-continuation-third-prefix-2026-10-18) adds one input and 50,001 observations after matching seven overlapping trajectories exactly. Runtime coverage reaches 881 of 1,200 deposited inputs and 3,001,161 observations. The complete archive is hash-verified and retained in task object storage and local evidence. Neither prefix completes a paper result.

### Fourth supplementary checkpoint audit

[Two further checkpoints](results/selfishness037-fourth-prefix-2026-10-19) add 50 disjoint original inputs and 240,451 audited observations. Forty-eight reach step 5,000; two end in native extinction. Local and producer audits match exactly. Reconciliation preserves all earlier inputs and reaches 135/100,000 supplementary inputs, including 128/500 at selfishness 0.37. The condition aggregate and paper remain incomplete.

### Fourth runtime continuation audit

[Three further original runtime inputs](results/runtime-continuation-fourth-prefix-2026-10-19) add 100,138 observations after eight overlapping trajectories match exactly. Coverage reaches 884/1,200 deposited inputs and 3,101,299 observations. The complete exported archive and all member hashes verify. The paper’s 500-seed timing protocol remains unresolved; no completion credit is added.

### Runtime continuation reaches its bound

[The terminal archive audit](results/runtime-continuation-terminal-prefix-2026-10-19) adds 25 original inputs and 253,312 observations. Coverage reaches 909/1,200 deposited inputs and 3,354,611 observations. Both groups reach their six-hour limits; interrupted inputs receive no credit. Their logs and exact remaining intervals are retained. The different 500-seed paper protocol remains unresolved.

### Selfishness 0.37 reaches 403 audited inputs

[Eleven further checkpoints](results/selfishness037-fifth-prefix-2026-10-19) add 275 disjoint inputs and 1,351,453 validated observations. Of these, 270 reach 5,000 steps and five end in native extinction. All local and producer audits agree. Inventory reconciliation preserves earlier evidence and reaches 403/500 inputs for condition 0.37, with 410/100,000 supplementary inputs overall. No completion-order aggregate or paper verdict is claimed.

### Remaining runtime intervals queued on the retained node

[The bounded continuation](results/runtime-continuation-launch-2026-10-19) preserves original raw indices 86–99 and altruistic indices 22–99, including interrupted inputs at full 50,000-step horizons. The owned node is restoring from its snapshot; boot command `cmd-6icjf` is registered. The prior six-hour group limits remain, with a $3.90 quoted compute bound. Registration adds no validated coverage.

### Full-condition aggregation requires every original seed

Use `summarize_supplement_condition.py ARCHIVE INVENTORY CONDITION NEW_OUTPUT`. [The real incomplete-data check](results/supplement-complete-condition-gate-2026-10-19) rejects 403/500 inputs at condition 0.37 and writes no aggregate. The complete-data path remains unvalidated until the cohort finishes. Endpoint counts alone will not establish agreement with a published figure.

## Selfishness Figure 10 target

[The vector-PDF extraction](results/selfishness-figure10-target-2026-10-19) records median-curve ink bounds at 99 interior selfishness factors.
At 0.37, the printed line covers population 1132.78–1143.03; this is graphical precision, not a statistical interval.
The paper compares medians of per-run mean population across 500 seeds, not endpoint counts.
The original averaging and quartile conventions remain unresolved; no additional replication result is claimed.

## Selfishness 0.37 checkpoint 427

[The next 25 inputs](results/selfishness037-sixth-prefix-2026-10-19) pass 120,288 observation checks and exact producer/local audit comparison.
Twenty-four complete 5,000 steps; one reaches native extinction. All 410 prior inventory records remain unchanged.
Coverage is now **428/500** for this condition and **435/100,000** supplementary inputs overall.
The bounded replacement collector resumes export after the former collector stopped; the original producer continues without rerunning completed inputs.
No partial-condition aggregate or new paper-completion credit is claimed.

## Selfishness 0.37 checkpoint 452

[Another 25 disjoint inputs](results/selfishness037-seventh-prefix-2026-10-19) pass 125,025 observation checks; every run reaches 5,000 steps.
Producer and local audits agree exactly, and all 435 prior inventory records remain unchanged.
Coverage reaches **453/500** for this condition and **460/100,000** supplementary inputs overall.
The remaining 47 seeds are required before condition aggregation; paper completion remains unchanged.

## Population-median bounds before the final 47 seeds

[Full native-trajectory analysis](results/selfishness037-median-bounds-2026-10-19) covers all 453 audited seeds and 2,217,626 observations.
Allowing every missing run any mean population in [0,2500] bounds the final median to 1126.08–1143.14 when averaging observed rows.
Excluding the initial observation gives 1126.25–1143.32; zero-extending the ten extinct runs leaves these bounds unchanged.
All four bounds contain the extracted Figure 10 ink interval, 1132.78–1143.03, without assuming random completion order.
This establishes compatibility only. The cohort, historical averaging conventions, and paper verdict remain incomplete.

## Selfishness 0.37 checkpoint 477

[Another 25 disjoint inputs](results/selfishness037-eighth-prefix-2026-10-19) pass 125,025 observation checks; every run reaches 5,000 steps.
Producer and local audits agree exactly, and all 460 prior inventory records remain unchanged.
Coverage reaches **478/500** for this condition and **485/100,000** supplementary inputs overall.
The remaining 22 seeds are required before condition aggregation; paper completion remains unchanged.
