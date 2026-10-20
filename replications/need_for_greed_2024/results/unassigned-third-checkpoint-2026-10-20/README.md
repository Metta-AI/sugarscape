# Third unassigned-shard checkpoint

Fresh storage readback verifies the 11,892,983-byte archive and every extracted file hash.
All 25 original inputs and 125,025 observations pass raw trajectory audits, deposited-configuration equality, and qualified execution-payload checks.
The inputs are disjoint from all 882 previously audited inputs and the separately assigned active Table IV range.

Coverage reaches 907 unique inputs and 3,520,381 observations: 400 baseline and 507 sweep inputs.
The remaining sweep contains 9,593 inputs. No complete Table IV row or whole-study credit is assigned.
The separately running five-level row remains at 427/500 audited inputs; this checkpoint does not advance that row.
Recomputed Tables I–III retain all result fields except the updated inventory hash.

`storage-intent.json` identifies durable raw evidence and its expected SHA-256.
`audit.json` retains all member hashes and raw results; `reconciliation.json` preserves every earlier record and excludes duplicate credit.
The existing producer continues within its original bound. No new simulation or reservation was added for this audit.
