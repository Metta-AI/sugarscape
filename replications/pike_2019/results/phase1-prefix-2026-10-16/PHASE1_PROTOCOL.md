# Phase I ensemble

Run the unchanged historical standard, explicit and network variants for 100 replicates each, at 1,000 steps, matching the paper's ensemble sizes.
Keep Mesa seed 42 as in the released runners. Assign NumPy seeds 0–99, pairing inputs across variants.
Original NumPy states are unavailable; this is a new reproducible ensemble, not a claim to recover the original trajectories.
Seed zero has already been inspected as a pilot. Include it without selecting or excluding other seeds based on outcomes.
Use Mesa 0.8.5, NumPy 1.26.4, NetworkX 3.6.1, Python 3.11.14 and PYTHONHASHSEED=0.
Retain all outcomes, including extinction and errors. Stop on errors and preserve partial evidence; never silently replace a failed seed.
Freeze runner and protocol before starting. Execute one worker, with a 2 GiB free-space guard.

## Outcomes and analysis

Check every identity trajectory against native health records, and retain native reporter values separately from individual-agent counts.
Compare final survivor means with the cached standard 46.18, explicit 46.96 and network 46.68.
Report 95% seed-level intervals and paired differences between approaches; do not treat an insignificant difference as equivalence.
No author equivalence margin or original seed mapping is available.

Reproduce notebook price definitions: per-step geometric mean of transaction prices, sample standard deviation of log prices when there are at least two trades, and transaction count.
For the published dispersion histograms, pool defined per-step log-price standard deviations across runs, as the original notebook does.
Record steps with fewer than two trades separately. Absent trades must not become a zero price or zero dispersion.
Retain complete per-step results; report early steps 1–100 and late steps 901–1000 as descriptive diagnostics, including the number of defined observations.
Those windows are new diagnostics, not claimed original paper windows.

Reproduce the original independent two-sample t-test with equal variances and its erroneous doubling of p-values as an explicitly labeled historical calculation.
Also report the correctly computed two-sided values and paired seed-level differences.
Treat individual runs, not timestep samples, as independent units for uncertainty.
Record timing, but concurrent local workloads and different hardware preclude reproducing historical wall-clock differences from this ensemble.

Phase I alone does not complete this paper. Group thresholds, movement policies and shared-resource experiments remain required.
