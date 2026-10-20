# Direct-metric quartiles at two complete conditions

All 648 comparisons for wealth, remaining lifespan, and age at death fit the paper’s nominal curve envelopes at selfishness 0.36 and 0.37.
This covers 200 original inputs and 985,742 observations already audited. It adds no simulations or unique-input coverage.

| Condition | Measurement | First quartile | Median | Third quartile |
| --- | --- | ---: | ---: | ---: |
| 0.36 | Wealth | 36/36 | 36/36 | 36/36 |
| 0.36 | Remaining lifespan | 36/36 | 36/36 | 36/36 |
| 0.36 | Age at death | 36/36 | 36/36 | 36/36 |
| 0.37 | Wealth | 36/36 | 36/36 | 36/36 |
| 0.37 | Remaining lifespan | 36/36 | 36/36 | 36/36 |
| 0.37 | Age at death | 36/36 | 36/36 | 36/36 |

Each cell includes all four previously declared per-run averaging conventions and nine quantile definitions.
The analyzer verifies the existing independent NumPy metric hashes and values before comparison.
It extracts Figures 3, 4, and 6 directly from the pinned PDF and checks quartile ordering across all 101 plotted conditions.
Only the two complete native conditions receive simulation comparisons.

Independent R verifies all 648 quantiles and scalar distances. Maximum errors are 2.843e-14 measurement units and 5.684e-14 PDF points.
A second complete analysis produces byte-identical artifacts. Raw-trajectory arithmetic remains documented by the two original metric audits.

Together with the population comparisons, four measurements have median and quartile graphical agreement at both conditions.
Death rates remain unresolved: aging inclusion matches diagnostic medians but neither quartile.
Curve distances ignore dash gaps. Graphical compatibility neither establishes statistical equivalence nor identifies the historical plotting pipeline.
The full experiment still requires the remaining original inputs and complete table/figure comparisons. This is not a completed-paper result.

## Reproduce

Use the retained workspace containing both original metric audits and the pinned manuscript PDF.
Python requires NumPy and PyMuPDF; R requires jsonlite.

```sh
python analyze.py /path/to/workspace /new/result
Rscript verify.R /new/result/0.36-meanWealth /new/result/0.36-meanWealth/r-validation.json
```

Run the verifier for each of the six condition/metric directories. It derives condition and axes from each report.
The committed validation pins every decompressed report, vector, and verifier. Gzip timestamps are fixed at zero.
