# Paper-table SARSA / Rule M cohort

All 50 inputs complete through tick 20,000. Full trajectory audit adds 1,000,050 observations. Canonical coverage is 1,450 inputs and 29,001,450 observations: 800 released-code and 650 paper-table inputs. The remaining 150 paper-table inputs and final claim synthesis are incomplete.

Independent R checks 320,016 means, 320,016 sample standard deviations, fourteen endpoints, and 20,000 whole-run bootstrap draws. Maximum scaled arithmetic discrepancy is 3.09e-14.

All fourteen endpoint mean ranges overlap readable paper targets under the corrected horizontal calibration. There are 3,786 readable curve records and ninety unresolved records. These are descriptive raster comparisons, not equivalence tests or historical-parameter identification.

The 37,712,588-byte native archive passes fresh storage readback and every member hash check. SHA-256: `a7efe51a853d53f8680ece24f6885ef377b90f9db87fa78432a8f822d3603665`.

The frozen paper-table settings remain learning rate 0.8 and discount rate 0.9. Released-code settings remain separate. No numerical target was used to change either interpretation.

Validation: `readback.py` performs the complete union audit and cohort arithmetic; `verify_cohort.R` independently recomputes raw-input statistics; `compare_curves.py` uses corrected paper targets; `verify_storage.py` verifies a fresh remote archive download. Exact commands and successful terminal receipts are retained here.
