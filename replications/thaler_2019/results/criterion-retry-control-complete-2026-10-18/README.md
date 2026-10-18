# Original Criterion repetition control

The original instrumented binary runs with 500 agents, 1,000 steps, seed 42,
no rebirth and 32 capabilities on m5ad.16xlarge. All six intended processes
complete: three default Criterion processes contain 48 simulations; three fresh
single-iteration processes contain three simulations.

| Mode | Processes | Simulations | Mean final retries/commits | Range |
| --- | ---: | ---: | ---: | --- |
| Original Criterion defaults | 3 | 48 | 0.0871433 | 0.0865565–0.0876412 |
| Fresh single iteration | 3 | 3 | 0.0894201 | 0.0876255–0.0908062 |
| Published normal32 target | — | unknown | 0.29 | — |

Repeated benchmarking and cumulative counter aggregation do not reproduce the
published 0.29 in this diagnostic. This does not establish a paper error:
historical runtime, scheduling and instrumentation equivalence remain unresolved.
These instrumented durations are not performance evidence. No new paper credit.

## Preserved harness failure and disjoint recovery

The initial three default-mode processes succeeded. Our harness placed
`--iters 1` after `--match`, which this historical Criterion parser rejects.
The attempted single process exited one before simulation. The original archive
preserves its stderr, traceback, unsuccessful service status and all three
successful default-mode records. The error is ours, not a scientific result.

The corrected runner puts mode options before `--match`. Only the three missing
single processes ran in a fresh directory after the same instance restarted.
No completed default process was repeated. The reboot is an additional execution
condition; the comparison is descriptive, not a paired scheduling experiment.
The original fixed shuffle also placed all default processes before singles.

The first recovery collector queried the old service name and failed before
collection. A corrected collector observed the existing recovery service;
it did not restart simulations. Both sealed archives were subsequently verified,
and the unchanged owned instance lease was stopped after collection.

## Independent audit

`audit_retry_protocols.py ORIGINAL_EXTRACTED RECOVERY_EXTRACTED NEW_AUDIT_JSON`
requires all six process identities, source/binary pins, matching configurations,
command forms, raw file hashes, exit records and expected service results.
It independently recomputes cumulative and per-simulation ratios from raw stderr,
checks printed rounding and monotonic counters, and verifies the preserved parser
failure contains no simulation-counter output. All 51 simulation-counter records
pass. Collection receipts retain archive sizes and SHA-256 hashes.
