# Full native Figure 11 A-C reconstruction

Population and stored resolution curves match the pinned author archive exactly.
The plot retains original CSV bin labels; bin one is unused zero, not a measured first round.
Resolution values retain integer truncation and the original occupied-population denominator.
No corrected interpretation is substituted into the archived numerical comparison.

All curves use three seed replicates. Shading shows the observed minimum and maximum,
not confidence intervals or independent hardware repetitions. The two timing curves
use different GPUs, compilers and CUDA versions; absolute timing equivalence is not claimed.

Across all sixteen widths, an ordinary least-squares line with an intercept fitted to
mean time versus grid cells has R² 0.999705 on H100 and 0.999422 in the archived V100 data.
The maximum absolute fit residuals are 0.204425 ms and 0.726805 ms respectively.
At 16,777,216 cells, mean step times are 14.635167 ms and 33.685000 ms.
These descriptive fits are consistent with the paper's linear-scaling description.
They are not a preregistered acceptance test, a complexity proof, or a hardware speedup estimate.

The reconstruction uses every native condition and excludes instrumented observer timings.
It does not splice historical visualization images into fresh-run results.
The remaining Figure 11 D-F comparison and historical visualization provenance remain separate.

```sh
python replications/richmond_2023/plot_native_results.py NATIVE/run PINNED_AUTHOR_DATA NEW_OUTPUT
```

Input hashes, every plotted mean/range and complete linear fits are in `audit.json`.
The PNG was visually inspected for labels, legends and clipping.
