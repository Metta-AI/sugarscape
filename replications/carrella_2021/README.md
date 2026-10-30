# Carrella (2021): parameter recovery

Completed qualified method reproduction. All 75 finite Table 8 workflows were exercised; 38 printed matches and 37 discrepancies remain. Historical randomness and runtime equivalence are qualified.

Sources: [publication 1](https://www.jasss.org/24/2/7.html).

## Retained workflow

Retains the independent model, its dataset runner, and the author-estimator entrypoint. Source probes, reconciliation scripts, and copied reference tables are archived.

The independent model follows CarrKnight/nofreelunch commit `0400f750`. The embedded NetLogo model's CC BY-NC-SA 3.0 notice remains applicable; the repository's MIT license does not replace it.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/carrella_2021/run_independent.py PARAMETERS_CSV AUTHOR_REFERENCE 0 5000 NEW_RUN
Rscript replications/carrella_2021/run_estimator.R AUTHOR_REFERENCE rejection 5000 1 NEW_ESTIMATE
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/0ba7d93eb5e7f5110ae8bc7ef71b0b2cdcd1e342/replications/carrella_2021) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
