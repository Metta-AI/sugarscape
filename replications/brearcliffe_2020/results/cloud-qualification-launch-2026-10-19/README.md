# CPU host qualification launch

Owned node `relh-sugarscape-brearcliffe-cpu8-20261019-v1` is queued for an eight-core, 32 GiB CPU host.
Command `cmd-kmpyv` starts on arrival with a 120-minute platform limit and a 6,900-second outer timeout.
At the quoted $0.012/minute and fifteen-minute idle window, the compute-plus-idle bound is $1.62. Queued time is not billed.
The same node's queue hold was extended to eight hours after the provider estimated a wait longer than thirty minutes; no second node was created.

The trial runs two sequential full-length cases: Rule M/EC and Q-Learning/SARSA, seed20261019, released-code parameters.
Both local reference trajectories have passed full native BehaviorSpace comparison. The trial requires exact comparison of all640032 values across40002 observations on the new host.
Every payload file is hash-pinned. The image tag resolves to a fixed provider digest at node creation; runtime versions will be retained with results.
No ensemble scheduling occurs in this trial.

The 32,696,568-byte runtime bundle is retained externally, with hash in `bundle.json`.
Direct upload while queued failed before a successful transfer receipt. The bounded arrival uploader, local session52232, polls only this owned node and uploads when it is running.
The boot command allows five minutes for upload, verifies the archive hash, then extracts and executes the bounded trial. It fails if the input never arrives.
The uploader's eight-hour bound matches the queue hold. Check actual uploader/node/command state before any retry; a polling error is not evidence the remote trial stopped.

Status: registered pending wake. No cross-host qualification or additional ensemble completion is claimed.
