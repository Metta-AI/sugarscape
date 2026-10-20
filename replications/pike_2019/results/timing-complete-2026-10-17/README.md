# Controlled timing evidence

`audit.json` contains 900 per-seed measurements and 30 paired mean-difference or
mean-ratio comparisons. `timing-records.tar.gz` preserves original timing rows,
manifests, configurations, exits, control receipts, and the full execution ledger.
`files-sha256.json` pins every file in the complete raw archive.

Retrieve the complete raw archive from the owned node and verify the digest in
`raw-archive.json` before running `audit_timing.py ARCHIVE ENGINE NEW_OUTPUT`.
The engine must be the pinned historical checkout documented in the parent README.
The auditor streams the archive without extracting its 2.2 GB contents.

`verify_statistics.R audit.json NEW_OUTPUT.json` independently recomputes all
intervals using R stats::t.test. The first attempt's JSON list-decoding error is
retained; the corrected audit passes without modifying numerical inputs.

Common-resource timings describe runs with nonfinite holdings. They are not
successful economic replications. Historical hardware differs, and these results
do not establish whole-paper completion.
