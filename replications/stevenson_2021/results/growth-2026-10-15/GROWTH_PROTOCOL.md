# Fixed-society growth diagnostic

Declared before running the dense 100-seed ensembles. This is a specification-based
diagnostic, not a claim to recover the author's unspecified fitting procedure.

Run both original fixed scenarios, infertility/birth cost 85/0 and 10/40, for
3,000 cycles using seeds 1–100. Record every cycle with the unchanged baseline
birth threshold. These are the same seed identities as the long ensembles;
their trajectories are correlated and must not be counted as additional independent
replicates of steady-state outcomes. Keep every trajectory, extinction, and failure.

Appendix B's equation 5 specifies continuous logistic growth. Fit
`N(t) = K * expit(r * (t - midpoint))` by unweighted least squares to all
observations at cycles 1–3000, separately for each surviving complete trajectory.
The horizon is our declared measurement choice, not a recovered author setting.
Do not fit the delayed equation 6 or infer r from steady-state mean age.

Use SciPy least_squares, positive log-parameterization of K and r, and an unbounded
midpoint. Initialize K at 833.3333333333334, r at each of 0.005, 0.02, 0.05,
and midpoint at the first observed cycle reaching population 400 (or 1500 if
never reached). Select the converged finite solution with lowest squared error;
retain every optimization attempt, termination code, fitted parameters, and error.
An extinction or absence of a converged fit remains a reported failure and is
never silently excluded from an all-100 claim. Inspect residuals and report
boundary/implausible fits rather than changing settings after observing them.

Report seed-level r, K, midpoint, root mean squared residual, and across-seed
mean, standard deviation, and 95% Student-t interval. The paper reports r=0.018
and r=0.032. Compare absolute and relative differences without manufacturing an
acceptance threshold from outcomes. The meaning of the paper's percentage
uncertainties remains unresolved. Parameter intervals are descriptive across
seeds, not proof that the model or fitting protocol matches the author.

Before accepting outputs, validate hashes, exact seed order, complete timestamps,
finite metrics, zero conservation error, population accounting, and exact agreement
with the existing same-seed ensemble at all shared recorded cycles through 3000.
Any mismatch is an implementation/provenance issue to investigate first.
