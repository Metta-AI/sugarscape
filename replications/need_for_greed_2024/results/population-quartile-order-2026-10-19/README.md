# Population quartiles constrain aggregation order

All 100 original selfishness-0.37 trajectories are freshly read and hash-verified: 495,265 observations.
The analysis independently recomputes four per-run population-mean conventions and matches the earlier retained values.
All three published population curves are rechecked against the original PDF vector paths.

Two aggregation orders are compared: quantiles across per-run means, and temporal quantiles after pooling runs at each timestep.
Both initial-row conventions and both observed/zero-extended extinction denominators are retained.
Nine standard quantile definitions produce 216 comparisons; none is selected after seeing its result.

| Type-2, including initial row | First quartile | Median | Third quartile |
| --- | ---: | ---: | ---: |
| Paper centerline | 1106.314 | 1151.526 | 1180.365 |
| Across per-run means | 1106.329 | 1151.480 | 1180.332 |
| Across pooled temporal means, zero extended | 1151.720 | 1177.400 | 1209.230 |

All 108 per-run comparisons fall within the nominal undashed stroke envelope; all 108 pooled-time comparisons fall outside it.
Distances are measured to complete polyline segments, deliberately ignoring dash gaps.
Inclusion therefore means geometric consistency, not proof of agreement with visible ink. Exclusion is stronger because the envelope includes gaps.
This supports averaging each run before cross-run quantiles for this population condition and rules out the four tested pooled-time conventions.
It does not identify the historical quantile algorithm, initial-row handling, extinction convention, or pipeline for other measurements.

Independent R arithmetic checks all 216 quantiles and segment distances.
Maximum value disagreement is 2.274e-13; maximum distance disagreement is 2.843e-14 PDF points.
The first verifier failed because JSON coordinates decoded as a list rather than a matrix; that script and correction are retained.
The corrected verifier then exposed two NumPy 1.26.4 type-3 median differences on odd-length temporal series.
Type 3 now uses the explicit nearest-even order statistic from the [R definition](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/quantile.html).
The other eight methods are unchanged. Initial reports and scripts remain, and both native-derived vector files are byte-identical.
This correction leaves the 108-versus-zero envelope result unchanged.

```sh
python analyze.py WORKSPACE NEW_OUTPUT_DIRECTORY
R_LIBS_USER=/path/to/library Rscript --vanilla verify.R NEW_OUTPUT_DIRECTORY NEW_R_VALIDATION.json
```

The scripts use the retained paper, original trajectory archives, and existing audited cohort paths.
The independent R verifier currently names the retained curve artifact's absolute workspace path explicitly.
The compressed vectors are published and read back, with hashes in publication-readback.json.
No simulations, unique-input coverage, statistical-equivalence claim, or completed-study credit are added.
The death-rate definition and full paper ensembles remain unresolved.
