# Stevenson (2021): wealth inequality

Incomplete replication. Fixed and conditional evolutionary ensembles were completed, but fixed-society ages, growth fits, author conventions, and figure requirements remain unresolved. No verified author implementation was located.

Sources: [publication 1](https://arxiv.org/abs/2108.11892v2), [publication 2](https://arxiv.org/pdf/2302.03096v2).

## Retained workflow

Retains the fixed-parameter simulator, declared 100-seed ensemble runner, and its analysis. Evolutionary builders, figure digitizers, sensitivity investigations, and chronological reports are archived.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
c++ -std=c++17 -O2 replications/stevenson_2021/simulate.cpp -o NEW_SIMULATOR
python replications/stevenson_2021/run_ensemble.py NEW_SIMULATOR low-fertility NEW_RUN
python replications/stevenson_2021/analyze_ensemble.py NEW_RUN NEW_ANALYSIS
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/c6cf984450724c70838d5506c82316714dcf5798/replications/stevenson_2021) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
