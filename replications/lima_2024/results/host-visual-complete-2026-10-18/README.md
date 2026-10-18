# Completed host scenario with observed native GUI

Both original NetLogo experiments finish 1,000 steps while host JaCaMo runs
with the eight container services. Two screenshots capture the actual Mining
World window during this run; process provenance links it to the host launcher.

The final snapshot reconciles all **934 router deliveries** exactly. Native logs
validate **1,423 NetLogo creations** and **11 JaCaMo creations**, including
incoming attributes and paths. All **799 identities** occur once at shutdown:
247 model-1 survivors, 252 model-2 survivors, 299 queued agents and one active
miner. Ten JaCaMo returns are observed. No missing identity is discarded.

The collector backed up native files before starting only the stopped database
container, then stopped it again. The archive contains 36 files, including raw
logs, snapshot, saved AgentSpeak files, screenshots, configurations and auditors.
Every member matches the source evidence byte for byte. Both auditors reproduce
identical reports after extraction to a fresh location.

Extract `native-evidence.tar.gz`, then run:

```sh
python EXTRACTED/harness/audit_snapshot.py EXTRACTED/snapshot-final.jsonl NEW_SNAPSHOT_AUDIT.json
python EXTRACTED/harness/audit_native.py EXTRACTED NEW_NATIVE_AUDIT.json --jacamo-log jacamo-host.log
```

This completes the fresh scenario's visible-GUI and full-trajectory requirements.
It does not establish exact historical dependency equivalence. The separate
saved-agent score criterion remains failed and is not reclassified here.
