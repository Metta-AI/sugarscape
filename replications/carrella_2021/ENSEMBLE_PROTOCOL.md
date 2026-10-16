# Complete author-model replay

Replay all 5,000 archived parameter rows, including their recorded random seeds, without changing model rules or parameters.
Use the pinned NetLogo 6.1.1 author model, OpenJDK 11.0.32.1, and the historical connector's 501 report-before-go observations.
Retain every six-observable trajectory and independently reconstruct all 150 statistics with NumPy 1.26.4.
Compare all 750,000 statistics with the archive using the previously declared `rtol=1e-10, atol=1e-10` replay tolerance.
Record every mismatch; do not replace seeds or discard failed rows.
This exact-input replay validates simulation and measurement, not statistical generalization to new seeds.

The runner reuses a workspace between inputs, resetting each input's seed and invoking the original `setup`.
This matches the original worker pool's lifecycle. Four independent processes cover [0,1250), [1250,2500), [2500,3750), and [3750,5000).
Each process owns a new output directory and stops on execution errors. Partial outputs remain evidence, not completion markers.

Before this ensemble, two execution paths were compared on the first ten inputs:
separate Java reporter calls and one NetLogo command containing the complete observation loop.
All 35,070 numeric trajectory values were identical, and both paths matched all 1,500 archived statistics.
The one-command path removes repeated host calls while retaining the same reporter order and model operations.
The last archived input is also checked before starting the ensemble.

`Replay.java` produces `row-N.csv` files. `compare_replay.py` rejects missing or extra rows in the declared range,
exports fresh summary statistics in the archive's column order, and records per-row hashes and mismatches.
A mismatch yields a nonzero exit after saving the comparison report.
The full-range manifest must account for every input before this experiment is considered complete.

Extinction does not shorten the original 501-observation driver loop. The model stops advancing its own tick and retains its terminal state.
Validate increments while the prior population is positive, and identical subsequent records after population reaches zero.
Summary trends and snapshot indices use observation number, not the frozen model tick.
