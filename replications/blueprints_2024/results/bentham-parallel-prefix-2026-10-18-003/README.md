# Audited AWS Bentham snapshot

This snapshot adds 92 original inputs and 460,092 timestep observations.
Every input passes the existing source-pin, configuration, seed, trajectory-hash,
finite-observation, contiguous-timestep, terminal-state, and outcome-classification checks.
All 92 finish at timestep 5,000 with population at least the initial 250.

The reconciled union contains 1,805 of 2,000 required homogeneous inputs:
raw 500, altruistic 500, egoistic 500, and Bentham 305.
All 305 audited Bentham inputs classify as better or equal.
These partial counts do not establish the complete Bentham result.

The frozen attempt ledger has 174 attempts: 153 successes and 21 timeouts.
The prior public snapshot already audited 61 successes; this snapshot adds the other 92.
Every timeout has exit code 124 under the fixed 3,600-second per-input limit.
Required original indices are 157, 159, 165, 177, 181, 196, 197, 203, 216, 221,
226, 230, 232, 237, 254, 255, 269, 288, 292, 301, and 316.
No seed substitutions, timeout exclusions from the required denominator, or scientific negative claims are made.
The ongoing producer and any later outputs are outside this frozen snapshot.

`native-evidence.tar.gz` retains the 92 completed native input directories,
the frozen attempts ledger, selection, plan, and start metadata.
Its 43,083,781 bytes match SHA-256 `9a43e963d3dc6fb8af91ee4e4cb3b53f77104502156d3869ffe567df3320cbdf`.
Every archived regular file was compared byte-for-byte against the extracted evidence.
Partial failed trajectories remain on the owned AWS instance for terminal preservation.

`audits/` contains all 92 full-trajectory audit reports.
`coverage.json` retains contributing audit hashes and excludes agreeing overlaps.
To repeat, extract the archive and run the repository's `audit_batch.py` for each input,
using its recorded remote root from `audit-commands.json` and a fresh audit directory.
Reconcile these reports with the earlier contributing audits using the retained command.
The whole-paper replication remains incomplete.
