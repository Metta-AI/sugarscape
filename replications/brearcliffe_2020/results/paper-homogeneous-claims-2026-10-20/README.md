# Paper-table homogeneous breed contrasts

All four homogeneous pairings complete fifty runs, with seven A-minus-B endpoint metrics each.
Independent R reopens all 200 raw trajectories and verifies 2,800 endpoint values exactly and 252 summary values within 2.11e-15 scaled error.
All twenty-eight pointwise 95% bootstrap intervals include zero, as under released-code settings.
These intervals do not establish equivalence, simultaneous coverage, or the claimed activation-order cause.

EC/EC mean endpoint wealth is 1,790.5351 for breed A and 2,320.7374 for breed B.
The paired difference is -530.2023 with pointwise interval [-1,569.25473, 527.07987].
This does not establish the narrative claim that A performs equally or slightly better; “slightly” has no numerical margin.

Reproduce with `python analyze.py REPLICATION_DIRECTORY UNION_AUDIT_JSON`, then `Rscript --vanilla verify.R RESULT_DIRECTORY REPLICATION_DIRECTORY UNION_AUDIT_JSON`.
The analysis uses existing whole-run resamples and adds no simulations.
