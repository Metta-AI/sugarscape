# Figure 10 graphical target

The median curve at selfishness 0.37 crosses population **1132.78–1143.03** within its printed line thickness.
These are graphical bounds, not confidence intervals, quartiles, or a replication result.
The caption defines medians of per-run mean population across 500 seeds; endpoint population is a different quantity.
Time averaging, extinction handling, and the historical quartile convention remain unresolved.

The extractor reads the pinned PDF directly, checks its hash, and intersects the filled magenta outline at 99 interior factors.
It retains both intersections rather than treating the outline vertices as original observations.
The frame-center approximation and PDF coordinate rounding add uncertainty beyond the reported ink bounds.
The endpoints and dotted quartile curves are excluded.

Reproduce from the study checkout with PyMuPDF:

```sh
python replications/blueprints_2024/extract_selfishness_target.py /path/to/blueprints-author-2024.pdf /new/output
```

Two real-PDF executions produced byte-identical CSV and JSON files.
`validation.json` pins the extractor and outputs. No simulation comparison was performed.
The separately retained complete-condition gate still requires all 500 original seeds before aggregate comparison.
