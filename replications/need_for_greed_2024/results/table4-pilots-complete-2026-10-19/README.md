# Full Table IV runtime pilot gate

Both preselected original inputs complete at 5,000 steps under CPython 3.11.14 and PyPy 3.11.13 / 7.3.20.
The seed is 238165197779399277, selected before outcomes as the smallest deposited seed.

| Selfishness | Observations per runtime | Final population | CPython/PyPy |
| --- | ---: | ---: | --- |
| 0.36 | 5,001 | 1,158 | Byte-identical |
| 0.40 | 5,001 | 1,312 | Byte-identical |

The checkpoint was downloaded from completed task-owned object-storage export and checked against its sealed size and SHA-256 hash.
All four complete trajectories pass the public supplementary auditor locally: configuration, source/runtime manifests, finite values, timesteps, completion, and reported outcomes.
Both original configurations are byte-identical to the corresponding Need for Greed archive entries.
Six frozen payload files match the launch files exactly. All 49 archive members pass publication readback.
The archive retains every raw trajectory, original/effective configuration, manifest, result, native logs, audit, and pilot gate.

There are 20,004 native observations across four executions, but only two distinct original inputs and 10,002 observations per runtime.
Those two PyPy results are already part of the 400-input assignment; they must not be counted again when the batch completes.
The unchanged coordinator has passed its gate and continues the remaining assigned inputs under its original bounds.

To repeat a run audit, extract the checkpoint into a fresh directory and use the included script:

```sh
python audit_supplement.py BLUEPRINTS_SELFISHNESS_ZIP EXTRACTED/runs/RUN_DIRECTORY NEW_AUDIT_DIRECTORY --expected-runtime pypy
```

Use `cpython` for each reference run. The exact four invocations are retained in audit-commands.json; choose new output directories for fresh audits.
This qualifies the two selected runtime controls. The full 500-input Table IV bin and whole paper remain incomplete.
Shared coverage remains 170 inputs until batch reconciliation; no completed-study credit is added.
