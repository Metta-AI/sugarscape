# Four additional completed original-input retries

Original Bentham indices 165, 177, 181, and 196 completed under the longer operational timeout.
The original seeds, release, configurations, and full 5,000-step horizons remain unchanged.
All four fresh trajectory audits pass, adding 20,004 observations.
Each finishes with population at least the initial 250 and classifies as better or equal.

The deduplicated homogeneous union contains 1,833 of 2,000 required inputs:
raw 500, altruistic 500, egoistic 500, and Bentham 333.
All 167 missing Bentham inputs remain required. The paper-level study remains incomplete.
Earlier timeout attempts are retained as operational failures, not scientific negatives.
This snapshot excludes any subsequent outputs from the live retry producer.

The archive preserves all four native input directories, original retry plan, producer, and earlier failed-attempt records.
Every member was checked byte-for-byte; `archive.json` records size, SHA-256, and file count.
`attempts.json` retains the exact commands, seeds, durations, and original audit hashes.
`audit-commands.json` records fresh full audits; `coverage.json` reconciles them with earlier evidence.
To reproduce, extract the native archive, relocate the input paths in the recorded audit commands,
and reconcile the fresh reports using the retained reconciliation command.

When extracting elsewhere, pass `--recorded-root ORIGINAL_INPUT_PATH` to `audit_batch.py`. The original path is retained in each attempt command and audit report.
