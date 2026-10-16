# Blueprints for Machine Ethics (2024)

**Incomplete replication. Original configurations recovered; historical release equivalence remains under investigation.**

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

The archive contains inputs, not result trajectories. The release predates those inputs and matches their complete schema,
but the authors have not explicitly identified their exact experimental code revision.
This is stronger provenance than choosing the last pre-submission release; it is not proof of code identity.

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
