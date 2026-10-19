# Complete selfishness 0.37 condition

All 500 original seeds pass independent audit: 2,452,673 observations, ten native extinctions, no exclusions.
Endpoint counts are 10 dead, one below the initial population, and 489 at or above it.
The median of per-run mean population is 1138.059688 including the initial row and 1138.2373 excluding it.
Zero-extending extinct trajectories through step 5000 leaves both medians unchanged.
All four medians lie within the extracted Figure 10 line bounds, 1132.783573–1143.028745.
These bounds describe graphical precision, not statistical uncertainty.

The full original cohort supports qualified agreement for this single condition.
Historical time averaging and quantile conventions remain unresolved; other time windows are not covered.
The full paper and supplementary sweeps remain incomplete.

`endpoints.json` comes from `summarize_supplement_condition.py ORIGINAL_ZIP TERMINAL_INVENTORY 37 NEW_OUTPUT`.
`means.json` and `per-run.csv` come from `../selfishness037-median-bounds-2026-10-19/analyze.py TERMINAL_INVENTORY ORIGINAL_ZIP NEW_OUTPUT`.
The inventory is `../selfishness037-terminal-prefix-2026-10-19/inventory/inventory.json`.
Both commands were repeated against the retained native archives; all three output files matched byte-for-byte.
Independent NumPy medians and endpoint arithmetic are recorded in `validation.json`.
Source archives, trajectories, configurations and audits are hash-checked by the production analysis commands.
