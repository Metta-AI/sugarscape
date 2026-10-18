# Terminal runtime recovery checkpoint

Command `cmd-ty59b` exited one at 01:36:42 UTC on October 18.
The raw 50,000-step worker hit its remaining six-hour allowance.
The altruistic worker exited with SIGKILL, and the provider reports one container out-of-memory kill.
The container had an 8 GiB memory limit; lifetime peak usage reached 8,589,938,688 bytes.
These container-wide counters do not establish either child's individual peak memory.
Both child exit codes are one. A targeted process check found no remaining study workers.

The sealed 99,304,936-byte final checkpoint is hash-verified and exported to object storage.
Independent audits validate all 28 raw and three altruistic completed inputs.
Both full audit reports are exactly equal to checkpoint 10's earlier reports.
This adds no coverage: unique runtime coverage remains 854/1,200 inputs.

| Group | Completed original indices | Remaining original indices |
| --- | --- | --- |
| Raw, 50,000 steps | `[27,55)` in this batch | `[55,100)` |
| Altruistic, 50,000 steps | `[0,3)` | `[3,100)` |

The unfinished raw seed is 588455110223385558; the altruistic seed is 1626428329783443257.
Both incomplete native directories, including partial trajectories, configs and logs,
were sealed separately in a 7,748,333-byte archive and downloaded with SHA-256 verification.
They remain external research evidence and receive no completion credit.
A future run must use a fresh output directory and start at the audited missing index.
Memory planning must account for simultaneous workers before repeating the failed condition.

The frozen manifests and ledger snapshots, independent audits, failure logs and
container memory counters are retained here. Archive locations and hashes are in `readback.json`.
The full declared runtime scope remains unfinished; this terminal audit does not narrow it.
