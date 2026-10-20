# Twelve paired cohorts under both parameter interpretations

The first twelve ordered pairings contain 600 paired inputs and 1,200 trajectories.
Released code uses learning rate 0.9 and discount 0.8; the paper table uses learning rate 0.8 and discount 0.9.
Every comparison uses the same corrected paper targets, with source hashes checked before analysis.

| Endpoint raster overlap | Count |
| --- | ---: |
| Both interpretations | 121 |
| Paper parameters only | 8 |
| Released parameters only | 2 |
| Neither interpretation | 18 |
| Unresolved target | 19 |

The two added pairings are Q/Q and Q/SARSA, each with fifty paired inputs.
All their matched trajectories differ between interpretations.
Q/Q adds seven shared overlaps, one released-only maximum-age overlap, and six unresolved targets.
Q/SARSA adds twelve shared overlaps and two unresolved targets.
The previous ten pairings and every previous source hash are preserved exactly.

All 200 matched non-learning runs remain identical, while all 400 matched learning runs differ.
The eighteen shared non-overlaps remain; ten belong to EC/EC, which learning parameters cannot change.
These descriptive counts are not a parameter-selection score or statistical equivalence test.
Historical seeds and figure provenance remain unknown. Four paired cohorts and final claim synthesis remain incomplete.

Independent R recomputes all 46,512 curve-pair and 168 endpoint categories from source intervals and verifies endpoint mean differences.
Two executions produce byte-identical Python reports. Existing independent cohort audits validate the consumed statistics.
This synthesis adds no simulation coverage or completed-study credit.

From the study directory, using new output paths:

```sh
python results/twelve-pair-parameter-comparison-2026-10-20/analyze.py results NEW_COMPARISON.json
Rscript --vanilla results/twelve-pair-parameter-comparison-2026-10-20/verify.R results NEW_COMPARISON.json NEW_VALIDATION.json
```

The R verifier requires `jsonlite` and `digest`.
