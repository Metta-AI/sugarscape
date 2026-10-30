# Phase II: grouping without policy

Run 100 seeds for each of six conditions: explicit and network grouping, each at trade thresholds 1, 5, and 10.
Each run uses 200 initial agents, the released 50×50 landscape, and 1,000 steps.
Use NumPy and module-level random seeds 0–99, paired across conditions, and Mesa seed 42 as in the author's runners.
Set PYTHONHASHSEED=0, Mesa 0.8.5, NumPy 1.26.4, NetworkX 3.6.1, and Python 3.11.14.
Original NumPy states are unavailable. The selected pre-publication revisions are not verified paper pins.

`run_groups.py` exposes the hard-coded trade threshold and group policy as explicit parameters.
For the explicit approach, retain the author's ordered trade-dictionary traversal and threshold comparison, passing no movement policy.
For the network approach, pass the declared threshold to the native `net_group` implementation with no policy.
Preserve agent activation, metabolism, trading, movement, grouping, and native library behavior.
Do not load shared-pool, stale-network-node, or starvation-order corrections into this experiment.
Before launch, require byte-identical default-configuration records against native runners for both approaches.

Freeze the runner, adapter, batch driver, and this protocol in the output directory before execution.
Use one sequential worker; retain every outcome, exact command, file hash, and exit status.
Stop on failure or below 2 GiB free space; do not delete evidence, replace seeds, or silently resume incomplete runs.

## Analysis

Require all 600 runs before aggregate paper conclusions.
Reconcile individual identities and native health; keep native group/resource reporter counts separate from individuals.
Reconstruct geometric mean transaction prices, sample log-price standard deviation when at least two trades occur, and trade volume per step.
Preserve undefined prices and dispersion; do not substitute zero for missing trades.
Use runs as uncertainty units, paired across thresholds and approaches; report survivor means, 95% intervals, and paired differences.
Compare distributions and the published qualitative claim that grouping does not change outcomes.
Nonsignificance does not establish equivalence, and no author equivalence margin is available.
Compare with the independent Phase I ensemble only when both grids are complete and audited.
Concurrent local workloads preclude interpreting runtime as a historical timing replication.
Phase II alone does not complete the paper; Phase III policies and common-resource claims remain separate.
