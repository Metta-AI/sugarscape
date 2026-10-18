# Native timing terminal evidence

The original run ended on 2026-10-18 at 02:02:50 UTC with exit 1.
The unchanged TVar executable received SIGSEGV after 294.084 seconds
for the four-capability, 500-agent rebirthing condition (ordinal 41).
Its command, output and exit record remain in the sealed archive.
No failed measurement is credited or silently replaced.

Independent auditing accepts 41 of 45 conditions and 164 raw measurements.
All 39 previously published conditions remain identical.
Table 6 covers 25/25 conditions; Table 8 covers 16/20.
The new TVar/1500 and IO/500 slopes are 64.368168 and 20.800449 seconds.
The failed condition and three unstarted conditions remain required.
This execution failure is not evidence against a published scientific result.
The cause remains unresolved; different hardware and old compiler/runtime behavior require investigation.

Reproduce the audit after extracting `terminal.tar.gz` into a new directory:

```sh
python replications/thaler_2019/timing/audit_native.py EXTRACTED NEW_AUDIT
```

The subsequent instrumented retry ensemble started after this terminal exit.
Do not restart timing work concurrently on that allocation.
