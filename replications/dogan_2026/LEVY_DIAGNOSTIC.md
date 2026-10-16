# Displacement-levy accounting diagnostic

The original model is pinned at `0b6a3df470388f60535d8ffb67c34a7f9fa0059a`.
No live native or bundled source is changed by this diagnostic.

In `_apply_displacement`, let the nominal levy be L and new-owner wealth be W.
The original code deducts `W * min(1, L/W)` from the owner but credits
`L * min(1, L/W)` to the treasury and reported tax revenue.
For L<W this credits L²/W instead of L; for L>W it credits L instead of W.
The manuscript's equation 4 specifies a transfer of min(L,W).
These formulas disagree except when L=W (or the levy is zero).

`audit_levy_events.py ENGINE NEW_OUTPUT` observes the original displacement
function at pinned source lines. It runs fast automation, D=50, seed zero for
300 steps, and independently repeats the same model without the observer.
The full per-step native outputs must be byte-identical before accepting event
observations. It records owner deductions, treasury credits, and tax reporting.
This is an execution diagnostic; it does not estimate corrected policy outcomes.

The proposed `conserving-levy.patch` credits the amount actually charged,
min(L,W), to both treasury and revenue. It is a separate research variant,
not a replacement for the author's released source or replication baseline.

Before examining corrected outcomes, declare the following comparison:

- Replay the original 75-run D sweep, D in {10,25,50,100,200}, three original
  automation speeds, seeds 0–4, horizon 300, and native seed-42 calibration.
- Apply only the retained accounting patch to an isolated source variant.
- Verify event-level deduction/credit equality and native/observer trajectory
  parity on the corrected fast D=50 seed-zero run.
- Compare all paired seed outputs with the complete original 75-run sweep.
  Retain every seed and all raw outputs; do not filter outcomes.
- Report changes in Gini, mortality, revenue, redistribution, population,
  working-human share, and means at each D/speed. Compare D=50 original results
  to canonical levy results to check protocol equivalence first.
- Check manuscript sensitivity claims separately: Gini coefficient of variation
  across five D-level means below 0.04; maximum/minimum mortality means within
  5%; equal working counts across D for each paired seed; realized levy share
  below 3% at D=200. These operational interpretations must be explicit because
  the prose does not fully specify its aggregations.

Neither a conservation defect nor successful reproduction of deposited data
alone proves or refutes the paper's central policy ranking conclusions.
Quantifying the corrected variant is required before interpreting its effect.
