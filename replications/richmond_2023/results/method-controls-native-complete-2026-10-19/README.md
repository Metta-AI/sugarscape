# Five native method controls independently audited

All five predeclared variants completed seed 0, width 256, occupation 0.17, and 100 steps.
Each starts with exactly the same 11,264 active records. The released full trajectory matches the historical capture byte for byte.
A fresh 37,844,967-byte archive download passed SHA-256 and every member-hash check.
All five public auditor executions passed, covering **3,964,000 post-step records**.

| Variant | Final active agents | Total deaths | Diagonal moves | Final negative-wealth survivors | Final unresolved |
| --- | ---: | ---: | ---: | ---: | ---: |
| Released | 8,792 | 2,472 | 316,519 | 0 | 3,065 |
| Transfer attributes | 7,211 | 4,053 | 311,069 | 3,258 | 2,103 |
| Cardinal movement | 8,582 | 2,682 | 0 | 0 | 1,310 |
| Nonpositive death | 8,792 | 2,472 | 316,519 | 0 | 3,065 |
| Combined three rules | 4,613 | 6,651 | 0 | 0 | 456 |

Nonpositive death alone is byte-identical to the release for this condition.
Transfer-only preserves wealth and metabolism, exposing negative-wealth survivors under the retained equality-only death rule.
The combined control removes those survivors and diagonal movement. Its population difference cannot isolate one rule because it changes three rules together.
These source-defined variants were frozen before their outcomes were observed. None was selected to improve agreement with the paper.

The auditor reconstructs metabolism, death identity, resource accounting, transferred attributes, and wrapped movement distance using observed destinations.
It does not independently reproduce random choices, conflict winners, or within-step resolution order.
Historical release states fail when incorrectly labelled transfer or cardinal controls, confirming those audit checks reject the known mismatches.

The resolution counter, cap, carryover, landscape, and scheduling remain unchanged. Unresolved agents remain even in the combined control.
Consequently this is a method-discrepancy diagnostic, not a fully corrected paper model or completed replication.
Instrumented timings are excluded from performance claims. Single-condition differences are not ensemble effect estimates.

The initial restored-node launch exited before simulation because system Python was absent.
The retained recovery restored tools, completed all variants, and exported the archive within the same $8 reservation.
No historical files were overwritten. The owned node received a stop request only after all commands ended and evidence was exported.
Actual cost reconciliation remains pending; the full reservation stays held.

Extract the artifact listed in `artifacts.json`, then run each native state through:

```sh
python replications/richmond_2023/audit_state_transitions.py PINNED_LINUX_INITIAL.csv runs/VARIANT/state.csv NEW_REPORT.json --variant VARIANT
```

Use the Linux initial-state archive from `state-observer-complete-2026-10-18`.
Source variants, pinned protocol, build logs, executable hashes, and every raw native state are retained in the new artifact.
