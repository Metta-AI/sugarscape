# Whole-table analysis completion gates

The public analyzer partitions all 10,100 original sweep configurations across the paper's 23 Table IV rows.
It verifies the pinned input manifest, typed audited records, unique entries, observation totals and complete per-row input membership.
Baseline records cannot substitute for sweep records, and no unknown original entry is accepted.

A row receives percentages and exact percentage-point differences only when every original input is audited.
Incomplete rows retain counts, equality outcomes, required inputs and explicit missing entries.
Both the paper's less-than-or-equal classification and the released plot's strict-less-than classification are retained.
Published percentages remain unchanged, including the 100.2% sum at 0.81–0.85.
No rounding convention, significance threshold or completed-paper verdict is inferred.

The real 337-input inventory yields 180 audited sweep inputs and zero complete rows.
The 0.36–0.40 row exactly reproduces the prior audit: 177 inputs, three extinctions, 174 above the initial population and 323 missing.
A second CLI invocation produces byte-identical output. A duplicate-entry inventory is rejected before output creation.
All incomplete rows suppress percentages and comparisons. Complete-row reporting remains unvalidated until a real full row is available.

```sh
python replications/need_for_greed_2024/analyze_table4.py ORIGINAL_INPUTS.json.gz AUDITED_INVENTORY.json NEW_REPORT.json
```

The original manifest is retained under `need-for-greed-remaining-plan-001/prepared/inputs.json.gz` in the evidence directory.
The qualified inventory is `need-for-greed-table4-prefix-003/reconciliation.json`.
This aggregation consumes prior raw audits; it does not replace them or add simulation credit.
