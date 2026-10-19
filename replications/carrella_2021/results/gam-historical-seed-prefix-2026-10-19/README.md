# Historical GAM seed prefix

Prospective seeds 1 and 2 completed all five saved folds under R 4.0.5 and mgcv 1.8-34.
Each passes the public replay auditor: 18,750 predictions/bounds and 125 recomputed metrics.
Neither matches any of the five printed performance scores.

Across both seeds, all 12,500 point predictions exactly equal the completed historical seed-zero control.
All 25,000 interval endpoints differ, as do all ten final random states.
The five primary performance scores therefore remain unchanged; interval coverage and width change.
This is a two-seed prefix, not the final nine-additional-seed sensitivity result.
The remaining prospective seeds continue under the original time and spending bounds.
No best seed is selected, and no primary discrepancy or study completion status changes.

`results.tar.gz` contains the immutable completed prefix, including the five original input folds and both replay variants.
`receipt.json` and `readback.json` retain archive and member hashes.
The archive has 35 regular files and five directory entries and 4,748,576 bytes; its SHA-256 is
`09493c9cef37e3add59b9c20f62db2189035d5bf6df0bf49eedf953bae8e05f5`.
Each variant differs from the qualified replay only in the literal fitting seed.
The unchanged public `audit_replayed_gam.R` produced both audit directories.
`compare_seed0.R` independently compares every prediction and bound against the prior historical seed-zero replay.
Full command receipts preserve paths and arguments; source runtimes remain a bundle of differences from the modern environment.
