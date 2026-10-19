# Full-data SABC1D estimator sensitivity

All ten prospective estimator seeds 1–10 complete unchanged five-fold estimation on the original 5,000 author inputs, with cross-validation seed 0.
R audits verify 37,750,000 exact input cells and 250,000 held-out parameter predictions. No seed is excluded or replaced.
Relevant package versions match the primary run for every seed; the original Table 8 scores remain unchanged.

| Parameter | Published | Observed ten-seed range |
| --- | ---: | ---: |
| Initial population | 0.545 | 0.542824–0.545846 |
| Maximum spice endowment | 0.521 | 0.514261–0.519726 |
| Maximum sugar endowment | 0.506 | 0.501849–0.510225 |
| Mutation probability | 0.371 | 0.366895–0.372255 |
| Reproduction wealth | 0.605 | 0.599929–0.605778 |

Four published values fall within observed seed ranges. Spice endowment remains outside, including allowance for three-decimal rounding.
Ten observed seeds do not identify the historical random stream or define confidence intervals.
Range inclusion does not establish agreement; exclusion does not establish a negative replication.

Python independently recomputes errors, training-mean baseline errors, coverage, interval widths, and normalized scores.
Maximum absolute difference from R is 4.973799150320701e-13 against a declared 1e-10 arithmetic tolerance.
Fresh archive readback verifies all 157 files. Repeating analysis from archived CSV/JSON produces byte-identical summaries, scores, hashes, and arithmetic checks.
All archived RDS bytes match the previously R-audited folds; the RDS audits were not rerun after extraction.
A separate object-storage import on the existing runtime node verifies the archive and all 157 member hashes again.

Archive: 174,476,952 bytes; SHA256 `4227a260533e1e33ed398210fd4733c898c8bfbdfe6f06d1d9abb58145cb080e`.
Local retained evidence: `/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-sabc1d5000-finalization-001/native-evidence.tar.gz`.
Durable object: `s3://relh-sugarscape-evidence-20261017/carrella-sabc1d5000-seed-sensitivity-001/native-evidence.tar.gz`.
Its manifest, `archive-validation.json`, is retained alongside it in object storage and this result directory.
The archive is retained externally to avoid duplicating its 166.4 MiB in Git.

Run the existing analyzer against the retained ensemble using `summarize_estimator_seeds.py ENSEMBLE NEW_OUTPUT`.
Launch configuration and exact R scripts remain in `../sabc1d5000-seed-sensitivity-launch-2026-10-19`.
No local estimator worker remains active. Primary totals remain 38 printed-precision matches and 37 unresolved discrepancies; the study is incomplete.
