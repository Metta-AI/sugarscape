# Recorded audit results

Status: **discrepancy; no completed paper replication**.

| Model | Max metabolism, vision | Seeds | Mean population at 30 | Variance | Bootstrap 95% variance interval | Published variance | Stable runs / first 30 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| author-mesa | 1, 1 | 220 | 82.950 | 12.048 | [9.801, 14.489] | 13.0 | 30/30 |
| dtl | 1, 1 | 30 | 91.800 | 5.614 | [3.145, 8.051] | 13.0 | 30/30 |
| author-mesa | 2, 10 | 220 | 83.327 | 12.121 | [10.053, 14.295] | 12.05 | 30/30 |
| dtl | 2, 10 | 30 | 95.833 | 3.661 | [2.326, 4.949] | 12.05 | 30/30 |
| author-mesa | 4, 7 | 220 | 67.377 | 17.642 | [14.604, 20.838] | 18.34 | 3/30 |
| dtl | 4, 7 | 30 | 79.233 | 5.495 | [2.851, 8.461] | 18.34 | 0/30 |

Intervals describe Monte Carlo uncertainty of these new runs; they do not establish model equivalence.
The original paper's seed-level observations are unavailable. The two models have different semantics.
These comparisons cannot validate the unimplemented history-matching and posterior experiments.

Thin lines show the first 30 runs; thick lines show means over all recorded seeds.

![Population trajectories and post-step-30 changes](https://github.com/Metta-AI/sugarscape/blob/e72314ec4d198476ca2351d6cb4e6b71e4078c07/replications/mcculloch_2022/results/audit-2026-10-15/population.png)
