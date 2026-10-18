# Completed original-input retries

Original Bentham inputs 157 and 159 completed after their earlier AWS timeouts.
Both retain their original seeds, release, configurations, and 5,000-step horizons.
Only the host and operational timeout changed: the retry limit is 7,200 seconds.
Measured durations were 1,292.4 and 1,466.7 seconds; neither reached that limit.
Both complete trajectory audits passed, adding 10,002 observations.
Both final populations meet or exceed the initial population of 250.

The reconciled homogeneous union contains 1,807 of 2,000 inputs:
raw 500, altruistic 500, egoistic 500, and Bentham 307.
The remaining 193 Bentham inputs remain required. The study remains incomplete.
Earlier timeouts are operational failures, not negative scientific replications.
Their original records remain preserved alongside the retry plan in the archive.

`native-evidence.tar.gz` contains both completed input directories and producer metadata.
Its 949,009 bytes match SHA-256
`5efb9f77baca5499137132f02c0ee8dff7f1a9d5196eb00ed96ef9df83712bb6`.
All 23 archived files were checked byte-for-byte against retained evidence.
`attempts.json` records exact commands, seeds, durations, and audit hashes.
`audits/` contains the full trajectory checks; `coverage.json` reconciles prior evidence without double counting.
To reproduce, extract the archive and run `audit_batch.py` on each input directory,
then reconcile with the prior audits using `reconciliation-command.json`.
This snapshot excludes later outputs from the ongoing retry producer.
