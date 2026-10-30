# Replacing Sugarscape (2023)

Incomplete replication. Baseline, disease-seed, example, and trade/lending replays were executed. Historical implementation alignment, seasonal measurement choices, and full paper-level interpretation remain unresolved.

Sources: [publication 1](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2023:replacing-sugarscape.pdf).

## Retained workflow

Retains native scenario/example runners and the configuration hashes consumed by the example runner. Observer investigations, historical source patches, and secondary analyses are archived.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/replacing_2023/run.py AUTHOR_ENGINE SCENARIO 1 NEW_RUN
python replications/replacing_2023/run_examples.py AUTHOR_ENGINE NEW_EXAMPLES
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/85f65106233b130c70ee99a9183cebde39a4deb5/replications/replacing_2023) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
