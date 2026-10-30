# Oremland and Laubenbacher (2014)

Completed qualified method reconstruction. Convergence, reductions, search, transfer, and timing were exercised. Historical settings, numerical equivalence, and global optimality remain unestablished.

Sources: [publication 1](https://www.jasss.org/17/2/6.html).

## Retained workflow

Retains model construction and bounded uniform/policy ensembles with their Java adapters and trajectory auditor. Reduced-model searches, ranking/transfer campaigns, timing investigations, and derived targets are archived.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/oremland_2014/build_model.py AUTHOR_MODEL CAPACITY_TXT NEW_MODEL_DIR
python replications/oremland_2014/run_ensemble.py JAVA_HOME NETLOGO_APP RECONSTRUCTED_MODEL NEW_RUN --seeds 100 --seconds 1800 --timeout TIMEOUT_EXECUTABLE uniform
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/78eaf58888eb119d472ccc3c1fcd807f0b96968d/replications/oremland_2014) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
