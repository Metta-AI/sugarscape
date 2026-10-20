# Independent-stream diagnostic

This is a post hoc diagnostic prompted by the first 40×40 ranking discrepancy, not a preregistered paper replication.
It holds the generated policies and native models fixed while changing random-stream assignment.

The diagnostic has three groups: an independent 50×50 reference (50 runs per policy/clock), an independent 50×50 comparison (50), and a 40×40 comparison (88).
All 37,600 simulations use distinct seeds, sampled without replacement from 10,000,000 through 2,147,483,646 using Python RNG seed 20261018.
No seed is shared across policies, phases, reference/comparison groups, or runs; none overlaps the earlier small seed ranges.
Every retained request passes ID, seed uniqueness, policy, phase, and compressed/expanded hash checks.

The experiment is queued after the independent full-size ranking batch, preserving the four-worker limit.
Each batch retains a one-hour overall cap, 30-minute per-shard cap, and 512 MiB Java heap per worker.
The unchanged runtime pipeline repeats its 400-run qualification before new native work.

Scientific comparisons must use this diagnostic's own independent reference, not the earlier shared-seed reference.
The frozen protocol retains both clocks and the earlier weights, ties, budgets, and pooled/stratified analysis choices.
A remaining mismatch would leave other source and implementation questions unresolved; this diagnostic alone cannot validate a negative replication.
Native results remain pending. No completion credit is assigned.
