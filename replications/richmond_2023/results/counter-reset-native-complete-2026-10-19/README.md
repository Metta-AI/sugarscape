# Counter reset isolates unresolved-agent carryover

All four predeclared native controls completed and passed independent accounting across **2,873,995 post-step records**.
The released and combined-three-rule baselines reproduce their prior full trajectories byte for byte; repeated baselines add no unique experiment credit.
Every variant starts with the same 11,264 active agents. No rule was selected after inspecting outcomes.

| Variant | Final active | Steps with unresolved agents | Unresolved agent-step observations | Bidding rounds per step |
| --- | ---: | ---: | ---: | --- |
| Released | 8,792 | 97 | 265,921 | 1–3 |
| Reset only | 8,602 | 0 | 0 | 3–4 |
| Combined three rules | 4,613 | 97 | 46,344 | 1–3 |
| Combined plus reset | 4,962 | 0 | 0 | 3–4 |

Both unreset variants first leave unresolved agents at step 3, when the carried counter starts at nine.
Both reset variants start every step at zero and resolve all conflicts within three or four rounds.
The nine-round limit never binds in either reset trajectory. These observations isolate the per-step counter omission in this condition.
The combined reset variant also has zero diagonal moves and zero negative-wealth-after-metabolism survivors, as required by its other declared changes.
Its 48 stationary observations are not unresolved agents; all recorded statuses reconcile.

The [paper, section 4.3.1](https://onlinelibrary.wiley.com/doi/10.1002/spe.3207) describes within-step dynamic bidding and a maximum of nine rounds.
The released histogram path resets its counter, while the population/scaling path does not.
The control adds that reset to the latter path and preserves the nine-round limit.
It changes outcomes, so it remains explicitly separate from historical author-code replay.

The auditor checks metabolism, death identity, resource accounting, transferred attributes, wrapped movement, and all 100 counter traces.
Observed destinations are inputs. Random choices, conflict winners, and within-step execution order are not independently reconstructed.
This single seed, width256, occupation0.17 experiment does not establish behavior at other densities or widths.
The initializer, landscape, scheduling, and conflicting published parameter values remain unchanged qualifications.
No whole-paper completion or benchmark-performance credit is assigned.

The 30,655,255-byte artifact was exported, independently downloaded, and checked by SHA-256 and every member hash.
Both runtime source baselines and the pinned observer passed exact parity checks.
A stop request followed terminal execution and durable export; the full $8 reservation remains held until cost reconciliation.

To reproduce, extract the artifact in `artifacts.json` and use the pinned Linux initial state from `state-observer-complete-2026-10-18`:

```sh
python replications/richmond_2023/audit_state_transitions.py INITIAL.csv runs/counter_reset/state.csv NEW_REPORT.json --variant counter_reset
python replications/richmond_2023/audit_state_transitions.py INITIAL.csv runs/combined_with_counter_reset/state.csv NEW_REPORT.json --variant combined_with_counter_reset
```

The frozen launch directory retains the runner and full archive/counter audit workflow.
