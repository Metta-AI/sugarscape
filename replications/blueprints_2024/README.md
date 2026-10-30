# Blueprints for Machine Ethics (2024)

Incomplete replication. All 2,000 homogeneous configurations are audited and all four Table 3 rows match the released classification. Supplementary sweeps, historical timing, and aggregation provenance remain incomplete.

Sources: [publication 1](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2024:blueprints-for-machine-ethics.pdf).

## Retained workflow

Retains the hash-checked original-input runner and homogeneous batch runner. Runtime investigations, supplementary scheduling, figure extraction, and reference renderings are archived.

The author engine is v2024.1, commit `b9ca671ab7591c7b3606f2d76c33eda344d626d1`. The deposited dataset retains its Unlicense.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/blueprints_2024/run.py AUTHOR_ENGINE AUTHOR_CONFIG_ZIP ORIGINAL_ENTRY NEW_RUN
python replications/blueprints_2024/run_batch.py AUTHOR_ENGINE AUTHOR_CONFIG_ZIP rawSugarscape NEW_BATCH --start 0 --stop 500
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/8d06b06b57a2f4826b6522c1a4f756c1493d8297/replications/blueprints_2024) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
