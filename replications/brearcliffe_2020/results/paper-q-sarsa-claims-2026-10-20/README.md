# Paper-table Q-learning/SARSA claim contrasts

Both ordered matchups complete fifty runs through tick 20,000 under learning rate 0.8 and discount rate 0.9.
The analysis reopens all 100 audited raw trajectories and preserves existing 20,000 whole-run resamples per matchup.
Independent R checks all 200 endpoint values exactly and 30 statistics within a maximum scaled error of 1.78e-15.

| Pairing | Q-learning minus SARSA endpoint wealth | Pointwise 95% bootstrap interval | Early negative mean-difference ticks |
| --- | ---: | --- | ---: |
| Q / SARSA | 1,068.16565 | [1,011.02676, 1,124.83778] | 20 |
| SARSA / Q | 1,063.05835 | [1,003.09259, 1,128.45260] | 13 |

Q-learning has greater endpoint wealth in all fifty runs of each orientation.
Both released-code orientations also have positive endpoint differences and positive pointwise intervals: means 927.47415 and 908.32215.
`interpretation-comparison.json` retains both settings and their early reversals.
This supports the endpoint direction under both interpretations, without establishing all-time dominance or the magnitude implied by “slight.”
The paper provides no numerical threshold for “slight,” and its historical settings and seeds remain unresolved.

Reproduce using the retained 1,550-input union audit and the result directory containing both complete paper-table cohorts:

```sh
python analyze.py REPLICATION_DIRECTORY UNION_AUDIT_JSON
Rscript --vanilla verify.R RESULT_DIRECTORY REPLICATION_DIRECTORY UNION_AUDIT_JSON
```

The analysis is post hoc. Intervals are pointwise and exclude unknown historical sampling uncertainty.
The final paper-table SARSA/SARSA cohort and full-study synthesis remain required; no whole-study credit is added here.
