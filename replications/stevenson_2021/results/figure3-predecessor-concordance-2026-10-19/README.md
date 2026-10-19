# Figure 3 concordance with the preceding paper

All 362 target-paper Figure 3 markers correspond in family and drawing order to Figure 16 on page 21 of the author's [August 2021 predecessor](https://arxiv.org/abs/2101.09817v2).
Independent calibration of both panels gives maximum relative differences of 0.001756% in mean age and 0.023437% in wealth/Gini values.
Each marker comparison is retained, with no nearest-neighbor selection or dropped points.
This supports reuse of the plotted data; rounded graphics do not establish bitwise equality of original observations.

The preceding paper provides additional context but does not directly label this figure's parameter grid:

- Figure 14(a), page 19: birth-cost sensitivity with infertility 10, puberty 1, and a 130,000–150,000-cycle window.
- Figure 14(b), page 19: puberty sensitivity with birth cost zero, infertility 10, and a 10,000–20,000-cycle window.
- Figure 15(a), page 20: infertility sensitivity with puberty 1, birth cost zero, and a 40,000–50,000-cycle window.
- Figure 17 discussion, page 21: detail measurements use 10,000–20,000 cycles below mean age 21 and 200,000–225,000 cycles above mean age 20.

These captions concern distinct plots and overlapping age conditions. They are not silently assigned as one target-paper protocol.
Original numerical parameter values per Figure 3 marker, seeds, repetitions and aggregation remain unresolved.
No simulation agreement or paper completion is inferred.

```sh
python replications/stevenson_2021/audit_figure3_predecessor.py /path/to/stevenson-population-2021-v2.pdf /new/output
```

Both source hashes, calibration coefficients and full comparison rows are retained. Repeated execution produces byte-identical outputs.
