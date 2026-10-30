# The Need for Greed in Artificial Decisionmakers (2024)

Incomplete native reproduction. Audited coverage is 1,205 unique inputs and 5,005,871 observations: 400 baselines and 805 sweep inputs. Another 9,295 sweep inputs remain. Tables I–III and the complete 0.36–0.40 Table IV row match; death-rate and aggregation questions remain unresolved.

Sources: [publication 1](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2024:need-for-greed.pdf).

## Retained workflow

Retains the hash-checked native input runner and source manifest. Sweep orchestration, repeated verification wrappers, per-table analyzers, and the copied source-audit inventory are archived.

The author engine is the MIT-licensed v2024.1 release `b9ca671ab7591c7b3606f2d76c33eda344d626d1`. Source files must match `source-sha256.json`.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/need_for_greed_2024/run_native.py AUTHOR_ENGINE AUTHOR_CONFIG_ZIP ORIGINAL_ENTRY NEW_RUN --seconds 900
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/d002e524f2577ba7a10d648df6ba3bbd2af8bbce/replications/need_for_greed_2024) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
