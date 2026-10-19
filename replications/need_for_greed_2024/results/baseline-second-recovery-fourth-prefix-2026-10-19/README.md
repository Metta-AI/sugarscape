# Fourth checkpoint from the informed baseline recovery

Twenty-five disjoint original inputs pass fresh full-trajectory audits, adding 67,030 observations.
Original configurations, frozen payloads, source manifests, seeds, terminal exits and complete prior trajectory hashes all match.
Every metric is finite, ticks are consecutive, and every endpoint reaches step 5,000 or extinction.
Fresh storage download matches the sealed 6,457,111-byte archive and SHA-256 `1b9948bfb38038d36a26341f1809b151f51b2ec1a2b9c8679bd8f662d5c4473f`.

Reconciliation against the latest 387-input inventory rejects overlap and yields 412 inputs with 1,683,353 observations.
Baseline coverage reaches 207/400; 193 remain. Sweep coverage is unchanged at 205/10,100.
The existing bounded producer continues unchanged. No completed-paper credit follows.

The raw archive is stored at `relh-sugarscape-evidence-20261017/need-for-greed-baseline-recovery-002/checkpoint-0004.tar.gz`.
`audit_archive.py` reopens every member against the frozen original evidence; `reconcile.py` checks unique-input coverage.
