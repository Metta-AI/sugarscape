# Bounded endpoint-control recovery

The preselected selfishness-1 baseline reached its 600-second limit and exited 124.
Its incomplete trajectory and command receipt are retained here, including exact compressed-byte readback.
The paired original sweep also exited 124 at 600 seconds; its failed bytes and the six-input terminal receipt are retained.
The four zero/midpoint inputs exited successfully. Both level-1 inputs are selected for sequential recovery.

A bounded local coordinator waits at most 600 seconds for the original six-input batch to become terminal.
It then reruns only selfishness-1 inputs whose original exit code is 124, in fresh directories.
Each retry uses the qualified public runner and unchanged original 5,000-step configuration, with an 1,800-second wall-time limit.
At most two inputs run sequentially; the coordinator has an external 4,250-second limit plus ten seconds of termination grace.
The runner verifies the pinned archive, source files, and native configuration precedence before execution.
No original output is overwritten, and no live simulation is duplicated.

`audit.py` is prepared but has not yet run on the complete recovered batch.
It will compare every recorded observation, baseline/sweep pairs, prior baseline hashes, and interrupted-prefix bytes.
A timeout or launch does not add input coverage or completed-paper credit.
The shared inventory remains 164 inputs pending complete control reconciliation.
