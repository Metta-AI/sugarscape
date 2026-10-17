# Original-input homogeneous-society ensemble

This protocol supersedes the provisional seed-1-through-500 experiment after original author configurations were recovered.
That experiment used incorrect plain decision-model names and has been stopped; its outputs remain intact.
The original protocol and runner remain in Git history through commit `96c7221`.
This correction is based on archived inputs, not selecting parameters for closer numerical agreement.

Replay all 2,000 configurations from the hash-pinned homogeneous archive: 500 shared original seeds for each of four models.
Use the schema-matching v2024.1 release pinned by `run.py`. Change only the output logfile path.
Retain all 5,000 timesteps or extinction; do not discard seeds or replace failed experiments.
Run an operational pilot and independent-process repeat before launching full batches.
The pilot uses an original seed and must be identified explicitly if its completed output is included in the ensemble.

```sh
python replications/blueprints_2024/run_batch.py /path/to/v2024.1 \
  replications/blueprints_2024/results/archive-audit-2026-10-15/blueprints-homogeneous.zip \
  altruisticHalfLookaheadBinary /new/ensemble
```

Repeat for `rawSugarscape`, `egoisticHalfLookaheadBinary`, and `benthamHalfLookaheadBinary`.
`--start` and `--stop` select half-open indices in the numerically sorted original seed list.
These support audited resumptions; completion requires exactly 500 unique original seeds per model.
An output directory or manifest alone does not establish successful execution.

Retain every timestep and metric as lossless gzip, with original and compressed SHA-256 hashes.
Verify decompression byte-for-byte before removing this run's redundant uncompressed copy.
Preserve existing pilots and interrupted evidence. Stop before starting a new run if less than 1 GiB remains free.

Compare the Table 3 counts directly against `published_targets.json` using terminal populations zero, 1–250, and above 250.
Also report 95% Wilson intervals without treating overlapping intervals as proof of reproduction.
For time trajectories, an extinct population remains zero through timestep 5,000.
Do not impute undefined per-agent metrics after extinction; report their denominators explicitly.
Preserve seed pairing in between-model comparisons.

Exact-input agreement is the initial criterion. A mismatch triggers source-version, rule, runtime, and measurement investigation.
Section IX explicitly identifies v2024.1, whose current tag matches our pinned revision. Full result and runtime fidelity still require validation.
Selfishness, mixed societies, horizon analysis, and fork equivalence remain separate required comparisons.

The deposited runtime archive has 100 seeds per model and horizon, disjoint from the homogeneous 500 seeds.
Table 6 reports 500 seeds and the prose says they are the same seeds as before.
Archive replay and reconstruction from homogeneous inputs must remain distinct, with changed horizons declared explicitly.
Use `audit_runtime_inputs.py ARCHIVE_DIRECTORY NEW_JSON` to verify this input discrepancy.
