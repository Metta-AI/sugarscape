# Rule M claims under paper-table parameters

All six relevant paper-table matchups are complete: 300 native trajectories, with both breed orientations against EC, Q-learning, and SARSA. This analysis adds no simulation coverage.

All eighteen endpoint differences—wealth, vision and metabolism across six matchups—are positive for Rule M minus its opponent. Every pointwise 95% whole-run bootstrap interval is above zero. Higher metabolism represents greater sugar consumption, not an unqualified benefit.

| Pairing | Endpoint wealth difference | Pointwise 95% interval | Post-initial positive mean ticks |
| --- | --- | --- | --- |
| paper-rule-m-ec | 175.474 | 156.031 to 193.253 | 18106/20,000 |
| paper-rule-m-q | 213.697 | 207.087 to 220.473 | 20000/20,000 |
| paper-rule-m-sarsa | 206.829 | 199.474 to 214.168 | 20000/20,000 |
| paper-ec-rule-m | 195.278 | 179.165 to 209.526 | 18042/20,000 |
| paper-q-rule-m | 206.405 | 201.367 to 211.768 | 20000/20,000 |
| paper-sarsa-rulem | 212.677 | 205.292 to 220.021 | 20000/20,000 |

EC retains its early wealth advantage: 1,894 negative mean-difference ticks in Rule M/EC and 1,958 in EC/Rule M. The complete curves are retained; no favorable window was selected. Q-learning and SARSA comparisons have positive ensemble-mean wealth differences at every post-initial tick.

Independent R reopens all 300 raw trajectories, checks all 1,800 endpoint values exactly, and verifies 234 statistics within 3.553e-15 scaled error. Python checks each raw trajectory hash against the cumulative audit and cohort summary. Existing whole-run resampling indices remain unchanged.

All eighteen endpoint directions and positive intervals also hold under the released-code parameters. The six non-learning contrasts match exactly across interpretations. Both parameter settings remain reported; these results do not identify the authors' historical settings.

This post hoc analysis supports the stated directional endpoint claims under both declared interpretations. Intervals are pointwise, not simultaneous or estimates of historical sample uncertainty. Full paper-table ensemble and remaining claim synthesis are incomplete; no whole-study credit is added.

Reproduce using a copy of these scripts and protocol in an output directory, with NumPy for Python and jsonlite for R:

```sh
python analyze.py /path/to/study /path/to/complete-union-audit.json
Rscript --vanilla verify.R /path/to/output /path/to/study /path/to/complete-union-audit.json
```

The audit contains retained native artifact locations; recover those artifacts before rerunning the raw-data checks.
