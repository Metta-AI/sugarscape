# Figure 4 ensemble-size experiment

Declared before executing `variance_curve.py`.
The first audit compared the reported approximately-200-run variances at the source's actual size of 220.
This follow-up covers all 17 ensemble sizes in the released `ensemble_sizer.py`, for all three parameter pairs.

Use independent simulations for every ensemble size, matching the source's `run_ensemble(k)` procedure.
Do not use nested prefixes of one large ensemble, which would change correlations across the plotted points.
Each simulation lasts 30 steps. Use contiguous, nonoverlapping seeds starting at 10,000,000;
iterate parameter pairs (1,1), (2,10), (4,7), then sizes in the released order.

Compute sample variance with denominator n−1, as in the author implementation.
Display the released numerical curve alongside the new curve and pointwise bootstrap 95% intervals
using 5,000 resamples and random seed 161803. These intervals are descriptive Monte Carlo uncertainty,
not simultaneous confidence bands or a retrospective equivalence criterion.

The source provides no numerical definition of variance stabilization and no original seed-level data.
Report differences without inventing a threshold for "stable after approximately 200 runs."
Retain every simulation and the pinned source constants. This experiment supplements, rather than replaces, the original audit.
