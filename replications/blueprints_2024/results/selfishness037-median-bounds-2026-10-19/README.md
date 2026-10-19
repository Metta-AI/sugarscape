# Bounds on the eventual 500-seed population median

We reread 453 audited original trajectories, comprising 2,217,626 observations and ten native extinctions.
Every archive, trajectory and source configuration matches its pinned hash.
The remaining 47 runs can take any mean population in [0, 2500]; no random completion-order assumption is needed.

| Averaging convention | Lower bound | Upper bound |
| --- | ---: | ---: |
| Observed rows, including initial population | 1126.079284 | 1143.144471 |
| Observed rows, excluding initial population | 1126.254500 | 1143.323100 |
| Zero after extinction, including initial population | 1126.079284 | 1143.144471 |
| Zero after extinction, excluding initial population | 1126.254500 | 1143.323100 |

Bounds use the arithmetic mean of ordered positions 250 and 251.
Replacing missing values with zero gives the lower bound; replacing them with 2500 gives the upper bound.
Exact rational order-statistic calculations independently match the augmented-cohort calculation.
These are deterministic bounds, not confidence intervals or point estimates from a random sample.

All four intervals contain Figure 10's extracted population ink bounds, 1132.783573–1143.028745.
This establishes compatibility only: remaining seeds can still put the final median outside the printed curve.
The ten extinct runs do not change these bounds when zero-extended.
Other averaging windows, excluding extinct runs entirely, and historical quantile conventions remain unverified.
No completed-condition or paper-completion credit is added.

Two executions reread the original archives and reproduce the per-run CSV exactly.
All substantive summary fields agree; the final report adds an explicit median definition.
Independent NumPy arithmetic agrees for all eight endpoints with zero floating-point discrepancy.
`validation.json` records source and target hashes; `per-run.csv` retains integer sufficient statistics and trajectory hashes.

Run from the repository root with the original, hash-pinned supplementary ZIP:

```sh
python replications/blueprints_2024/results/selfishness037-median-bounds-2026-10-19/analyze.py \
  replications/blueprints_2024/results/selfishness037-seventh-prefix-2026-10-19/inventory/inventory.json \
  /path/to/original-selfishness.zip /path/to/new-output
```
