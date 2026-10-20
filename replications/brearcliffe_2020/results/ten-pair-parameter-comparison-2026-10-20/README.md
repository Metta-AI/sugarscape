# Ten paired cohorts under both parameter interpretations

The first ten ordered pairings now have 50 seeds under each frozen interpretation: 500 paired inputs and 1,000 trajectories.
Released code uses alpha 0.9/gamma 0.8; the paper table uses alpha 0.8/gamma 0.9.
This synthesis reopens the complete-cohort summaries, means, and corrected paper comparisons, verifying all source hashes and shared targets.

| Endpoint raster overlap | Count |
| --- | ---: |
| Both interpretations | 102 |
| Paper parameters only | 8 |
| Released parameters only | 1 |
| Neither interpretation | 18 |
| Unresolved source target | 11 |

The eight paper-only overlaps concern three EC/Q-learning endpoints, one EC/SARSA endpoint, one Q-learning/Rule M endpoint, and three Q-learning/EC endpoints.
The released-only overlap is EC vision in the EC/SARSA pairing.
All individual metrics and both numerical means are retained in `comparison.json`.

All 200 matched runs in the four non-learning pairings have identical full trajectories.
All 300 matched runs in the six learning pairings differ.
Ten of the eighteen shared endpoint non-overlaps belong to EC/EC, which is unaffected by these learning-parameter changes.
Changing those parameters therefore does not explain every observed discrepancy.

Overlap counts are descriptive, not a parameter-selection score or evidence of statistical equivalence.
Adjacent raster columns are dependent, and historical seeds and figure provenance remain unknown.
Both interpretations remain required; the six remaining paired cohorts are not inferred from this subset.

The real analysis ran twice with byte-identical reports, preserving every result and source hash from the earlier four-pair comparison.
Independent R recomputes 38,760 curve-pair categories and 140 endpoint categories from source intervals, plus every endpoint mean difference.
The initial R verifier mistakenly treated retained coordinates on an explicitly excluded mislabeled panel as a valid target.
It now follows the explicit source status; the failed attempt is retained and the primary comparison remains unchanged.
Existing independent R cohort audits validate the input statistics; this synthesis adds no simulation coverage or whole-study completion credit.

From the study directory, using new output paths:

```sh
python results/ten-pair-parameter-comparison-2026-10-20/analyze.py results NEW_COMPARISON.json
Rscript --vanilla results/ten-pair-parameter-comparison-2026-10-20/verify.R results NEW_COMPARISON.json NEW_VALIDATION.json
```

The R verifier requires `jsonlite` and `digest`.
