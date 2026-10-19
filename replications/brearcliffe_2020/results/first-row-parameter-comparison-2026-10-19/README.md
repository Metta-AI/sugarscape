# Four paired cohorts do not distinguish historical learning parameters

Both frozen interpretations now cover the same first four pairings, with 50 seeds each: 200 paired inputs and 400 trajectories.
The released code uses alpha 0.9/gamma 0.8; the paper table uses alpha 0.8/gamma 0.9.
This comparison reopens the summaries, means, and corrected curve comparisons. Every source hash and common paper target is verified.
Earlier uncorrected released-code comparison artifacts are excluded.

| Pairing | Identical paired trajectories | Endpoints overlapping under both | Endpoints overlapping under neither | Unresolved endpoints |
| --- | ---: | ---: | ---: | ---: |
| Rule M / Rule M | 50/50 | 9 | 0 | 5 |
| Rule M / EC | 50/50 | 12 | 2 | 0 |
| Rule M / Q-learning | 0/50 | 11 | 1 | 2 |
| Rule M / SARSA | 0/50 | 14 | 0 | 0 |

Both interpretations give identical endpoint categories: 46 overlaps, three non-overlaps, and seven unresolved targets.
The existing endpoint criterion therefore cannot identify which learning settings produced these historical plots.
Non-learning pairings are exact controls; their parameter changes do not change trajectories.
Learning trajectories differ, but their endpoint categories remain the same.

Across full curves, Rule M/Q has six columns overlapping only under released settings and sixteen only under paper settings.
Rule M/SARSA has one released-only and two paper-only overlaps.
Adjacent columns are dependent; these counts are descriptive and are not independent statistical trials or a parameter-selection score.
No interpretation is selected from these results. Remaining pairings still require both frozen interpretations.

The real analysis command ran twice with byte-identical reports; formatting and lint checks pass.
Existing independent R checks cover each source cohort's arithmetic. This synthesis adds no new trajectory audit, simulation coverage, or completed-paper credit.
Run from this study's directory:

```sh
python results/first-row-parameter-comparison-2026-10-19/analyze.py results /tmp/brearcliffe-first-row-comparison.json
```

The output path must not already exist. Raster overlaps do not establish equivalence; unresolved source labels and historical seeds remain limitations.
