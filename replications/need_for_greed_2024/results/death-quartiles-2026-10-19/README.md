# Death-rate median agreement does not reproduce both quartiles

The same 100 original selfishness-0.37 trajectories are freshly re-read and hash-verified: 495,265 observations.
Independent NumPy aggregation reproduces the earlier 2,400 primary measurements and aging diagnostics byte-for-byte.
The full original Figure 5 paths are extracted directly from the pinned paper PDF.
Lower and upper dashed curves use the first/third-quartile interpretation explicitly described for Figure 2.
The upper path has 100 vertices rather than 101; target coordinates are selected by selfishness, never by assuming a fixed vertex index.

Eight primary conventions, eight aging-inclusive per-run conventions, and two later-author pooled-time conventions are each evaluated under nine quantile definitions.
Initial-row, extinction-padding, and denominator alternatives remain separate.
Type 3 uses the explicit nearest-even order statistic qualified in the preceding population analysis.

| Definition family | Median comparisons within envelope | Lower-quartile comparisons within envelope | Upper-quartile comparisons within envelope |
| --- | ---: | ---: | ---: |
| Written starvation + combat metric | 0/72 | 0/72 | 0/72 |
| Include aging, per-run aggregation | 72/72 | 0/72 | 0/72 |
| Later author pooled-time calculation | 18/18 | 0/18 | 0/18 |

No tested definition/convention reproduces all three curves at this condition.
Thus the previous aging-inclusive median agreement does not explain the complete published death-rate summary.
Aging inclusion also contradicts the paper's written exclusion and remains diagnostic, not a replacement metric.

Distances use complete polyline segments and each curve's own stroke width, ignoring dash gaps.
This is a generous undashed geometric envelope, not a confidence interval or exact painted-pixel equivalence.
The thinner dashed curves are assessed with their own widths; the median's wider stroke is not substituted.
Independent R checks all 486 quantiles and scalar segment distances: maximum errors are 2.221e-16 and 2.843e-14 PDF points respectively.
All compressed analysis inputs pass publication readback.

```sh
python ../all-metric-comparison-2026-10-19/validate_numpy.py BLUEPRINTS_REPO COHORT_AUDIT METRICS_JSON NEW_FRESH_METRICS
python compare.py WORKSPACE NEW_FRESH_METRICS NEW_OUTPUT_DIRECTORY
R_LIBS_USER=/path/to/library Rscript --vanilla verify.R NEW_OUTPUT_DIRECTORY NEW_R_REPORT
```

The comparator verifies the fresh metrics against the prior retained report and pins the later-author CSV by its decompressed hash.
Historical plotting and measurement fidelity remain unresolved; the analysis does not establish a validated negative paper replication.
No new input coverage or completed-study credit is added.
