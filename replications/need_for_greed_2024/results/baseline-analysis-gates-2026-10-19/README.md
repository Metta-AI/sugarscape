# Tables I–III completion gates

The baseline analyzer selects only the 100 original inputs for each published ethical model.
It preserves the paper’s equality classification and the differing released-plot classification. Raw Sugarscape controls remain separate.
It never substitutes sweep endpoints for baseline configurations.

The real 412-input inventory contains 38 altruistic, 37 egoistic, and 95 utilitarian inputs, plus 37 raw controls.
All three rows are incomplete. The analyzer emits exact missing entries and counts, withholding percentages and comparison differences.
A second public-CLI execution produces byte-identical output.

Complete-row arithmetic remains unqualified until a real fully audited 100-input baseline is available.
The full paper remains incomplete; this preparation adds no simulation or completion credit.

```sh
python replications/need_for_greed_2024/analyze_baselines.py ORIGINAL_INPUTS.json.gz AUDITED_INVENTORY.json NEW_REPORT.json
```

The command verifies the pinned original-input archive, typed audit records, uniqueness, inventory totals, and literal published targets before comparison.
The output path must not exist. `validation.json` pins the analyzed source and result bytes.
