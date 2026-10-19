# Three further original runtime inputs

Three original Raw Sugarscape runtime inputs add 50,329 independently audited observations. One completes 50,000 steps; two terminate through natural extinction. Exact duplicate reconciliation reaches **871/1,200 deposited runtime inputs** and **2,700,518 observations**. Full paper scope remains incomplete.

The sealed full checkpoint was exported to owned storage and verified against its recorded SHA-256. Every file was checked. Unchanged local files reuse earlier immutable evidence through verified symlinks; the stored checkpoint itself is self-contained.

To avoid duplicating the earlier 50 MB checkpoint in Git, this directory contains a delta. Extract `../runtime-memory-prefix2-2026-10-18/checkpoint-0009.tar.gz` into a fresh directory, then overlay `checkpoint-0011-delta.tar.gz`. All 114 resulting file hashes exactly match the complete sealed checkpoint; `delta-verification.json` records every hash, both archive hashes and the full checkpoint hash. Existing evidence directories must not be overwritten.

Run `audit_runtime.py ORIGINAL_RUNTIME_ZIP EXTRACTED/GROUP NEW_AUDIT --allow-prefix --recorded-root ORIGINAL_REMOTE_GROUP`, using the retained audit commands for original remote roots. Reconcile with the previous coverage using `reconcile_runtime.py`; all overlapping input identities, endpoints and trajectory hashes must match. `new-inputs.json` lists only newly counted inputs.

The producer remains bounded and active. The deposited 100-input groups do not establish the paper's separately reported 500-seed runtime experiment; no paper completion credit is added.
