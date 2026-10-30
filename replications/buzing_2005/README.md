# Buzing, Eiben and Schut (2005)

Incomplete study. Three 150-run reconstruction/correction grids were audited. The newer recovered JAWAS source, communication rules, reproduction corrections, and historical fidelity remain qualified.

Sources: [publication 1](https://www.jasss.org/8/1/2.html).

## Retained workflow

Retains native source preparation, a bounded pilot, the reconstruction ensemble, and required Java adapters. Fertility, pacing, landscape, and paper-comparison investigations are archived.

No redistribution license was located for the recovered JAWAS archive. Keep that reference external; the retained files are preparation and execution adapters.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/buzing_2005/run_pilot.py JAWAS_ARCHIVE JAVA_HOME NEW_PILOT paper-com2 0 --cycles 500 --unpaced
python replications/buzing_2005/run_ensemble.py JAWAS_ARCHIVE JAVA_HOME NEW_ENSEMBLE
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/817321da5128261257ca957a041244a2e026115a/replications/buzing_2005) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
