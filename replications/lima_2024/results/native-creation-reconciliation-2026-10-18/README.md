# Native NetLogo creation reconciliation

The strengthened native auditor checks every printed agent-creation record
against the corresponding consumed database row. It verifies incoming sugar,
metabolism, vision, identity and path, and requires the copied history and
creation-success marker. No model instrumentation or simulation change was made.

All three completed portable scenarios pass: host 1,493 records, container 1,364,
and saved-agent control 1,425, totaling **4,282**. Earlier identity conservation,
JaCaMo reconstruction and 1,000-step trajectory checks also pass unchanged.
The raw logs and snapshots are retained in each scenario's previously published
`native-evidence.tar.gz`; these reports pin the same native-file hashes.

Run `audit_native.py EXTRACTED_RUN NEW_REPORT` after extracting the corresponding
archive. Add `--jacamo-log jacamo-host.log` for host execution, or
`--initial-checkpoints EXTRACTED_RUN/initial-checkpoints.json` for the saved-agent
control.

The native logs print the incoming tuple, not the newly randomized sugar state.
Paper page 51 explicitly specifies drawing new sugar on entry while keeping
metabolism and vision. The source implements that adaptation; this audit does
not turn source evidence into direct observation of the new sugar value.
