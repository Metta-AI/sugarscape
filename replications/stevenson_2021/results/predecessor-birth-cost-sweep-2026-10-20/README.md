# Predecessor birth-cost sweep

The [earlier paper](https://arxiv.org/abs/2101.09817v2), Figure 14(a), exposes 96 run-1 parameter points at integer birth costs 1–96.
Its caption fixes infertility 10, puberty 1, and the 130,000–150,000-cycle window.
The extractor pairs the circle mean-age series and plus-sign Gini series by their common birth-cost coordinate.
Separate printed axes calibrate age and Gini. The maximum integer parameter residual is 0.003970.
Repeated extraction reproduces both output files byte-for-byte; source shapes, axes, and caption were visually checked.

At birth cost 40, the plotted run-1 mean age is approximately 2,351.66 and Gini is 0.34047.
Our existing 100-seed later-window mean age is 1,420.67; the target paper's Table 1 reports 2,264.
The discrepancy therefore also appears against an independently plotted predecessor result, rather than only a table entry.
This is a graphical comparison, not an uncertainty interval or a validated negative replication.

These 96 points do not identify the target Figure 3's 66 birth-cost parameter assignments.
Its neighboring plot extends beyond the mean-age range of this sweep; nearest-age matching alone cannot establish reused observations.
The source's run-1 seed and aggregation remain unknown. No Figure 3 grid, new simulation coverage, or completed-study credit is inferred.

```sh
python extract_birth_cost_sweep.py predecessor.pdf NEW_OUTPUT
```

Use the pinned source hash in `audit.json`. Analysis requires PyMuPDF and NumPy.
