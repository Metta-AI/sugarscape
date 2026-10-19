# Evolutionary computing claim-level contrasts

Page 14 describes evolutionary computing (EC) as accumulating more wealth and fewer combat deaths than the reinforcement-learning methods.
It also describes fewer starvation deaths than the other methods.
This analysis covers all six relevant released-code matchups in both breed orientations: 300 already-audited inputs.

All 14 directional endpoint comparisons agree with those claims: four wealth, four combat, and six starvation contrasts.
Each corresponding pointwise 95% whole-run bootstrap interval excludes zero in the stated direction.
The analysis retains the other four comparisons as context, including EC's lower wealth and higher combat deaths against Rule M.

Differences below are EC minus its opponent at tick 20,000. Death columns are cumulative counts, not rates.

| Pairing (group A / group B) | Wealth difference | Combat-death difference | Starvation-death difference |
| --- | ---: | ---: | ---: |
| rule-m-ec | -175.47 | 4,126.12 | -27,944.42 |
| ec-rule-m | -195.28 | 4,400.96 | -26,886.42 |
| ec-q | 632.31 | -3,086.46 | -32,537.98 |
| ec-sarsa | 637.55 | -3,680.52 | -34,337.44 |
| q-ec | 638.81 | -3,667.90 | -34,688.76 |
| sarsa-ec | 629.92 | -3,635.02 | -34,323.86 |

For Rule M/EC, mean combat deaths are 20,706.08 for EC and 16,579.96 for Rule M: 24.89% more for EC.
For EC/Rule M, they are 20,516.18 and 16,115.22: 27.31% more for EC.
All four endpoint mean ranges overlap the corresponding corrected Figure 6 raster ranges.
The paper's description of near equality supplies no numerical equivalence margin, so these contrasts do not establish equivalence or a paper-negative finding.
The mislabeled EC/SARSA Figure 6 panel remains excluded from graphic agreement judgments; native contrasts assess the textual claim separately.

Python reopens and hashes all 300 trajectories against the cumulative audit and cohort summaries.
Independent R reopens them, checks all 1,800 endpoint values exactly, and verifies 270 summary values within 3.553e-15 scaled error.
Both wealth contrasts against Rule M also reproduce the opposite signs of the prior independently verified Rule M analysis.
Full-curve sign counts retain every tick after initialization; no favorable time window was selected.

This analysis was specified after cohort plots were available. Intervals are pointwise, not simultaneous or estimates of the authors' unavailable sample uncertainty.
No new simulation coverage or completed-paper credit is added. The remaining ensembles, parameter interpretation, and whole-paper synthesis remain outstanding.
