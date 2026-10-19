# Heterogeneous50 death-rate discrepancy

All 500 original trajectories and 1,781,148 observations are revalidated against the completed population analysis.
Figure 20's median outline at 50% utilitarian agents spans 1.204152–1.399848 percent, using the visually checked 0–30% axis.
None of the eight tested statistic definitions lies inside that interval:

| Death numerator | Temporal aggregation | Including / excluding initial, percent |
| --- | --- | --- |
| Starvation + combat | Mean of per-step ratios | 0.230161 / 0.230207 |
| Starvation + combat | Ratio of per-run sums | 0.174354 / 0.174362 |
| Starvation + combat + disease + aging | Mean of per-step ratios | 1.648438 / 1.648768 |
| Starvation + combat + disease + aging | Ratio of per-run sums | 1.622072 / 1.622178 |

Each result is a median across all 500 run-level statistics. No extinct run is dropped.
The 150 zero-population observations cannot form a death/population ratio; they are excluded from ratio arithmetic and their death counts are retained separately.
These are explicit positive-population-row conventions, not a reconstruction of proven historical zero-denominator handling.

The released `plots/plot.py` uses starvation plus combat divided by population for its homogeneous time-series plot.
The supplementary Figure 20 implementation has not been recovered, so that helper does not uniquely define the paper statistic.
All reported death causes form a separate sensitivity case; it was not substituted for the released helper's numerator.

Independent R aggregation reproduces all eight medians exactly from retained per-run sufficient statistics.
That R check shares the per-step ratio sums; it does not independently recompute them from native observations.
A repeat full-trajectory calculation and PDF extraction produces byte-identical output.

This is an unresolved metric-definition or implementation discrepancy, not a validated negative replication.
Historical numerator, denominator timing, aggregation order, zero-population handling, and plotting code need further investigation.
The earlier agreement on population and wealth statistics remains scoped to those statistics; it does not erase this mismatch.
No new simulation or completed-study credit is added.
