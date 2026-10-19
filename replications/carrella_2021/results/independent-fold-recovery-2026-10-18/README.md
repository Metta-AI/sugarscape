# Independent-data completed-fold recovery

The operational runner `../../resume_estimator.R` verifies independent input hashes,
method, size, seed, source directory, package versions, and a contiguous completed-fold prefix.
It checks original training/test partitions and restores each saved outgoing random state.
New folds use a pending file followed by an atomic rename into a fresh destination.
The earlier [ABC recovery control](../fold-recovery-2026-10-18) remains historical evidence.

Two bounded full workflows qualify the new runner:

- Linear regression, 1,250 inputs: reuse folds 1–2 and recompute folds 3–5 through unchanged author functions.
- Bootstrap forest, 1,250 inputs: replay all five completed folds through the original aggregation workflow.

Every fold object, including predictions, intervals, input rows, and outgoing random states,
must equal its original execution. Aggregate objects and metric files must also match exactly.
The forest control checks replay and aggregation; it does not validate newly fitted forest continuation.
A wrong seed is rejected before destination creation.

Each workflow has a 600-second bound. `evidence.tar.gz` retains both the first qualification
and the repeated atomic-write qualification, their logs, commands, verifiers, and output objects.
The archive manifest verifies every retained file against the external originals.
`verification-atomic.json` records the final exact comparisons for 12,500 parameter predictions.
Original reference outputs remain in the existing independent LM and bootstrap-forest evidence.

The active 5,000-input forest producer was neither interrupted nor duplicated.
Continuation requires confirming its terminal state first. An incomplete fold must be recomputed.
These controls add no paper-level completion credit.
