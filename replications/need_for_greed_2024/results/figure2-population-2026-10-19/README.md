# Figure 2: population at selfishness 0.37

The 100-seed cohort’s median per-run population mean is 1,151.480303939 including the initial row, or 1,151.6606 excluding it. Both fall within the paper’s nominal vector stroke at selfishness 0.37. Zero extension after extinction leaves both medians unchanged.

The plotted median vertex maps to population 1,151.526076436. The observed points lie 0.001168 and 0.010344 PDF points from the median path; the stroke half-width is 0.341720 points. These distances establish graphical inclusion under the recorded axis calibration, not statistical equivalence or historical rounding precision.

`extract.py` reads Figure 2 directly from vector drawing paths on PDF page five. It verifies the paper hash, both axes’ labels, 101 evenly spaced vertices per curve, path continuity, and quartile ordering. The axes and caption were also visually checked on the rendered page. All 303 centerline vertices are retained as paper targets; only one condition has an audited cohort comparison.

Dashed quartile paths retain their dash metadata. Continuous ink is not inferred across gaps. This result does not compare the cohort quartiles or reproduce all of Figure 2.

Two complete extractions are byte-identical. Independent NumPy point-to-segment arithmetic agrees within 1e-12 PDF points. The four averaging conventions remain observationally indistinguishable at this plot resolution.

```sh
python extract.py AUTHOR_PDF AUDITED_SELFISHNESS037_JSON NEW_COMPARISON_JSON
```

The PDF and cohort hashes are recorded in `comparison.json`. This adds no new simulations or completed-paper credit.
