# McCulloch et al. (2022)

Completed mixed study. The released model does not reproduce exact stabilization in all declared runs by step 30. Independent trajectories match the author model; posterior agreement remains conditional on the archived prior.

Sources: [publication 1](https://www.jasss.org/25/2/1.html).

## Retained workflow

Retains the released and independent models, stabilization runner, analysis, dependency lock, and complete-world equivalence check. Calibration campaigns and their reference outputs are archived.

The author model's MIT license and Mesa's Apache notice remain under `sugarscape_cg/`.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
PYTHONHASHSEED=0 python replications/mcculloch_2022/run.py --engine independent --output NEW_RUN
python replications/mcculloch_2022/analyze.py NEW_RUN --output NEW_ANALYSIS
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/6dad74a8235653bfe50263bc5041339116d1b754/replications/mcculloch_2022) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
