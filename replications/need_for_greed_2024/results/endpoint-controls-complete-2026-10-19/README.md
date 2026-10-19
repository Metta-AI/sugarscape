# Complete original endpoint controls

All six preselected controls complete through timestep 5,000 or native extinction.
Each baseline/sweep pair is byte-identical at seed 238165197779399277.

| Selfishness | Observations per input | Final population |
| --- | ---: | ---: |
| 0.0 | 137 | 0 |
| 0.5 | 5,001 | 978 |
| 1.0 | 5,001 | 1,132 |

The recovered level-1 sweep took 872.629 seconds, within its original 1,800-second bound.
Both recovered outputs preserve every byte of the two original timed-out prefixes.
All three baseline hashes reproduce the prior retained baseline evidence.
Original failures remain in the endpoint recovery launch evidence; they are not overwritten.

The audit reopens all six raw trajectories, source files, original configurations, archive, receipts, and historical baseline hashes.
It checks consecutive timesteps, seed, finite scalar/array values, population bounds, and completion.
Two invocations produce byte-identical reports. All six published gzip trajectories decompress to their recorded original hashes.

Reconciliation checks the frozen 10,500-input partition and proves these six inputs are disjoint from the previous 164.
Coverage is now 170 inputs and 835,607 observations: 67 baseline and 103 sweep inputs.
Another 333 baseline and 9,997 sweep inputs remain, including the 400-input cloud batch that receives no credit here.
Two reconciliation invocations produce identical reports.

Reproduce with the retained workspace artifacts:

```sh
python audit.py WORKSPACE/sugarscape-replication-evidence NEW_AUDIT.json
python reconcile.py WORKSPACE NEW_RECONCILIATION.json
```

This validates endpoint configuration equivalence at one preselected seed, not across all seeds.
The paper's full ensembles, aggregation conventions, and death-rate definition remain unresolved. No completed-study credit is added.
