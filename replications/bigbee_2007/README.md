# Bigbee, Cioffi-Revilla and Luke (2007)

Incomplete historical replication. Seventeen recovered MASON scenarios were executed; corrected reproduction invariants pass. The recovered implementation is not authenticated as the exact published experiment.

Sources: [publication 1](https://doi.org/10.1007/978-4-431-71307-4_20).

## Retained workflow

Retains the scenario runner, Java adapter, required configuration mapping, and reproduction correction patch. Original runs require a clean author checkout; corrected runs require applying that patch in a separate checkout. Historical binary-parity audits and extracted paper targets are archived.

The original implementation identifies Academic Free License 3.0; external sources and dependencies retain their notices. The runner requires the pinned author checkout and its Java runtime.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/bigbee_2007/run_showcases.py AUTHOR_ENGINE JAVA_BIN original NEW_ORIGINAL
python replications/bigbee_2007/run_showcases.py AUTHOR_ENGINE JAVA_BIN corrected NEW_CORRECTED
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/6b24bda489ebd391b509c3e61eb90790565799f8/replications/bigbee_2007) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
