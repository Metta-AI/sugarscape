# Durable evidence for the first 253 audited inputs

Seven archives preserve every currently audited Brearcliffe input: 250 released-code and three paper-table inputs.
They contain 185,878,625 compressed bytes and 2,569 regular files, covering 5,060,253 previously audited observations.
No simulation was rerun and no coverage or completion credit was added.

Objects are stored under `s3://relh-sugarscape-evidence-20261017/brearcliffe-durable-evidence-001/`.
`manifest.json` pins every archive, every member, and the exact 253-input source audit.
Manifest SHA256: `deb7db345b04542429eed42934406f84c6e41e5fb3af5b27bdefb2bd61558f7f`.

Six existing sealed archives retain their prior hashes. A seventh archive packages four previously separate completed input directories.
During preparation, every trajectory hash matched the source audit, with no duplicate or missing input IDs.
All seven archives and the manifest were uploaded, then imported to a fresh directory on the existing owned node.
The import reports eight files and 186,376,336 bytes, including the manifest.
An independent readback verified all seven archive hashes and all 2,569 member byte counts and hashes.
The 253 unique trajectory identities match exactly. Existing numerical audits are preserved, not repeated by this storage check.

`verify_storage.py` verifies downloaded archives placed beside the pinned manifest.
The complete upload, import, and remote verification receipts are retained here.
The storage CLI returned empty JSON stdout for successful uploads; exit receipts alone were not treated as integrity proof.
Fresh storage readback supplies that proof. Original local and remote evidence remains in place.

This archive set is a snapshot. Inputs completed after these 253 require their own later preservation and audit.
