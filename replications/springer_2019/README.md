# Springer (2019): DynaSOAr Sugarscape

Incomplete historical reproduction. Native execution and capacity/timing controls were investigated. Allocator, compiler, dependency, and historical hardware qualifications remain; no unrestricted timing-equivalence verdict is claimed.

Sources: [publication 1](https://doi.org/10.4230/LIPIcs.ECOOP.2019.17), [publication 2](https://doi.org/10.4230/DARTS.5.2.2).

## Retained workflow

Retains native qualification, archived-native-output verification, and author licensing. Progress diagnostics, historical allocator variants, and plot-derived targets are archived.

The official ECOOP/DARTS artifact is the source of truth. Its author license remains in `AUTHOR_LICENSE`; contemporary CUDA/compiler changes remain explicit qualifications.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/springer_2019/qualify.py NEW_RUN --cub toolkit --source-mode portable-syntax
python replications/springer_2019/audit_qualification.py NEW_AUDIT NATIVE_ARCHIVE
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/9f710823ba1330e4f5de96ac12c1f35975d30696/replications/springer_2019) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
