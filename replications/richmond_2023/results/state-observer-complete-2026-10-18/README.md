# Native state fidelity audit

The unchanged-model observer completed seed 0, width 256, occupation 0.17, 100 steps.
All 100 reported population counts match the unchanged benchmark.
All 101 snapshots have unique agent IDs and occupied coordinates.
The capture contains 893,017 active-agent observations, including 11,264 initial agents.
Observer timings are excluded from performance results.

## Initializer control

The first audit failed against the macOS GCC 16.2 reference (11,025 initial agents).
The exact same extracted initializer source, SHA-256
`dea737bf041b31802b42e6633ad2578ae7182c4fb31eb1e83dd8114afb97df33`,
was compiled on the native GPU node using GCC 11.4, `-std=c++17 -O2`.
Its 11,264 active initial records match the native capture exactly, field for field.
This controls the toolchain mismatch; it does not isolate which compiler/library difference caused it.
The failed reference audit is retained. The new auditor pins the matching Linux reference hash.

## Observed released-code behavior

An independent accounting reconstruction checks all 100 complete transitions using observed destinations.
It reconciles 881,753 post-step agent records, 615,829 moves, and 2,472 deaths.
Every successful move stores metabolism -1 and destination sugar minus one,
matching the released handler's omitted transfer of wealth and metabolism.
All post-step agent records therefore have metabolism -1 in this condition.
The first post-step snapshot contains 4,442 agents with nonpositive wealth.
There are 316,519 diagonal moves despite the paper's four-cardinal-direction description.
No negative-wealth-after-metabolism survivor occurs in this capture;
this run does not establish an effect from the equality-only death predicate.

At step 99, 8,792 agents remain active: 5,727 occupied and 3,065 unresolved.
The original population CSV reports only the occupied subset.
The resolution counter ends at 106 and is not reset between these steps.
The unresolved observations support the earlier counter-carryover finding.

The reconstruction validates resource accounting, death identity, transferred attributes,
one-cell wrapped displacement and final state consistency. Observed destinations are inputs:
it does not independently reproduce GPU random choices, conflict winners or within-step round order.
The original simulation is unchanged; no corrected model is substituted for the historical replay.
These results do not complete the remaining figure and performance interpretation requirements.

## Reproduce

Extract `native.tar.gz` and `host-control.tar.gz` into separate directories.
Use the pinned benchmark CSV from `full-scaling-prefix31-2026-10-18`.

```sh
python replications/richmond_2023/audit_agent_states.py NATIVE HOST/state.csv PREFIX/performance_scalingperStep.csv NEW_AUDIT.json
python replications/richmond_2023/audit_state_transitions.py HOST/state.csv NATIVE/run/state.csv NEW_TRANSITIONS.json
```

Source and build logs, protocol, raw native states, Linux compiler details,
initializer executable and CSV are included in the archives.
