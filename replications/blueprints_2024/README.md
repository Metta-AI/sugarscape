# Blueprints for Machine Ethics (2024)

**Incomplete replication.** The paper identifies the v2024.1 release used here. All 2,000 original homogeneous configurations are complete and audited; all four Table 3 rows match the published counts under the released plotter's classification.

The complete 500-seed heterogeneous50 cohort contains 1,781,148 observations and 150 native extinctions. Its median population, 938.1763–938.3139 under four conventions, falls within Figure 16's graphical ink bounds. This is qualified graphical agreement, not a confidence interval.

Deposited-runtime coverage is 935/1,200 inputs and supplementary coverage is 1,006/100,000. The bounded continuation ended; its timed-out input receives no credit. Full supplementary sweeps, historical timing, and exact plotting/averaging provenance remain unresolved.

[Published paper](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2024:blueprints-for-machine-ethics.pdf), DOI 10.1109/ACCESS.2024.3519139. [Numeric targets](published_targets.json) retain the checked paper values.

## Original experiment inputs

The authors' separate [datasets repository](https://github.com/digital-terraria-lab/datasets)
contains `blueprints-homogeneous.zip`, introduced June 12, 2024 in commit `9e78c44ca9cffefbb3593a0d490f1631da3239f2`.
The [retained archive and audit](https://github.com/Metta-AI/sugarscape/tree/9414e7b75bd0dc444e8efe24cf2aecab529b4829/replications/blueprints_2024/results/archive-audit-2026-10-15) pin repository revision
`0b50404c2529aa0ab08ce14c7f7abfe30fab837e`, preserve its Unlicense, and validate:

- Exactly 2,000 configurations: four decision models and 500 identical shared seeds.
- Every paired input differs only in decision-model name and output filename.
- Every configuration key and nonoperational default matches the May 28, 2024 release `Glucose/v2024.1`,
  commit `b9ca671ab7591c7b3606f2d76c33eda344d626d1`.

The archive contains inputs, not result trajectories. Section IX on PDF page 20 explicitly identifies v2024.1.
The live `Glucose/v2024.1` tag resolves to our pinned commit `b9ca671ab7591c7b3606f2d76c33eda344d626d1`.
[Release evidence](https://github.com/Metta-AI/sugarscape/blob/9414e7b75bd0dc444e8efe24cf2aecab529b4829/replications/blueprints_2024/results/release-and-runtime-audit-2026-10-17/release.json) corrects earlier notes that inferred the release solely from schema.
Historical producer manifests remain unchanged; full results and runtime equivalence remain to be validated.

The original decision models are `rawSugarscape`, `altruisticHalfLookaheadBinary`,
`egoisticHalfLookaheadBinary`, and `benthamHalfLookaheadBinary`.
The released model dispatch selects the half-lookahead behavior from these names.
The 500 original seeds are retained in the audit, with no substitutions.

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

## Preserved evidence

[The full experiment record](https://github.com/Metta-AI/sugarscape/blob/69c8768600b9926b9ce2923c2d2b46040997d41b/replications/blueprints_2024/README.md) retains dated runs, budgets, failures, source hashes, figures, and detailed controls. Existing histories, outputs, and checkpoints remain unchanged. Historical launch notes do not establish current job status. Restore archived raw inputs before rerunning an analysis, as described in that record.

## Experiment evidence

Code, fixed study inputs, protocols, and written experiment summaries remain in this branch.
Generated run outputs, logs, checkpoints, and binary archives are excluded from the review diff.
The [immutable evidence archive](https://github.com/Metta-AI/sugarscape/tree/9414e7b75bd0dc444e8efe24cf2aecab529b4829/replications/blueprints_2024) preserves the pre-cleanup files.
To restore an input, run `git show 9414e7b75bd0dc444e8efe24cf2aecab529b4829:REPOSITORY_PATH > OUTPUT_PATH` from this repository.
Use the documented runners to regenerate outputs; local output directories remain untracked.
