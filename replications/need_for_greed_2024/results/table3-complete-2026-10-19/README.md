# Table III reproduced with all 100 original utilitarian inputs

All 100 deposited utilitarian baseline configurations have complete audited trajectories, totaling 500,100 observations.
Every run finishes above the initial population of 250. No run goes extinct or ends at or below 250.

| Outcome | Paper Table III | Replication | Percentage-point difference |
| --- | ---: | ---: | ---: |
| Extinct | 0% | 0% | 0 |
| Worse | 0% | 0% | 0 |
| Better | 100% | 100% | 0 |

Independent R selects the exact 100 baseline filenames directly from the original deposited ZIP and verifies the endpoint census and percentages.
The public baseline analyzer repeats byte-for-byte on the real complete row; Tables I and II remain incomplete and have no reported comparison percentages.
This qualifies the analyzer’s complete-row behavior on real audited inputs.

Five newly recovered inputs contribute 25,005 observations. Their original configurations, source, seeds, complete prior trajectory hashes, and every metric pass the raw audit.
Reconciliation yields 417 unique inputs and 1,708,358 observations: 212 baseline and 205 sweep inputs.
Remaining coverage is 188 baseline and 9,895 sweep inputs. No sweep endpoint is substituted for a baseline.

The five-input snapshot is stored at `relh-sugarscape-evidence-20261017/need-for-greed-utilitarian-complete-001/five-completed.tar.gz`.
Fresh storage download matches all bytes and member hashes. The SHA-256 is `9e02d9aa577a416124465fb2a66e99aa42c5a5aa1641eed4e94985b37ee70562`.
Future regular checkpoints can include these same five inputs. Reconciliation must verify exact overlap and count each original input once.

This completes Table III under the released engine and deposited protocol. It does not complete the paper or establish independent-engine replication.
The full sweep, remaining tables, and death-rate measurement discrepancy remain unresolved.

## Reproduce

Run the public `analyze_baselines.py` against the original-input inventory and this complete audited inventory.
Then independently verify Table III from the original ZIP filenames:

```sh
Rscript verify_table3.R NEED_FOR_GREED.zip reconciliation.json tables.json NEW_VALIDATION.json
```

The R verifier requires jsonlite. The output must not exist. The included raw auditor and snapshot code preserve the five recovered inputs; earlier audits establish the other 95.
