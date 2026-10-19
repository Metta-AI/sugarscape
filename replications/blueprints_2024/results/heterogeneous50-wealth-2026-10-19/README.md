# Heterogeneous50 total societal wealth

All 500 audited trajectories contribute 1,781,148 observations to this complete-condition analysis.
The analyzer verifies each native archive and trajectory hash, then checks observation counts, contiguous ticks, and population sums against the earlier audit.
It reads `agentWealthTotal`, the author code's sum of current agents' wealth, rounded to two decimal places.
Exact rational arithmetic preserves those recorded decimals. It cannot recover unrounded internal totals.

The median of per-run mean total wealth agrees with Figure 17's plotted median at 50% utilitarian agents:

| Averaging convention | Median total wealth |
| --- | ---: |
| Observed rows, including initial state | 131604.22365626873 |
| Observed rows, excluding initial state | 131628.056101 |
| Zero after extinction, including initial state | 131604.22365626873 |
| Zero after extinction, excluding initial state | 131628.056101 |

Figure 17's median outline spans 130295.644086–132297.429696 at this coordinate, with axes visually checked on the pinned PDF page 17.
All four medians lie inside that graphical interval. Zero extension assumes wealth remains zero after native extinction; the final extinct observations are checked as zero.
Independent R arithmetic reproduces all four medians. Repeating full archive traversal and PDF extraction produces byte-identical per-run records and summaries.

The median-of-time-means interpretation follows the preceding heterogeneous population analysis and the Figure 17 discussion; historical plotting code and exact conventions remain unverified.
Ink bounds are not confidence intervals. This supports one wealth statistic for one complete condition, not the complete sweep or paper.
No new simulations or completed-study credit are added.
