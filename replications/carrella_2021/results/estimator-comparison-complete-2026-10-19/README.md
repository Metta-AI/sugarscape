# Complete paired estimator comparison

All 75 finite Table 8 scores now have author-model and independent-model estimates.
The other 15 table cells are explicitly unreported, not failed or omitted experiments.
The reconciliation verifies 262,500 held-out parameter predictions and 39,637,500 training/test input cells across 15 estimator/size combinations.
All inputs and individual audits are hash-pinned in `audit.json`.

Reproduce from the repository root:

```sh
python replications/carrella_2021/reconcile_estimator_comparisons.py replications/carrella_2021/ESTIMATOR_COMPARISON_INPUTS.json /new/output
```

The author-model comparison still has 38 matches at printed precision and 37 discrepancies.
Independent-model inputs use different random streams; paired scores do not establish statistical equivalence or a negative replication.
No whole-paper completion is claimed.
