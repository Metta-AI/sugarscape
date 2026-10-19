# Figure 16 heterogeneous population target

At 50% utilitarian agents, the printed median curve spans population **925.37–943.24** within its line thickness.
These are graphical bounds, not confidence intervals, quartiles, or a replication result.
The surrounding paper text defines the median of per-run mean populations over 500 seeds; endpoint population is a different quantity.
Time averaging, extinction handling, and historical quantile conventions remain unresolved.

The extractor checks the pinned PDF hash and intersects the filled magenta outline at all 99 interior percentages.
Both outline intersections are retained. The endpoints and dotted quartile curves are excluded.
PDF coordinate rounding and the approximate frame center add uncertainty beyond the ink bounds.
Page 17 was rendered and visually checked for axis ranges and curve identity before extraction.

Two real-PDF executions produced byte-identical outputs.
The generalized extractor also reproduces the existing Figure 10 CSV and JSON byte-for-byte.
The earlier Figure 10 validation hash records the historical extractor; its source remains in Git history.

From this checkout with PyMuPDF:

```sh
python replications/blueprints_2024/extract_population_target.py /path/to/blueprints-author-2024.pdf /new/output --figure 16
```

The current heterogeneous ensemble remains incomplete. No partial-cohort aggregate or whole-paper conclusion is claimed.
