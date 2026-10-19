# Bounded runtime batch: terminal audit

Both groups reached their original six-hour execution budget.
The retained logs identify subprocess timeouts; the producer and both group exits are nonzero.
No interrupted input receives completion credit.

The sealed final checkpoint contains 20 completed raw inputs and 16 completed altruistic inputs.
Independent trajectory audits and exact overlap reconciliation add 25 unique inputs and 253,312 observations.
Total deposited runtime coverage reaches 909/1,200 inputs and 3,354,611 observations.

The complete 110,008,683-byte archive matches its completed object-storage export receipt and SHA-256.
It remains in local evidence and task object storage, identified by `export-intent.json`.
All extracted member hashes, group logs, input audits, and reconciliation commands are retained here.
`remaining-intervals.json` identifies the unchanged original input ranges and interrupted first inputs for continuation.
No new batch has been launched.

The paper’s 500-seed timing protocol remains distinct from these deposited 100-seed groups.
This completes the bounded batch audit, not the runtime experiment or paper replication.
