# All-pairing recorder qualification launch

Execute all sixteen ordered method pairings for 1,000 ticks each, comparing the corrected recorder with native BehaviorSpace.
Each execution has a 120-second limit and 1 GiB Java heap. The sequential dispatcher has a 1,800-second total limit, 100 MiB output cap, and 2 GiB free-space gate.
Seed 20261019 and released-code learning rate 0.9/gamma 0.8 are fixed before execution.
The launch records every native command and pinned input. Session 3372 owns the local dispatcher; check actual process state before any restart.

A pairing counts only after both executions exit zero and all 16,016 values agree exactly across 1,001 observations.
Partial output, startup, or a successful subset does not qualify the remaining pairings or complete the paper.
