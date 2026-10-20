# Population aggregation at selfishness 0.36

The complete 100-seed cohort contains 490,477 observations. This analysis rechecks all trajectory hashes and changes no simulations or coverage counts.

Across nine quantile definitions, all 108 comparisons using per-run means fit the paper’s nominal curve envelopes. None of 108 time-pooled comparisons does.
Both initial-row conventions and both post-extinction denominators are included. This repeats the distinction previously observed at 0.37.

| Population statistic | Per-run alternatives | Time-pooled alternatives | Paper centerline |
| --- | ---: | ---: | ---: |
| First quartile | 1089.2993–1090.9435 | 1142.4300–1165.7653 | 1090.3157 |
| Median | 1134.3695–1135.9307 | 1156.8500–1180.4949 | 1135.7648 |
| Third quartile | 1171.3695–1171.9110 | 1190.3200–1214.6429 | 1171.6314 |

Independent R checks all 216 quantiles and segment distances. Maximum absolute errors are 2.274e-13 population units and 1.339e-14 PDF points.
Type 3 uses the previously qualified nearest-even order statistic; no new convention was selected to improve agreement.

Distances ignore gaps in dashed curves. Envelope inclusion establishes graphical compatibility only, not statistical equivalence or the historical plotting implementation.
The death-rate definition and other figure comparisons remain unresolved. This is not a completed-paper result.

## Reproduce

The workspace needs the previously audited archives and the committed `selfishness036-metrics-2026-10-19` results.
The analyzer requires NumPy and PyMuPDF; the independent verifier requires R and jsonlite.

```sh
python analyze.py /path/to/workspace /new/result
Rscript verify.R /new/result /new/r-validation.json
```

The retained R script names this workspace’s committed vector-curve path explicitly; relocate that path when reproducing elsewhere.
`validation.json` pins scripts, input artifacts, and decompressed output hashes. The vectors and comparison reports are gzip-compressed without timestamps.
