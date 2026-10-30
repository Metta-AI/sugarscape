# OpenABL Sugarscape benchmarks (2021)

Incomplete paper replication. Published C, MASON, FLAME, and GPU grids were exercised with separately qualified behavior checks. Buffer semantics, neighbor ordering, hardware differences, and distributed scaling remain explicit qualifications.

Sources: [publication 1](https://doi.org/10.1016/j.future.2020.10.014).

## Retained workflow

Retains independent C/MASON initialization, transition replay, and the required native build patch. Generated benchmark inventories, backend-specific controls, figure extraction, and timing plots are archived.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/openabl_2021/initialize.py NATIVE_INITIAL_JSON NEW_C_AUDIT --requested-cells 250
python replications/openabl_2021/initialize_mason.py NATIVE_INITIAL_JSON NEW_MASON_AUDIT --requested-cells 250
python replications/openabl_2021/replay.py INITIAL_JSON EXPECTED_JSON NEW_REPLAY --steps 100 --buffer copy
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/f93dcea972a586c16c13d6b29c9f91c87d01e100/replications/openabl_2021) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
