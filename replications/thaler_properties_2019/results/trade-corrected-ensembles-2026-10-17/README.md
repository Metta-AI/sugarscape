# Corrected trade ensemble

Extract `first.tar.gz`, `remaining.tar.gz`, `remaining-002.tar.gz`, and
`native.tar.gz` into one directory. Extract the reused control archive identified
by `reused-controls.json` into a separate `controls` directory. No raw CSV
restoration is needed: the auditor verifies gzip contents against original hashes.

Run `audit_paired_observers.py protocol.json native OUTPUT first remaining
remaining-002 --reuse-control CONTROL_PROTOCOL controls/first controls/remaining
--interrupted-ledger interrupted-ledger.json` with the study's Python environment.
The control protocol is published with the corrected spice ensemble.

The nonzero terminal receipt authorizes combining only the old batch's completed
prefix. The continuation manifest preserves its disjoint indices. All 100 pairs
are required; partial or duplicate inputs cannot produce aggregate inference.
Source files, binaries, initial conditions, trajectories, two Gini formulas, and
all derived measurements are audited. The reused controls are not rerun.
