# Original selfishness and heterogeneous inputs

Use the paper-named v2024.1 release, commit b9ca671ab7591c7b3606f2d76c33eda344d626d1.
The deposited selfishness and heterogeneous archives contain 50,500 and 49,500 inputs respectively.
Keep every original seed, decision-model list, selfishness factor, and 5,000-step horizon.
Only the logfile destination changes. Preserve the native singular-to-plural configuration normalization in the selfishness archive.
Do not interpret its placeholder plural field (`none`) as the selected model.

Before larger batches, execute six declared full-horizon controls using the smallest original seed, 158402133555746433:

- Selfishness factors 0.0, 0.5, and 1.0.
- Mixed societies with 1, 50, and 99 utilitarian entries in the original 100-entry decision-model list.

These are coverage and runtime controls, not aggregate estimates or a replacement for the complete sweeps.
Finish 5,000 steps or native extinction. Validate every timestamp, seed, population, finite scalar and array metric, and terminal state.
Retain original/effective configurations, source and archive hashes, commands, logs, exit statuses, and full lossless trajectories.
The primary runner and independent auditor must agree before expanding.
A homogeneous endpoint comparison requires native trajectory parity; do not assume semantic identity from names alone.

Use four workers on existing CPU capacity with a two-hour overall cap and an eight-GiB initial free-space guard.
Record partial or failed runs without substituting another seed or shortening the horizon.
Additional disjoint batches must exclude these completed inputs and retain all interrupted evidence.
