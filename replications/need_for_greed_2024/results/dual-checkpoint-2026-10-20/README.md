# Two disjoint native checkpoints

Fresh audits cover 25 inputs from the unassigned shard and 25 from the active Table IV batch.
They add 240,456 observations: 115,431 and 125,025 respectively.
All original configurations match both deposited archives, qualified payload bytes match, and every trajectory passes the source-aware auditor.
Both sealed archives pass fresh durable-storage download, size, SHA-256, and all-member verification.

The new checkpoints are disjoint from each other and all 807 previously credited inputs; every prior record is preserved unchanged.
Coverage reaches **857 unique inputs and 3,270,331 observations**: 400 baselines and 457 sweep inputs.
Every Tables I–III result field remains unchanged except the inventory hash. All three baseline tables remain exact.

The active five-level Table IV row covers 402/500 inputs: 100 each at 0.36 through 0.39, and two at 0.40.
Six populations become extinct and 396 finish above the initial population; none equals it.
This execution-ordered prefix is not a representative sample and receives no population percentage or full-row verdict.
No Table IV row is complete. There are 9,643 unaudited sweep inputs remaining.

Each nested audit script verifies its sealed archive against original retained source/configuration evidence.
`audit.json` retains their disjoint union and source-audit hashes; `reconcile.py` checks that union against the prior inventory.
The repository table analyzers consume the frozen original-input manifest and the new reconciliation.
The original producers remain active. No new allocation or simulation restart was required.
The full paper remains incomplete; these checkpoints add evidence, not a completed study.
