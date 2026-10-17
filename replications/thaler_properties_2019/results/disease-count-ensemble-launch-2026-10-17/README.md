# Remaining disease-count seeds

The first launch exited1 before exporting any trajectory. Its output argument was
relative, but the simulator ran from the native source directory. The failed
attempt, empty completion ledger, command and stderr remain retained privately;
`failure.json` and `terminal-state.json` record the failure here.

`replacement-002` uses an absolute output path and a fresh output directory after
confirming the first container was terminal. It executes only indices1–99; both
validated index-zero outputs are retained separately. The corrected model binaries,
seed list and scientific settings are unchanged. One sequential worker runs the
count-only and combined corrections, with90minutes per variant and a three-hour
outer cap, oneCPU,2GiB memory and a4GiB free-disk guard.

Audit the remaining interval explicitly:

```
python audit_observer_ensemble.py RUN replacement-002/protocol.json disease_persist NEW_AUDIT --interval 1 100
```

An incomplete interval requires `--allow-prefix` and produces no ensemble inference.
Even a full99-run interval must be reconciled with its separately audited first
seed before reporting100-run results.
