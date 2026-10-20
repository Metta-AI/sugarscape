# Fixed initial-population death denominator diagnostic

The paper states that Figure 5 reports mean starvation-plus-combat deaths as a percentage of population, but does not specify the denominator’s time reference.
This diagnostic tests the fixed initial population of 250, retaining the stated death causes. The hypothesis and four averaging conventions were recorded before calculation in `protocol.json`.

| Condition | First quartile within envelope | Median within envelope | Third quartile within envelope |
| --- | ---: | ---: | ---: |
| 0.36 | 0/36 | 0/36 | 0/36 |
| 0.37 | 0/36 | 0/36 | 36/36 |

Each cell includes nine quantile definitions and four initial-row/post-extinction conventions. No complete quartile/median triplet agrees.
The fixed initial-population denominator therefore does not explain the figure under these alternatives. The existing primary measurement is unchanged.

All 200 complete trajectories are reopened and hash-checked, covering 985,742 observations.
Python arithmetic and independent NumPy array sums agree on all 800 per-run diagnostic values, with maximum scaled error 2.776e-16.
Independent R checks all 216 quantiles and plot distances; maximum quantile error is 2.221e-16 percentage points, with identical distances.

Distances ignore gaps in dashed curves. This is a measurement diagnostic, not statistical equivalence testing or a negative-paper verdict.
No simulations or unique-input coverage are added. Historical plotting details remain unresolved.

## Reproduce

Use the retained workspace, both complete cohort audits, and pinned original manuscript. Python requires NumPy and PyMuPDF; R requires jsonlite.

```sh
python aggregate.py /path/to/workspace /new/metrics.json
python compare.py /path/to/workspace /new/metrics.json /new/result
Rscript verify.R /new/result/0.36 /new/result/0.36/r-validation.json
Rscript verify.R /new/result/0.37 /new/result/0.37/r-validation.json
```

`validation.json` pins the protocol, scripts and uncompressed artifacts. Both successful and unsuccessful comparisons remain in the output.
