# Complete Egoist curves against published figures

All 500 original inputs contribute 902,933 native timestep observations.
Independent aggregation and the unchanged released parser agree on all 30,006 compared values.
Population means agree exactly; other differences satisfy the existing relative/absolute tolerances of `1e-12`/`1e-8`.
Missing post-extinction rows contribute zero, with the denominator fixed at 500.
Derived ratios divide ensemble means, rather than averaging individual ratios.

Cyan Egoist legends and axes were visually checked on PDF pages 13–14.
Every relevant vector-path vertex is compared using the existing 0.005 PDF-point tolerance.

| Figure | Vertices | Maximum error, PDF points |
| --- | ---: | ---: |
| 4 | 4,860 | 0.003877 |
| 5 | 4,902 | 0.004306 |
| 7 | 4,995 | 0.004676 |
| 8 | 4,864 | 0.003941 |
| 9 | 4,811 | 0.003263 |

All 24,432 vertices in these five figures pass.
Figure 6 retains the death-definition discrepancy seen in Raw and Altruist:
the released parser sums starvation and combat, while the published curve matches all four recorded causes.
The released definition's maximum error is 42.732342 PDF points.
All-cause deaths match all 4,992 vertices, with maximum error 0.003922 points.
At timestep 5,000, the respective rates are 0.001168173 and 0.015011025.
Mean deaths are 0.320 starvation and 3.792 aging, with zero combat and disease deaths.
No simulation behavior changed.

Both definitions were fixed before inspecting these Egoist comparison errors, based on prior Raw and Altruist findings.
This does not identify the exact historical plotting revision or constitute an independent preregistered result.

![Egoist reproduction and published paths](https://github.com/Metta-AI/sugarscape/blob/9414e7b75bd0dc444e8efe24cf2aecab529b4829/replications/blueprints_2024/results/egoistic-figures-2026-10-18/comparison.png)

The six-panel comparison was visually inspected and retains both death definitions.
This completes this model's plotted curves; the four-model ensemble and whole paper remain incomplete.

`protocol.json` records paths, axes, definitions, and tolerance.
`timeseries/` retains parser audit, input ledger, means, command, and hashes.
Every compressed export was checked against its original bytes; `provenance.json` pins exported evidence.
Full native staging remains in the external `blueprints-egoistic-timeseries-001` evidence directory.

To repeat aggregation, run the repository's `audit_timeseries.py` with the saved coverage,
pinned author engine, `egoisticHalfLookaheadBinary`, and a fresh output directory.
Verify and copy the retained `timeseries/provenance.json` into that directory.
Run `audit_figures.py PAPER.pdf NEW_TIMESERIES NEW_FIGURE_AUDIT` with PyMuPDF and NumPy installed.
For plotting, decompress the retained CSV files and run `plot.py` with NumPy and Matplotlib installed.
