# Remaining original sweep inputs

Superseded by the [corrected eight-input exclusion inventory](../supplement-inventory-complete-controls-2026-10-18). This original worklist missed two completed paired-runtime inputs; retain it only as historical evidence.

Both original archives contain a complete Cartesian grid over the same 500 seeds.
Selfishness has 101 conditions, from 0.00 through 1.00 in increments of 0.01.
Mixed societies have 99 conditions, with 1 through 99 utilitarian entries in each original 100-entry model list.

| Experiment | Original inputs | Audited controls excluded | Remaining |
| --- | ---: | ---: | ---: |
| Selfishness | 50,500 | 3 | 50,497 |
| Mixed societies | 49,500 | 3 | 49,497 |
| Total | 100,000 | 6 | 99,994 |

`remaining.csv.gz` is a deterministic worklist, sorted by experiment, condition, and numeric seed.
Each row retains the original archive entry and configuration SHA-256.
The condition column means selfishness hundredths or the number of utilitarian entries, respectively.
Do not reinterpret the selfishness archive's placeholder plural model field: native normalization selects its singular Bentham model.

The planner reads and validates all 100,000 original configurations, including fixed fields, model lists, filename semantics, and shared seeds.
It verifies excluded controls against independent audit hashes, original configurations, producer manifests, and complete trajectory hashes.
The separate CSV readback reconciles the original ZIP filename sets against the worklist and exclusions, with no overlap or missing entries.
`inventory.json` retains archive hashes, per-condition counts, all seeds, exclusion evidence, and the planner hash.

Reproduce from the retained original ZIP files and extracted six-control archive:

```sh
python replications/blueprints_2024/plan_supplement.py \
  /path/to/original-archives \
  /path/to/extracted-six-controls \
  replications/blueprints_2024/results/supplement-controls-2026-10-17/audits \
  /path/to/new-inventory
```

The extracted control directory must contain `runs/` from `supplement-controls-2026-10-17/native.tar.gz`.
Use a fresh output directory; the planner refuses to replace existing evidence.

This worklist does not launch jobs or establish any new paper result.
The sequential CPython/PyPy full-trajectory control remains active.
Any dispatch still needs a measured runtime, bounded capacity allocation, and reconciliation against later completed inputs.
The two repeated runtime-control configurations are already among the six exclusions.
