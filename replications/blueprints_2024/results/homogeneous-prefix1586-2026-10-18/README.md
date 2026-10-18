# Independently audited homogeneous prefix

The two live producers were checked by process identity before this snapshot.
Their completed ledgers and manifests were frozen before auditing their immutable completed trajectories.
No active trajectory was copied, changed or counted. The original processes continue.

The Bentham resumed interval `[20,146)` contributes 126 valid runs and 630,126 observations.
The egoistic resumed interval `[66,440)` contributes 374 valid runs and 659,188 observations.
Every archived input, source pin, seed, trajectory hash, finite statistic and terminal state passes.
The union reconciler checks overlapping results and excludes duplicates.

| Model | Unique inputs / 500 | Extinct | Worse | Better or equal |
| --- | ---: | ---: | ---: | ---: |
| Raw | 500 | 348 | 5 | 147 |
| Altruistic | 500 | 344 | 10 | 146 |
| Bentham | 146 | 0 | 0 | 146 |
| Egoistic | 440 | 294 | 5 | 141 |

Total coverage is **1,586/2,000 inputs and 3,171,642 observations**.
This adds 72 unique inputs and 132,815 observations beyond the previous 1,514-input union.
Only raw and altruistic are complete 500-input groups. Remaining partial counts are not full Table 3 verdicts.
The last two cohorts still require all missing original inputs and full time-series/figure comparisons.

Public ledgers, manifests, independent audits and full union provenance are retained here.
Raw completed trajectories remain in the external evidence directories named by each audit.
The frozen local audit views use symlinks only to immutable completed seed directories;
they do not duplicate or mutate the live producer outputs.
