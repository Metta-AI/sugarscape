# Method reproduction verdict

**Completed qualified method reproduction: Sugarscape case study only.**
This applies the user's October 19 criterion: faithfully implement and execute the method; numerical agreement is not required.
Earlier incomplete verdicts used a stronger historical-results criterion and remain preserved as dated evidence.
This reassessment changes the verdict, not the primary measurements, tolerances, or failed-run history.

## Evidence supporting completion

- All 5,000 fresh author-model simulations reproduce 750,000 archived summary statistics within the declared tolerance.
- The separate study model in this fork executes all 5,000 original parameter rows, retaining all 501 observations per row.
- Native whole-model checks cover the landscape, scheduling, cached utility, retained trade potentials, mutation bounds, and observations.
- All 75 finite Table 8 cells have complete author-data and independent-data estimator workflows across 15 method/size combinations.
- Retained audits verify 262,500 independent-data predictions and 39,637,500 training/test input cells; the other 15 published cells are NA.
- The fresh reconciliation in this folder reproduces every prior output byte-for-byte and rechecks its evidence hashes.
- Ten predeclared parameter settings cover 1,280 additional whole-model runs; independent R validates the reported distribution comparisons.

The evidence is linked from [model semantics](../../MODEL_SEMANTICS.md), [independent ensemble](../../INDEPENDENT_ENSEMBLE.md),
[complete estimator comparison](../estimator-comparison-complete-2026-10-19), and [parameter diagnostic](../parameter-cohorts-complete-2026-10-19).
The diagnostics do not establish stochastic equivalence across all parameters or resolve rare-event frequencies.

## Stated method, implementation choices, and diagnostics

| Area | Implemented method and qualification |
| --- | --- |
| Simulation | The pinned author NetLogo model is replayed directly. The independent Python model preserves audited rules and uses a different random generator and draw order. |
| Independent seeds | Original integer seed parts seed Python; equal labels do not mean paired stochastic trajectories across engines. |
| Estimators | Pinned author fitting functions, original data sizes, five folds, 146 nonconstant predictors, and original bootstrap/interval procedures are retained. |
| Estimator random stream | Each primary method/size starts at seed zero, unlike the notebook's shared sequential stream. This documented reproducibility choice can change stochastic fits. |
| Historical runtime | R 4.0.5 and mgcv 1.8-34 are a plausible version sensitivity, not verified author environment pins. All five folds and intervals were retained. |
| Result-seeking diagnostics | Additional fitting seeds, package/source-history checks, and rare-event controls investigate discrepancies. None replaces a primary score or selects a best seed/version. |

The simulation rules are not silently replaced by the fork's default sexual-reproduction model.
The independent implementation is study-owned code in the Metta-AI fork; it is not evidence of equivalence for every default engine configuration.
A different pseudorandom stream does not change the intended sampling procedure, but limits exact trajectory and historical-score claims.
The original seed/fold/package provenance remains an optional historical investigation rather than a requirement to reproduce the documented method.

## Numerical outcome and unresolved provenance

The primary author-data results match 38 of 75 printed scores; 37 differ. No rows, folds, or extreme observations were dropped.
All ten historical GAM seed controls retain zero of five printed-score matches; no seed is selected to improve agreement.
These discrepancies are not classified as validated negative paper results: the historical environment and stream are not fully identified.
No tweak has been established as necessary or sufficient to recover all printed results.
If later work finds such a tweak, record it separately from the stated method and retain the original comparison.

This counts one completed method study, not a wholly positive numerical replication or reproduction of the paper's other forty models.
