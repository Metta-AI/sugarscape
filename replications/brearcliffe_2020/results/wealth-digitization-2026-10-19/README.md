# Figure 3 endpoint digitization

Thirty of thirty-two breed curves have visible endpoint pixels. The blue Q-Learning/Q-Learning and SARSA/SARSA endpoints remain unresolved through overlap.
`wealth-endpoints.json` records every selected pixel row, panel hash and image-derived wealth interval.
The fixed x302 column approximates the final plotted tick; x-axis tick labels are absent in these embedded panels.
Major grid lines y33=10,000 and y208=1 calibrate log10 wealth. Bounds include the full visible stroke and one extra pixel on each side.
These bounds describe raster resolution, not confidence intervals or an acceptance criterion. Full mean trajectories and ensemble uncertainty remain required.

The first extraction exposed four mislabeled panels in Figure 3's last row. Rounding y coordinates before sorting had moved the SARSA/SARSA panel ahead of its neighbors.
The corrected inventory groups nonoverlapping rows first, then sorts each row left to right. All four corrected assignments were checked against their embedded plot titles.
The rejected extraction is retained explicitly and must not be used in comparisons. Pixel measurements were unchanged; pairing labels were corrected.
Two extractions using the corrected inventory produce identical JSON bytes. No simulation output was used to choose pixel thresholds or calibration.
