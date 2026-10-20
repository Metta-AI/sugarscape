# Figure 3 vector targets

The author-source PDF contains 181 markers per panel: 50 puberty, 65 infertility and 66 birth-cost points.
All 362 marker centers are retained in `markers.csv`, including their source drawing indices and page coordinates.
The reconstruction reproduces the visually inspected source shapes.

All four axes are logarithmic, including the Gini axis. Tick calibration residuals are below 0.005 PDF points.
Filled circles identify puberty, open circles infertility, and paired diagonal strokes birth cost.
Arrow annotations and legend symbols are excluded by pinned drawing ranges and shape checks.
Two independent CLI executions produce byte-identical extraction outputs.

The figure does not label numerical parameter values per marker, seeds, repetitions, or averaging windows.
Marker ordinals are not parameter values; ordinals in separate panels are not asserted to identify paired simulation runs.
The exported marker centers retain graphical rounding and cannot replace raw simulation observations.
No simulation match or paper completion is claimed.

```sh
python replications/stevenson_2021/extract_figure3.py /path/to/wealthVmAge_giniVmAgeG_SSC-eps-converted-to.pdf /new/output
```

The PDF comes from the retained [arXiv v2 source](https://arxiv.org/src/2108.11892v2); its SHA-256 is checked before extraction.
