# Blueprints for Machine Ethics (2024)

**Incomplete replication. Original configurations recovered; the paper explicitly names the v2024.1 release used here.**

Latest audited checkpoint: **590 / 2,000 homogeneous configurations**, covering 1,134,134 observations.
Original-seed prefixes are raw 345, altruistic 113, egoistic 102, and utilitarian 30.
[Checkpoint evidence](results/source-checkpoint-2026-10-17) adds 61 completed runs; two agreeing pilot duplicates remain excluded.
The four active batches pass source, configuration, seed, trajectory-hash, and terminal-state checks.
Earlier checkpoint sections below retain their historical counts. Full homogeneous and other paper experiments remain incomplete.

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
