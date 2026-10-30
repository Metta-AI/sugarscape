# Richmond et al. (2023): FLAME GPU 2

Completed qualified author-code study with mixed findings. All 84 original conditions and figure analyses were verified. Source defects, ambiguous update ordering, historical visualization, and hardware limitations remain explicit.

Sources: [publication 1](https://doi.org/10.1002/spe.3207).

## Retained workflow

Retains archive/native-result auditors. Run the published engine at its archived revision; experimental instrumentation, initializer alternatives, and image/scaling diagnostics are archived with their evidence.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/richmond_2023/audit_archive.py AUTHOR_ENGINE NEW_ARCHIVE_AUDIT
python replications/richmond_2023/audit_native.py NATIVE_EVIDENCE NEW_NATIVE_AUDIT
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/46e625b32a6c2b5bdc3ddfe0de59d0913f788e4e/replications/richmond_2023) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
