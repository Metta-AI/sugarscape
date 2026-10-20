# Reproduce and audit the two manuscript figures

This bundle preserves the native plotting script, its exact canonical CSV input, generated figures and source hashes.
The `results/canonical/` subtree matches the paths consumed and produced by the unchanged author script.
The top-level images remain the original published evidence copies.

From the repository root, using the recorded plotting environment:

```sh
python replications/dogan_2026/audit_figure_series.py \
  replications/dogan_2026/results/figures-2026-10-15 \
  /absolute/new/figure-audit
```

The audit executes the plotting script, independently recomputes all 42 plotted means, and compares both generated images byte-for-byte with the native images.
`manifest.json` records Python 3.12.4 and the NumPy, pandas, Matplotlib and Pillow versions.
Different plotting environments can change pixels; arithmetic agreement and rendering identity remain separate checks.

The post-completion review found that publication had flattened the images and omitted the input CSV from their required runtime paths.
Those three files are restored from already retained, hash-matching evidence.
No simulation, plotted value, native script, tolerance or original artifact was changed.
The complete audit now runs directly against this committed bundle and reproduces `series-audit.json` byte-for-byte.
