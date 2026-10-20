# First complete Table IV row

All 500 deposited inputs for selfishness 0.36–0.40 are audited, with 100 at each level.

| Outcome | Count | Reproduction | Published |
| --- | ---: | ---: | ---: |
| Extinct | 6 | 1.2% | 1.2% |
| Worse | 0 | 0% | 0% |
| Better | 494 | 98.8% | 98.8% |

No final population equals the initial 250, so the paper and released plotting code's different equality conventions coincide here.
Independent R recomputation of `complete-row.csv` reproduces all counts and percentages:

```sh
Rscript --vanilla verify_row.R complete-row.csv
```

The original bounded producer exited zero after completing its 400 assigned inputs; the previously audited 100 inputs at 0.37 complete this row.
Fresh storage readback verifies the terminal archive's 10,978,296 bytes and SHA-256 `e37e46385132fa911d65e95730e5f4a1d111e3bc9f94680cc8855acedb858934`.
Every extracted member hash, original configuration, and qualified payload matches; all 115,023 new observations pass raw audits.
The archive contains only the final 23 inputs; earlier checkpoints remain required evidence and are counted once.

The unique inventory reaches 1,005 inputs and 4,010,479 observations: 400 baseline and 605 sweep inputs.
All Tables I–III result fields remain unchanged except the inventory hash.
The sweep still needs 9,495 audited inputs; this result does not complete the paper.

`storage-intent.json` and `storage-status.json` identify the durable archive.
`audit_prefix.py` verifies its exact bytes and original deposited inputs; `reconcile.py` preserves all previous input records.
`table4-report.json.gz` retains every incomplete row without estimated percentages.
The reconciliation metadata now explicitly compares equality with the initial 250; the prior prefix script used 500 for that auxiliary field.
The primary table analyzer already used 250, and both equality counts are zero in this row; no outcome or comparison changes.
