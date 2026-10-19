# Learning-parameter dependency audit

The pinned source has exactly eight uncommented references to learning-rate or gamma: two declarations, two setup assignments, and four reads inside Q-learning/SARSA updates.
Those update procedures are called only by the two breeds' corresponding action guards.
The source never changes those action choices. All three dynamic commands execute visualization; the recorder fixes that choice to the procedure containing only breed-color assignments.

All 800 paired model variants share their seed and differ exactly in the two setup literals.
The four pairings using only Rule M and EC therefore do not read the disputed values under the recorded driver.
The other twelve pairings do read them and remain the relevant parameter-sensitivity conditions.

This supports planning shared trajectory evidence for 200 unaffected paper-table inputs rather than redundant sensitivity simulations.
It does not change the frozen 1,600-row manifest, active reservations, audited coverage, or completion counts.
No unexecuted input is credited and no paired runtime sensitivity test is claimed here.
Historical seeds remain unknown regardless of parameter dependence.

The first audit incorrectly assumed no-visualization was empty and failed before writing output.
The corrected audit checks the actual two color assignments. The failed script and explanation are retained.
Two fresh audits, including one using the newly downloaded author model, produce identical JSON.

```sh
python replications/brearcliffe_2020/audit_parameter_dependencies.py AUTHOR_MODEL PREPARED NEW_OUTPUT
```
