# Paper-table evolutionary computing claims

All six relevant matchups are complete: 300 native trajectories, retaining both breed orientations. The fourteen stated directional endpoint claims hold under the paper-table settings, as they did under the released settings. Four wealth contrasts favor EC against reinforcement learning; four combat contrasts and six starvation contrasts favor fewer EC deaths. Every corresponding pointwise 95% whole-run interval excludes zero in the stated direction.

Differences are EC minus its opponent at tick 20,000. Death counts are cumulative, not rates.

| Pairing | Wealth difference | Combat-death difference | Starvation-death difference |
| --- | --- | --- | --- |
| paper-rule-m-ec | -175.47 | 4126.12 | -27944.42 |
| paper-ec-rule-m | -195.28 | 4400.96 | -26886.42 |
| paper-ec-q | 618.23 | -3892.60 | -35731.94 |
| paper-ec-sarsa | 649.41 | -3472.24 | -33635.28 |
| paper-q-ec | 590.10 | -3299.56 | -33523.04 |
| paper-sarsa-ec | 620.56 | -3632.06 | -34115.58 |

The remaining four contrasts are retained as context: EC has lower wealth and more combat deaths than Rule M. Those non-learning results match the released interpretation exactly. The paper gives no equivalence margin for near-equal combat outcomes, so no equivalence verdict is inferred. The mislabeled EC/SARSA Figure 6 panel remains excluded from graphic agreement judgments.

Independent R reopens all 300 raw trajectories, verifies 1,800 endpoint values exactly, and checks 270 statistics within 3.553e-15 scaled error. Python verifies native trajectory hashes against the cumulative audit and cohort summaries. All post-initial ticks are retained; no favorable time window is selected.

This post hoc analysis uses existing whole-run resampling indices. Intervals are pointwise, not simultaneous or estimates of historical sample uncertainty. It adds no simulation coverage or whole-study credit.

To repeat, copy these scripts and protocol into an output directory and run:

```sh
python analyze.py /path/to/study /path/to/complete-union-audit.json
Rscript --vanilla verify.R /path/to/output /path/to/study /path/to/complete-union-audit.json
```

Recover the native artifacts referenced by the audit before rerunning raw-data checks. Python requires NumPy; R requires jsonlite.
