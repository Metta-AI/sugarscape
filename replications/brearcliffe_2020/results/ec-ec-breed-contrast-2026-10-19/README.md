# EC/EC breed mapping and paired contrasts

The inspected paper, Figure 4 legend, released model, recorder, and digitizer consistently map A to blue and B to red.
The paper specifically discusses better EC/EC outcomes for A on page 14.
No reversed label was found in these paths. This does not verify every implementation detail or historical plotting step.
All 50 trajectory hashes match the previously audited complete cohort. No runs were added or relabeled.

The observed reversal is small relative to between-seed variation:

| Endpoint | Mean A minus B | Pointwise 95% paired bootstrap interval | Runs A > B / tied / A < B |
| --- | ---: | --- | --- |
| Wealth | -530.2023 | [-1569.2547, 527.0799] | 24 / 0 / 26 |
| Vision | -0.2893 | [-0.8284, 0.2554] | 23 / 2 / 25 |
| Metabolism | 0 | [0, 0] | 0 / 50 / 0 |
| Combat deaths | 1748.94 | [-1791.802, 5227.3485] | 26 / 0 / 24 |
| Starvation deaths | -0.46 | [-4.42, 3.46] | 24 / 3 / 23 |
| Mean age | -570.1457 | [-1700.5161, 579.4074] | 24 / 0 / 26 |
| Maximum age | -2082.78 | [-5809.5525, 1717.5815] | 24 / 0 / 26 |

All seven intervals include zero. This makes sampling variation a plausible explanation for reversed aggregate orderings, without establishing equivalence.
The diagnostic was selected after seeing the discrepancy. It uses the existing 20,000 whole-run draws and retains within-run breed dependence.
Intervals are pointwise, not simultaneous, and exclude uncertainty in the historical paper sample.
Independent R recomputes 56 quantities from the retained endpoint matrix and shared draws, with maximum scaled error 1.28e-15.
This check verifies arithmetic; it does not independently re-execute the simulation or validate the bootstrap random-number generator.
The original endpoint discrepancies remain recorded. Historical seeds and implementation fidelity remain unresolved; no negative or positive paper verdict is assigned.
