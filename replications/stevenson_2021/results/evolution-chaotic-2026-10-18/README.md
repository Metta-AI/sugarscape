# Conditional chaotic-parameter evolutionary reconstruction

All 100 seeds complete 500 action cycles without extinction, totaling 50,000 native cycles.
The audit validates 20,018,826 birth events against parental traits, joint trait totals against populations, and reproduction costs against the resource ledger.
Both pre-execution homogeneous controls match the fixed model byte-for-byte.
An additional infertility1/birthcost0 one-agent 1,000-cycle control also matches aggregate and individual observations exactly; it was run after the ensemble.

Infertility is initially uniform over integers 1–10, and birth cost is independently uniform over 0,10,...,90.
The experiment retains 830 zero-wealth, zero-age founders on distinct uniformly sampled cells, with exact parental inheritance and no mutation.
The chaotic case's initial population and trait ranges are declared reconstruction assumptions, not recovered author settings.
One generation is provisionally interpreted as one action cycle.
The original stable Figure 4 is not used as a numerical comparison target for this case.

| Metric | Ensemble mean at cycle 499 | Paper Table 1 evolved-chaos value |
| --- | ---: | ---: |
| Population | 888.74 | 916 |
| Mean age | 1.39440 | 1.41 |
| Wealth | 438.42 | 480 |
| Gini | 0.739173 | 0.73 |

All survivors have infertility1/birthcost0 in all seeds by cycle499.
Population across seeds at that cycle ranges from 178 to 1,839; the stable experiment ranges from 784 to 944.
This is observed variability under the declared parameter case, not a mathematical demonstration of chaos.
The pointwise ensemble ranges and Table1 comparison do not establish the author's sampling protocol or an acceptance threshold.
Longer-horizon statistics, intrinsic growth rates, and original evolutionary conventions remain outstanding; no completed-paper credit is claimed.

All original raw files are retained across disjoint archive parts, each below GitHub's single-file size limit.
The archive audit verifies every member exactly once by SHA-256 readback.
The summary means were independently recomputed from native CSVs with Python statistics.
The extended analyzer reproduces the existing stable comparison CSV byte-for-byte and preserves all stable summary values.

Use the same build and bounded execution commands as the stable experiment, adding `--scenario chaotic` to `run_evolution.py` and `analyze_evolution.py`.
The analyzer's figure argument remains the retained source-constraint extraction, but no stable-figure trajectory comparisons are computed for this scenario.
