# Izquierdo et al. (2009): ergodicity

Structural result reproduced for the formal Sugarscape appendix: finiteness, irreducibility, and aperiodicity imply its unique initial-state-independent limiting distribution. No practical mixing-time claim is made.

Sources: [publication 1](https://www.jasss.org/12/1/6.html), [publication 2](https://www.jasss.org/12/1/6/appendixB/EpsteinAxtell1996.html).

## Retained workflow

Retains the proof, model, landscape witness, and independent witness verification. Regeneration experiments and their additional verifier are archived.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/izquierdo_2009/witness.py FIGURE2_PNG NEW_RUN
python replications/izquierdo_2009/verify_witness.py NEW_RUN NEW_VERIFICATION
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/cef615f44fdbc4012fbe13e86736a0a544d797c6/replications/izquierdo_2009) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
