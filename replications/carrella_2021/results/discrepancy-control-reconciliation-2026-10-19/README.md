# Published-score discrepancies and existing controls

The reconciliation checks all 90 Table 8 cells against the complete paired estimator table and verifies every linked primary evidence hash.
There are 75 reported scores: 38 primary matches and 37 discrepancies. Two fresh executions produce identical JSON.

| Estimator | Primary discrepancies |
| --- | ---: |
| Semi-automatic ABC 1D | 9 |
| Generalized additive model | 10 |
| Quantile random forest | 9 |
| Regression random forest | 6 |
| Neural network ABC | 3 |

Thirteen discrepant cells join to three retained, same-size aggregate controls:

- Four 1,250-input semi-automatic discrepancies have ten-seed controls. Three published values fall inside observed ranges; spice endowment remains outside.
- All five 1,250-input generalized-additive discrepancies remain outside printed-precision agreement under the notebook-parser control.
- Four 5,000-input quantile-forest discrepancies have the sequential-RNG/parser control. Only spice endowment matches printed precision in that alternative run.

These are selected aggregate controls, not an assertion that the other 24 cells lack diagnostics.
Historical-runtime point fits do not supply complete five-fold aggregate scores and are not substituted here.
The seed ranges are not confidence intervals. A secondary match does not identify the historical setup, prove causation, or replace the primary result.
No score receives new replication credit or a validated-negative label.

The remaining investigation should target unresolved historical randomness and numerical sensitivity by estimator and dataset size.
Repeating the already exact simulation replay would not isolate those estimator-stage causes.

```sh
python replications/carrella_2021/reconcile_discrepancy_controls.py /new/output
```
