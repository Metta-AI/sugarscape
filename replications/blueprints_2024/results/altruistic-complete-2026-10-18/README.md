# Complete altruistic Table 3 ensemble

All 500 original altruistic inputs have completed. Their 840,379 timestep
observations reproduce the printed Table 3 row exactly:

| Outcome | Paper | Native reproduction |
| --- | ---: | ---: |
| Extinct | 344 | 344 |
| Worse | 10 | 10 |
| Better | 146 | 146 |

Table 3 was visually checked on PDF page 12, printed page 195600.
The complete cohort contains no final population exactly equal to the initial 250.
Consequently, the documented plotting/prose boundary difference does not affect this row.
This completes the altruistic row alongside the previously reproduced Raw Sugarscape row.
It does not complete the paper or its four-model homogeneous ensemble.

The final batch's 426 trajectories cover original seed indices `[74,500)`.
The auditor validates source pins, original configuration bytes, output-only
configuration changes, all finite observations, contiguous timesteps, terminal
conditions, compressed/raw hashes, and released classification semantics.
Earlier audited intervals contribute the first 74 unique inputs.
Reconciliation verifies previous audit hashes and excludes two agreeing pilot repeats.

The final 25 inputs add 47,431 observations to the previous published checkpoint.
Total audited homogeneous coverage is 1,514 inputs and 3,038,827 observations.
Egoistic and Bentham remain incomplete; their last audited prefixes are 381 and 133.
Their running processes were not restarted.

`audit.json`, the frozen manifest and completed ledger identify the final batch.
`coverage.json` identifies the contributing prior audits and their hashes.
`table3-comparison.json` pins the visually inspected paper and outcome comparison.
Raw trajectories remain at the `recorded_root` in the audit.
The retained reconciliation command reproduces the union from those audits.
Re-run `audit_batch.py ARCHIVE RECORDED_ROOT NEW_AUDIT_DIRECTORY` for the complete
426-input batch, without `--allow-prefix`.
