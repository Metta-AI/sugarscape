# Pike (2019): Multi-Level Mesa

Incomplete study. Phase I–III experiments, common-resource controls, and timings were executed. Nonfinite native health and unresolved source/measurement fidelity prevent a completed numerical replication.

Sources: [publication 1](https://arxiv.org/abs/1904.08315).

## Retained workflow

Retains the native runner and all three phase entrypoints with their imported adapters and frozen protocols. Resource/timing diagnostics, notebook recovery, and per-claim auditors are archived.

The author's license remains in `AUTHOR_LICENSE`. The pinned author engine and historical Multi-Level Mesa dependency remain external inputs.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/pike_2019/run_phase1.py AUTHOR_ENGINE MULTILEVEL_MESA NEW_PHASE1
python replications/pike_2019/run_phase2.py AUTHOR_ENGINE MULTILEVEL_MESA NEW_PHASE2
python replications/pike_2019/run_phase3_movement.py AUTHOR_ENGINE MULTILEVEL_MESA NEW_PHASE3
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/f5bbee6ba670bb9bbacb1c53941b1bb883cd3182/replications/pike_2019) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
