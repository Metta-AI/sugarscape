# Complete paired death-rule sensitivity

All 37,600 native runs complete and pass independent audit, with 75,200 validated request/result lines.
The experiment repeats the preceding independent-stream requests and changes only `sugar <= 0` to `sugar < 0` in death removal.
Policies, seeds, maps, horizons and clocks are unchanged. Native archives pass member-by-member SHA-256 readback.

The printed source conflicts: Appendix B prose specifies death at zero, while Algorithm 3 specifies death below zero.
Neither experiment establishes the authors' actual implementation.

| Group | Clock phase | Prose-rule mean deaths | Algorithm-rule mean deaths |
| --- | ---: | ---: | ---: |
| 50x50 reference | 0 | 98.0476 | 82.3704 |
| 50x50 reference | 4 | 97.0674 | 81.3400 |
| 50x50 comparison | 0 | 97.9452 | 82.2702 |
| 50x50 comparison | 4 | 97.0164 | 81.3412 |
| 40x40 comparison | 0 | 65.2524 | 55.4443 |
| 40x40 comparison | 4 | 64.5885 | 54.6876 |

Mortality changes in 37,223 of 37,600 pairs. Both increases and decreases occur; this is not a monotone coupling claim.
The independent standard-library readback recomputes all paired summary rows directly from native JSONL using integer sums.

At full budget, pooled average-rank linear mortality concordance against the experiment's own reference is 0.6376/0.4602 for 50x50 comparisons and 0.5854/0.5511 for 40x40.
The preceding prose-rule 40x40 values were 0.8686/0.8695.
All 768 ranking rows retain the declared budget prefixes, strata, ties and weights; 38,400 independent rank checks and 768 exact-rational concordance checks pass.
These are descriptive reconstruction sensitivities, not original Figure 10 uncertainty bars or a validated negative replication.

Literal negative tax payments can restore negative wealth to zero and preserve an agent under the algorithm rule.
The third objective is therefore labelled positive payments along the literal trajectory; it is not a clipped-payment counterfactual.

Original controls, implementation, convergence uncertainty, reduced-model conventions and optimizer/Pareto-frontier transfer remain unresolved. This study remains incomplete.

Reproduce with `prepare_death_boundary.py`, `run_rankings.py`, and `audit_ranking_model.py --seed-design independent --death-boundary negative`.
Use `analyze_ranking_model.py --reference-kind independent` for each comparison group, then `compare_death_boundaries.py` for paired summaries.
The frozen protocol directory retains the native 408-state qualification and prior-result regression.
