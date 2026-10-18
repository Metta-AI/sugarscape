# Qualification before a parallel Bentham handoff

The local producer remains unchanged. At preparation it had completed indices 20–148,
in addition to the prior indices 0–19; its current unfinished input was index 149.
The last five completed simulations took 679–949 seconds each.
This suggests several days of serial work for roughly 350 remaining inputs.
Those measurements are estimates, not a guarantee of cloud speedup.

A task-owned m5ad.16xlarge allocation first replays only completed index 20,
seed 460149852129392939, with Python 3.11.14 and the unchanged archived configuration.
Qualification requires all 5,001 original trajectory records to match the pinned SHA-256 exactly.
This deliberate qualification repeat adds zero new-input or paper-completion credit.

The native qualification is bounded at 3,600 seconds and its bootstrap at 5,400 seconds overall.
The allocation has a six-hour lease, nominal compute ceiling $19.776, and retained 60 GiB disk.
It uses the existing sandbox SSM workflow without inbound SSH or forwarded credentials.
The collector retains at most 100 MiB and waits at most 6,400 seconds.

No remaining input interval is assigned yet. Before any proposed 32-worker execution,
verify qualification, inspect the local producer again, preserve its completed ledger and any partial attempt,
and freeze the exact disjoint remaining input set. Do not run overlapping production intervals.
Local simulation and publication status remain distinct from this capacity qualification.
