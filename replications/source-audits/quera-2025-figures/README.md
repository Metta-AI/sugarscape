# Differentiable Sugarscape figure evidence

The arXiv v2 source archive supplies the original vector figures.
`source-audit.json` pins the archive and PDFs and records the historical-code and filename evidence.
The 150 finite-difference values come from six 25-point vector paths, with axis ticks visually checked against the PDF.
They are plotted coordinates subject to PDF rounding, not raw simulation data.
No gradient or calibration replication is established by this extraction.

Reproduce after downloading the pinned source archive:

```bash
pdftocairo -svg source/figures/sugarscape_gradients.pdf gradient-figure.svg
python3 extract_gradient.py gradient-figure.svg NEW_OUTPUT
```

The extractor retains path coordinates, tick calibration, and residuals in `audit.json`.
The gradient and calibration configurations must remain separate: the text and figure horizons differ.
The June wealth/vision change postdates the gradient PDF’s creation metadata, but timestamps alone do not establish the generating revision.
Filename tokens suggest training settings; they are not a complete training specification.
