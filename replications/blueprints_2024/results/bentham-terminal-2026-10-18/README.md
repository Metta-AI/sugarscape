# Terminal AWS Bentham evidence

The terminal archive adds 22 completed original inputs and 110,022 observations.
Each passes the full source, original configuration, seed, trajectory-hash,
contiguous-timestep, finite-observation, and terminal-state audits.
All 22 complete 5,000 steps and classify as better or equal.

The reconciled union contains 1,829 of 2,000 homogeneous inputs:
raw 500, altruistic 500, egoistic 500, and Bentham 329.
All 171 missing Bentham inputs remain required. The whole study remains incomplete.

The final attempt ledger contains 201 records: 175 successes and 26 timeouts.
Earlier snapshots already count 153 successes; only the remaining 22 are added here.
Interrupted descendants without final attempt records are not counted as successes.

The parent reached its scheduled cutoff at 08:34:15 UTC, but child process groups survived.
Their continued writes caused tar to fail and the collector to exit without accepting an archive.
We recorded and terminated all 120 descendants selected by the exact experiment output root.
No forced kills were needed, and the subsequent process check found none remaining.
The stable replacement archive was downloaded and its full SHA-256 verified.
It preserves completed and partial outputs; its receipt is `collection-recovered.json`.
The failed original archive remains on the instance's verified persistent EBS disk.
The owned instance was explicitly stopped after evidence recovery; the stop receipt is retained.
This launcher must use a bounded process group or cgroup with verified descendant termination before reuse.
The lifecycle failure is operational evidence, not a negative scientific replication.

The smaller public archive retains the 22 added native input directories and full final attempt ledger.
Every member was checked byte-for-byte; `archive.json` records its hash and size.
`audits/` contains every complete trajectory audit, and `coverage.json` deduplicates prior evidence.
Extract the archive, rerun the recorded audit commands with relocated input/output paths,
and reconcile those reports using `reconciliation-command.json`.
