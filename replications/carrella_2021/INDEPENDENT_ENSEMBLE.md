# Independent 5,000-input ensemble

Run the independent study model on every row of the author's pinned 5,000-input parameter table.
Keep the complete ordered table, including the first 1,250-input subset used by the smaller estimation experiment.
Do not select rows based on earlier discrepancies, extinction, or performance.

Preserve all five parameters exactly. Convert the archived seed's integer part into the independent Python generator's seed, recording both values.
This is a reproducibility convention for this implementation, not an assertion that Python and NetLogo share random streams.
The independent model and runner are frozen before launch.
Use 501 observations taken before each step, including unchanged terminal states following extinction.
Generate the original six time-series summaries and nineteen snapshots for each of six observables: 150 statistics per input.
The trend is the ordinary degree-one polynomial fit against observation index; standard deviation uses population normalization.

Retain every trajectory, source/data hashes, per-row completion and elapsed time, and all failures.
Each completion requires finite values, correct observation order, valid population and resource bounds, and a lossless trajectory archive.
A native-model exception or invariant failure stops the batch and preserves its partial output; it is not a completed simulation or negative replication.
Use a fresh directory for any resumed interval, with explicit nonoverlapping row ranges.

The initial analysis will report all parameter-conditioned differences and all 150 statistic distributions against the original reference.
Equal seed labels do not justify exact trajectory equality or ordinary paired-random-number variance assumptions.
Do not infer a statistical acceptance margin from these outcomes.
Discrepancies require model and measurement diagnosis before any negative verdict.
This ensemble is required input to independent estimator comparisons, not a replacement for the original author replay or remaining estimator runs.
