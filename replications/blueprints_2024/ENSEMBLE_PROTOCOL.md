# Homogeneous-society ensemble

Recorded before running seeds 1–500. Seed-zero pilots informed operational checks only.

Run every integer seed from 1 through 500 with each of `rawSugarscape`, `egoist`, `altruist`, and `bentham`.
These are new shared seeds, not the unavailable historical seed list.
Use the pinned release and complete configuration enforced by `run.py`, with 5,000 steps or extinction.
Do not change settings based on intermediate outcomes, omit extinct societies, or replace failed seeds.
Retain failed attempts and resume only after diagnosing the failure, in a new output directory.
A batch completion is not an ensemble completion: analysis requires exactly 500 unique successful seeds for each model.
Seed 501 is reserved for end-to-end storage validation and is excluded from the ensemble.

Retain every timestep and metric. The batch writer stores trajectories as lossless gzip files,
verifies decompression byte-for-byte, and then removes its own redundant uncompressed copy.
It records both uncompressed and compressed SHA-256 hashes. Existing pilot files remain unchanged.
The writer stops before a new simulation if less than 1 GiB remains free.
No simulation horizon or observation frequency is shortened to reduce storage or runtime.

For Table 3, categorize terminal population as zero, 1–250, or greater than 250.
Report all three counts and proportions with 95% Wilson intervals for each model.
For time trajectories, include every seed; an extinct population remains zero through step 5,000.
Do not impute undefined per-agent metrics after extinction; report their denominators explicitly.
Comparisons between models must preserve seed pairing.

The exact published numeric targets and historical code revision remain unresolved.
Therefore the initial analysis is descriptive, with no equivalence or negative-replication verdict.
Recover those targets and audit release-versus-fork behavior before declaring any paper-level result.
This ensemble covers Table 3 and homogeneous societies; selfishness and mixed-society experiments remain separate required work.

Example complete model batch:

```sh
python replications/blueprints_2024/run_batch.py /path/to/reference altruist 1 500 /absolute/new/evidence
```
