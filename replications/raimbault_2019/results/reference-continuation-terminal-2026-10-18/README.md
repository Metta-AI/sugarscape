# Reference continuation terminal audit

The bounded continuation exited 124 at 2026-10-18 02:17:01 UTC.
It adds 4,811 complete native inputs, including complete rows from eight interrupted chunks.
All new rows are disjoint from the re-audited 49,366-input baseline.
The union covers 54,177/55,000 inputs and 108,354 exact Gini comparisons.
The audit verifies all 53 pinned source/dependency files and derives 823 missing indices.
Interrupted simulations receive no credit.

One map was absent from the extracted local proof directory.
It was restored from the retained runtime archive only after its pinned SHA-256 matched.
The prior 49,366-input audit then reproduced byte-for-byte. The cause of absence is unknown.

```sh
python replications/raimbault_2019/audit_reference_continuation.py EXTRACTED RUNTIME NEW_AUDIT.json
```

Command `cmd-6wygn` continues only the 823 missing indices with a two-hour native bound.
The frozen plan and launcher retain eight workers, original inputs and a separate output directory.
It installs Java 11, Python and GNU time because packages outside the retained home reset on node wake.
No additional input has been credited from this new run.

The generated-production predecessor exited 1 before simulations could launch:
`/usr/bin/time` was absent. Its failure archive remains retained here.
That orchestration failure is not a negative replication. The original 8,000-input generated shard
must still run, followed by the separately budgeted full generated ensemble.
