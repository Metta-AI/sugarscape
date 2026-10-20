# Death-rate quartiles at selfishness 0.36

The complete 100-seed cohort contains 490,477 observations. Fresh raw-trajectory NumPy arithmetic reproduces the committed metric artifact byte-for-byte.

| Definition | First quartile within envelope | Median within envelope | Third quartile within envelope | Complete triplets |
| --- | ---: | ---: | ---: | ---: |
| Stated starvation-plus-combat metric | 0/72 | 0/72 | 0/72 | 0/72 |
| Aging included, diagnostic only | 0/72 | 72/72 | 0/72 | 0/72 |

Each family covers the same eight declared averaging/denominator conventions and nine quantile definitions used at 0.37.
Adding aging deaths explains graphical median agreement under these alternatives, but does not reproduce the quartiles at either completed condition.
Aging inclusion contradicts the written death definition. It remains a diagnostic, not a replacement for the primary measurement.

Independent R verifies all 432 quantiles and scalar curve-distance calculations. Maximum errors are 2.221e-16 percentage points and 2.840e-14 PDF points.
Distances ignore dash gaps; the envelope is generous. Figure 5 dashed curves retain the lower/upper-quartile interpretation used for Figure 2.
The historical plotting pipeline remains unidentified. No completed-paper or validated negative-replication claim follows from these comparisons.

The later-author pooled control is not rerun for this condition. Its earlier 0.37 data are not substituted for 0.36.

## Reproduce

Use the retained workspace, original PDF, and committed `selfishness036-metrics-2026-10-19` artifacts.
First rerun that directory’s `validate_numpy.py` against its cohort and metrics to obtain a fresh `fresh-metrics.json`.
The comparison refuses metrics differing from the committed artifact. It requires NumPy and PyMuPDF; the verifier requires R with jsonlite.

```sh
python compare.py /path/to/workspace fresh-metrics.json /new/result
Rscript verify.R /new/result /new/r-validation.json
```

`validation.json` pins the scripts and decompressed result bytes. Compressed artifacts have deterministic gzip timestamps.
No simulations or unique-input coverage are added by this analysis.
