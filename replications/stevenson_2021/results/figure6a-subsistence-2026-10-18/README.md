# Figure 6(a): complete subsistence-case reconstruction

The caption specifies infertility 5 and 10, puberty 1, birth cost zero and metabolism 4.
These differ from Table 1's metabolism-three societies; the earlier ensembles remain unchanged.
The generalized engine changes only the metabolism parameter and its accounting. Two 1,000-cycle native comparisons at metabolism three reproduce the pinned fixed engine's aggregate and individual outputs byte-for-byte.

Both printed subsistence cases complete 100 seeds (0–99) over 505 cycles, without extinction.
All 101,000 cycles pass independent population and resource balance checks. Wealth and Gini remain zero, as expected when agents begin with zero wealth and each harvested cell supplies at most their metabolism.
All commands, outputs, binary/source hashes and terminal statuses are retained, with archive member readback.

## Original vector evidence

The source-pinned extractor identifies both actual trajectories and fitted curves by their legend line styles.
It retains 1,165 vertices across four curves. Although the rendered time axis ends at 200, the original paths extend to cycle 505.
Visible and beyond-axis evidence remain separate. Omitted collinear vertices are not filled in; time-zero initialization is not compared with a post-action native state.
The comparison includes 995 actual-curve vertices at cycles 1–505.

| Infertility | Region | Vertices | Inside pointwise 95% seed band | RMS difference from seed mean |
| --- | --- | ---: | ---: | ---: |
| 10 | Visible, through 200 | 190 | 171 | 60.684 agents |
| 10 | Exported beyond axis | 305 | 245 | 43.030 agents |
| 5 | Visible, through 200 | 195 | 168 | 85.211 agents |
| 5 | Exported beyond axis | 305 | 272 | 74.643 agents |

The seed band uses the 2.5th and 97.5th percentiles independently at each recorded cycle.
It is descriptive, not a simultaneous confidence band or an equivalence test against an unknown author seed.
The original seed, time-origin convention and simulation implementation remain unresolved.
The original fitted curves are retained as evidence; this analysis does not assert recovery of their fitting procedure.
This executes the declared Figure 6(a) parameter cases but does not complete or invalidate the paper replication.

```sh
python extract_figure6a.py ORIGINAL_FIGURE_PDF NEW_EXTRACTION
python run_subsistence.py NEW_EXPERIMENT
python analyze_subsistence.py COMPLETED_EXPERIMENT NEW_EXTRACTION NEW_ANALYSIS
```

[The comparison plot](https://github.com/Metta-AI/sugarscape/blob/73c04a3c425b35121f16b43100a35f7b6ebbdf38/replications/stevenson_2021/results/figure6a-subsistence-2026-10-18/comparison.png) shows only original visible vertices against the complete ensemble. A separate Decimal calculation reproduces all 2,330 extracted coordinates within 1.43e-13. `verify_and_plot.py` retains the calculation and plotting procedure.
