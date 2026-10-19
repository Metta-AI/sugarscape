# Complete-condition population analysis

`summarize_population_condition.py` requires all 500 distinct original inputs for the selected selfishness or heterogeneous condition.
It checks the released configuration archive, configuration identities, audit hashes, native archive hashes, and full population trajectories.
Archive processing streams each relevant archive once without extracting trajectories to disk.

The median uses the 250th and 251st ordered per-run means, computed with exact fractions.
Four declared conventions include or exclude the initial row and either use observed rows or extend extinct populations with zeros through step 5000.
These alternatives expose historical ambiguity; they do not identify the original averaging or quantile convention.

The complete selfishness37 workflow reproduces all 500 per-run records and 2,452,673 observations from the earlier analysis.
All four medians match the prior report and independent NumPy calculations exactly.
A second execution produces byte-identical CSV and JSON outputs.
The actual heterogeneous50 inventory, with 376 audited inputs, is rejected before output creation.
A successful complete heterogeneous workflow remains pending.

Run from the checkout:

```sh
python replications/blueprints_2024/summarize_population_condition.py INVENTORY ORIGINAL_ARCHIVE NEW_OUTPUT --experiment heterogeneous --condition 50
```

This is analysis validation, not new simulation evidence or a completed replication study.
