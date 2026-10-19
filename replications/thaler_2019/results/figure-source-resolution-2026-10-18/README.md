# Figure 5a source and temporal alignment

The [author's paper-source repository](https://github.com/thalerjonathan/phd/tree/41e4eba6f6a5c3c661c227b383b3e57ed4844d71/writing/papers/publish/stmabs) contains the original figure asset.
It is byte-identical to the image introduced on July 27, 2018, under the filename `sugarscape_t60_environment.png`.
The publication source captions that image at time 50. The filename alone does not establish capture time.
The source image and the earlier independent published-PDF extraction agree on all 201 occupied cells.

The recovered filename motivated a diagnostic scan of exported times 0–100, keeping the qualified model, seed 42, and all initial conditions fixed.
Exactly one state matches every published occupied cell: **exported time 83**.
Times 49 and 50 still contain 206 agents and do not match.
No seeds, movement rules, landscape values, or resource parameters were fitted to the image.

A second complete 1,000-step native run reproduces all 203 output files byte-for-byte.
Across the 101 exported states, all 252,500 cells pass coordinate, occupancy, resource-bound, and agent-identity checks.
At time 83, all 201 agent positions match the figure.
The 2,299 unoccupied cells separate exactly into four resource-pixel classes:

| Native sugar | Yellow pixels | Cells |
| --- | ---: | ---: |
| 0 | 0 | 577 |
| 1 | 10 | 619 |
| 2 | 46 | 967 |
| 3 | 102 | 136 |

This resource characterization is exploratory, not a preregistered pixel tolerance.
Occupied-cell resources and all printed agent labels were not independently decoded.
The result resolves the earlier population-count disagreement for this figure through temporal alignment.
It supports a caption/time discrepancy, without claiming the original capture runtime is recovered.

The original MATLAB plotting script also supplies all 50 Figure 5b population values.
Every value matches the existing qualified replay exactly, independently of graph digitization.

A separate control executes the model modules committed alongside the original image.
That source retains an older regrowth expression and differs from the later qualified implementation.
It does not reproduce the screenshot in the declared time window; its full trajectory and scan remain preserved.
Both controls use GHC 8.4.3. The contemporaneous source declares an older resolver, so historical compiler parity is not asserted.

`audit_figure_source.py IMAGE NATIVE REPEAT PDF_GRID NEW_OUTPUT` reproduces the occupancy, resource, and repeat audit.
The two archives retain raw native outputs, source, build configuration, commands, and logs.
Every member was checked byte-for-byte; `archives.json` records hashes and sizes.
The paper's retry-ratio discrepancy and hardware-qualified performance interpretation remain unresolved.
This result does not add a completed study.
