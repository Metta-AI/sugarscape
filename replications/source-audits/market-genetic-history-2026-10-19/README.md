# Historical market-algorithm data recovery

Both public branches point to the same pinned revision; no tags were returned.
The current analysis notebook has one path-history commit, uploaded December 21, 2023.
The API returns no history for its referenced `Sugarscape_Alt -10-25-2023` directory.

Path-history searches recover basic-only and optimizer-only datasets in [May 4, 2023 revision da76183](https://github.com/zacharyejohnson/Academics/tree/da76183d6fcc3dbcb18a78bfd38bc1c2dbed2cd7/Sugarscape/parquet).
Five sampled population files match their Git blob identities and retained SHA-256 hashes.
The two aggregate tables each contain 30 run columns and 5,000 observations, plus a mean and index column.
Every population is finite, nonnegative and integral; all runs start at 2,000 agents.
Run-zero columns exactly equal the corresponding individual files. The mixed population sample also has 5,000 observations.

The initial arithmetic check assumed double precision and failed with maximum absolute error 0.0000569661458485.
Inspection identifies stored single-precision means. Independent scalar sums rounded to that stored precision reproduce all 10,000 mean values exactly.
The initial checker and precision diagnostic remain preserved. This is a precision correction, not evidence of an author calculation error.

These are earlier, shorter experiments. The [paper](https://jameslcaton.com/MarketAlgorithmAsDistributedGeneticAlgorithm-Johnson%2CCaton%2CMiljkovic%2CRayamajhee.pdf) requires 100 repeats and 60,000–100,000 periods.
The historical driver at the same revision says 30 repeats and 800 periods, so its defaults also fail to identify the saved 5,000-observation experiment.
The October experimental source/data and reproducibility settings remain unresolved. No simulation, study PR, or completed-paper credit follows.

Raw population files and complete Git trees remain in `sugarscape-replication-evidence/market-genetic-history-002`.
Run `python check_population.py EVIDENCE_DIRECTORY NEW_REPORT` with PyArrow to reproduce the arithmetic checks.
