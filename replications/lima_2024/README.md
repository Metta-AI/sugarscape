# Lima and Aguiar (2024): open multi-agent architecture

Completed qualified author-code feasibility study. Both container-only and host-GUI scenarios were observed, with native trajectories and agent conservation checked. Historical binary equivalence remains unproven.

Sources: [publication 1](https://doi.org/10.11591/ijai.v13.i1.pp45-56).

## Retained workflow

Retains the isolated container preparation/runner, Dockerfile, source pins, execution protocol, and native/snapshot auditors. Host/reload preparation variants and collection helpers are archived.

Preserve NetLogo 6.0.4 and Java 8. Replacement container-base provenance and author revision limits remain recorded in the archived study and retained source pins.

Use the pinned prerequisites from the archived study. Uppercase arguments denote supplied paths or identifiers; output paths must be new.

```sh
python replications/lima_2024/prepare_container.py AUTHOR_ENGINE NETLOGO_ARCHIVE NEW_RUN --project UNIQUE_PROJECT
python replications/lima_2024/run_scenario.py NEW_RUN
python replications/lima_2024/audit_native.py NEW_RUN NEW_AUDIT
```

## Historical study and evidence

The [pinned study record](https://github.com/Metta-AI/sugarscape/tree/04780f31c8ac84547c95866be69368de2f71bcf7/replications/lima_2024) retains full campaigns, removed scripts, reference outputs, source revisions, and dependency environments. It also links earlier raw-data archives.

Findings above describe that recorded study. The retained workflow covers the entrypoints listed here. Export historical files outside this checkout; generated diagnostics belong in temporary or explicitly chosen output directories.
