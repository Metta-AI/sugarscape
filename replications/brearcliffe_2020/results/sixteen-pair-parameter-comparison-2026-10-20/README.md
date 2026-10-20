# Sixteen paired cohorts

Both frozen parameter interpretations complete all sixteen pairings: 800 matched seeds and 1,600 trajectories.
Independent R verifies all 62,016 curve-pair classifications and 224 endpoints.
Of these endpoints, 166 overlap under both settings, four only under released settings, eight only under paper settings, nineteen under neither, and twenty-seven remain unresolved.
Raster overlap is descriptive, not statistical equivalence. Neither interpretation is selected.

The initial full comparison failed because the final released cohort directory lacked the `released-` prefix in the lookup table.
The one-line reference correction changes no simulation, metric, seed, or paper target.
The original source and failure are retained here. All scientific fields of the earlier thirteen-pair comparison remain exact.
A whole-file equality check failed only because the generalized command writes “13” instead of “thirteen” in its scope sentence.
`comparison-reference-correction.json` records both source hashes and that distinction.

Reproduce with `python compare_parameter_interpretations.py RESULTS NEW_REPORT`, then `Rscript --vanilla verify_parameter_interpretations.R RESULTS NEW_REPORT NEW_VALIDATION`.
