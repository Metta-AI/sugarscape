# Complete egoistic Table 3 ensemble

All 500 original egoistic inputs are independently audited across 902,933 timestep observations.
The paper's Table 3 counts match exactly: 331 extinct, 5 worse, and 164 better.
No final population equals the initial 250, so the plotting/prose boundary difference does not affect this row.

The final 13 inputs cover indices `[487,500)` and add 31,213 observations.
The existing auditor checks source pins, configuration bytes, seeds, compressed and raw hashes,
every observation, contiguous timesteps, terminal conditions, and released outcome classification.
The union excludes agreeing overlaps and now covers 1,713 original inputs:
raw 500, altruistic 500, egoistic 500, and Bentham 213.
Later unaudited AWS outputs are excluded from these counts.

Raw trajectories remain at `recorded_root` in `audit.json`.
The frozen manifest, ledger, audit, comparison, and reconciliation command are retained here.
Run the audit command from any directory; run reconciliation from the repository root.
The first reconciliation invocation used the wrong working directory and failed before producing a union;
its log remains beside the raw evidence. The corrected invocation passed.
The homogeneous grid, egoistic figure comparisons, and whole-paper replication remain incomplete.
