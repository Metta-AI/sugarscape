# Completed method replication: qualified author-code result

The Sugarscape experiment in [Brearcliffe and Crooks](https://doi.org/10.1007/978-3-030-83418-0_3) is complete under both documented parameter interpretations.
The result is mixed. It is neither an exact historical numerical replication nor a validated negative replication.
The [released model](https://www.comses.net/codebases/ffb52fc3-69e1-4bbd-b5d7-fa460617f74e/releases/1.0.0/) runs in native NetLogo 6.1.1 with its bundled matrix extension.

All sixteen ordered method pairings have fifty replicates per interpretation, each with initialization and 20,000 transitions.
The complete audit covers 1,600 trajectories and 32,001,600 observations.
Independent R verifies every cohort's means, sample deviations, and fourteen endpoint metrics using 20,000 whole-run bootstrap draws.
The evidence review links all input hashes to their cohort summaries and prior verified storage evidence.

## Findings

- Rule M has higher endpoint wealth, vision, and metabolism in all six opposing-method matchups under both settings. Early EC wealth advantages prevent an all-time dominance claim.
- EC claim analyses support fourteen stated endpoint directions across both settings. The near-equality wording has no numerical margin; released EC combat deaths exceed Rule M by 24.9–27.3%.
- Q-learning has higher endpoint wealth than SARSA in both orientations and settings. Paper-setting paired differences average 1,068.16565 and 1,063.05835; early mean reversals remain.
- All twenty-eight homogeneous A-minus-B pointwise intervals include zero under each setting. This does not establish equivalence or the proposed activation-order explanation.
- All sixty-four metabolism curves and sixteen EC vision curves finish below their initial mean. Upward intermediate changes prevent a universal monotonic interpretation.
- Among 224 figure endpoints, 166 overlap raster ranges under both settings, four only under released settings, eight only under paper settings, and nineteen under neither. Twenty-seven remain unresolved.

These comparisons are descriptive. The paper's plotted ranges describe digitization uncertainty, not historical sampling uncertainty.
Neither overlap nor non-overlap establishes equivalence or a statistically validated contradiction.
The native results support several directional findings while leaving specific graphical and narrative discrepancies unresolved.

## Reconstruction and discrepancy checks

The released model uses learning rate 0.9 and discount 0.8; the manuscript table reverses them.
Both 800-run ensembles were frozen before outcomes. No setting was selected for better agreement.
The release's five BehaviorSpace repetitions were expanded to the manuscript's fifty, with prospectively frozen seeds because historical seeds were unavailable.
Population remains 400 per breed, with the released map, combat, corner placement, replacement and growback settings.

The initial recorder consumed random numbers while measuring agent-set statistics.
The corrected recorder isolates measurement randomness with `with-local-randomness`.
It matches native BehaviorSpace exactly across 256,256 values for all sixteen pairings through 1,000 ticks.
Separate full-horizon Rule M/EC, Q-learning/SARSA and EC/EC controls each match all 320,016 values.
The failed original recorder and correction remain available; failed qualification outputs are excluded from the frozen ensemble.

Paper panel labels, horizontal calibration, and metric/breed mappings were reviewed before final comparisons.
Mislabeled, duplicated, or occluded figure segments remain unresolved, rather than supplying invented targets.
A final cohort-directory lookup error was corrected without changing data or scientific calculations; all earlier thirteen-pair scientific fields remain exact.
The complete-horizon R trend check initially failed because decimal parsing changed near-zero differences.
Exact decimal-text ordering validates all eighty original Python step counts without a tolerance or simulation rerun.
Those counts include stored-mean rounding noise and are not a substantive measure of behavioral fluctuations.

Every original failed check is retained alongside its correction. None motivated parameter tuning or selective seed replacement.
Historical seeds, plot aggregation details and historical hardware remain unavailable.
The runtime narrative, including the reported “as much as seven times” ratio, is not a controlled replicated benchmark.
Execution timings are retained as provenance, not evidence for that historical ratio.

## Evidence

- [Final native cohort and 1,600-input audit](../paper-sarsa-sarsa-complete-cohort-2026-10-20).
- [All sixteen parameter comparisons and independent R check](../sixteen-pair-parameter-comparison-2026-10-20).
- [Paper homogeneous contrasts](../paper-homogeneous-claims-2026-10-20) and [released homogeneous contrasts](../homogeneous-breed-contrasts-2026-10-19).
- [Rule M](../paper-rule-m-claims-2026-10-20), [EC](../paper-ec-claims-2026-10-20), and [Q-learning/SARSA](../paper-q-sarsa-claims-2026-10-20) analyses retain both interpretations.
- [Complete-horizon trends and parser discrepancy](../complete-horizon-trends-2026-10-20).

Run `python review_evidence.py RESULTS NEW_REPORT` to repeat the final linkage audit.
Use each linked directory's commands to reproduce its analysis from retained raw archives.
The qualified method criterion is met; unresolved historical numerical agreement remains explicit.
