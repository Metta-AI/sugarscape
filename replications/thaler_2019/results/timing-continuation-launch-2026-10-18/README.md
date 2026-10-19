# Four-condition timing continuation

Command `cmd-rnfx3` waits for the existing population-grid terminal archive
before running ordinals 41–44 on the same reserved eight-core allocation.
It preserves the prior TVar segmentation fault and all 41 accepted conditions.
No author model source, GHC version, benchmark arguments or fit threshold changes.
The continuation uses the original source tree and records fresh binary hashes;
compare them with `original-manifest.json` before reconciling results.

The wait is bounded at 18,000 seconds, timing at 14,400 seconds,
and execution at 15,000 seconds. The overall command is bounded at 33,100 seconds.
Every attempt remains bounded at 3,600 seconds; another native failure stops the run.
Archive collection is bounded at 64 MiB. No result is credited before raw auditing.

Validation: runner CLI parses, shell syntax passes, Ruff passes.
Re-running the updated auditor on the real 41-condition terminal archive produces
an identical audit. Continuation execution and its four-condition audit remain pending.

```sh
python replications/thaler_2019/timing/audit_native.py EXTRACTED NEW_AUDIT --start-ordinal 41
```

This audit will report the absent prefix as missing. Full coverage requires
reconciling the two archives without dropping the failed first attempt.
