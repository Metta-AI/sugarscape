# First recovered baseline prefix

Twenty-two completed original inputs pass independent raw-data auditing: 52,015 observations match retained trajectory hashes exactly.
Original deposited configurations, frozen execution payloads, source/runtime metadata, finite metrics, consecutive timesteps, and terminal outcomes are checked.
Two complete audit executions produce identical reports. A deliberately altered trajectory is rejected without writing an audit result.
The first qualification wrapper expected an unformatted traceback line; formatting split that line. The corrected wrapper passes, and both attempts are retained.

The 4,742,061-byte raw archive is retained in task-owned storage. A fresh storage download matches every byte.
`storage-readback.json` pins its location and SHA-256; `audit.json` lists every regular archive member hash.
The archive captures immutable completed runs while the existing producer continues. No simulations were restarted for this audit.

Unique-input reconciliation raises coverage from 170 to 192 inputs and from 835,607 to 887,622 observations.
There are 89 audited baseline inputs and 103 sweep inputs; 311 baseline and 9,997 sweep inputs remain.
Later checkpoint archives overlap this prefix and must be deduplicated by original configuration entry.
The two Table IV runtime pilots remain outside shared coverage. This prefix is not a completed paper replication.

Run `python audit.py EVIDENCE_ROOT ARCHIVE NEW_REPORT` against the retained original evidence tree.
Run `python reconcile.py EVIDENCE_ROOT NEW_REPORT` to reconstruct the inventory update.
