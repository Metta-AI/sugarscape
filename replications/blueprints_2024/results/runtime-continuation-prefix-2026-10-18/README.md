# Audited runtime continuation checkpoint

The sealed fifth checkpoint contains original raw-Sugarscape indices 66–69 of the deposited 50,000-step schedule.
One input reaches 50,000 steps; three end in native extinction. All four pass the public runtime auditor, adding 50,468 observations.
The original horizon and configurations remain unchanged except for logfile paths.

The downloaded archive SHA-256 matches its completed object-storage export receipt.
Every archive member matches its extracted bytes. Audit checks pinned author sources, interpreter, exact original inputs, commands, compressed/raw trajectory identity, all finite measurements and terminal endpoints.
Exact reconciliation with the previous published union verifies every overlapping original input and adds four previously uncounted inputs.

Deposited runtime coverage is now **877/1,200 inputs and 2,850,988 observations**.
Native extinction is a complete model outcome, not a timed-out or failed run.
The remaining 30 inputs in this raw-model interval and other unfinished groups receive no completion credit.
The existing bounded producer remains active; this checkpoint does not trigger a restart or a duplicate assignment.

This covers the deposited 100-seed schedule, not the paper's 500-seed Table 6 experiment. The paper remains incomplete.

```sh
python audit_runtime.py ORIGINAL_RUNTIME_ZIP EXTRACTED/rawSugarscape-50000 NEW_AUDIT --allow-prefix --recorded-root /root/sugarscape/blueprints-runtime-memory-003/runs/rawSugarscape-50000
python reconcile_runtime.py ORIGINAL_RUNTIME_ZIP PREVIOUS_COVERAGE NEW_COVERAGE NEW_AUDIT/audit.json
```
