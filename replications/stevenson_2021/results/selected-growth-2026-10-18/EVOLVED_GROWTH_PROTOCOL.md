# Growth of the selected reproductive traits

This diagnostic extends the existing logistic-fitting convention to the selected traits in Table 1: infertility/birthcost 10/0 and 1/0.
Each population starts from one homogeneous founder; it measures growth of the selected traits, not the 830-founder selection transient.
Use the unchanged fixed simulator, seeds1–100, 3,000 cycles and every-cycle observations, retaining extinction and failures.
The native models are qualified by the inherited-trait homogeneous parity controls.

Fit the same continuous logistic equation to cycles1–3000 with unweighted least squares, log-positive K and r, free midpoint, K initialization833.3333333333334, and three initial rates .005/.02/.05.
Initialize midpoint at first population400 crossing, otherwise1500; keep all attempts and select the converged finite minimum-SSE fit.
The paper targets are r=.170 and r=1.542. Its fitting window and protocol remain unknown.
Do not change initialization, windows or acceptance thresholds after seeing results.
Report failures and residual error, and do not interpret successful optimizer termination as validation of logistic dynamics, especially in the high-variability case.
This extends required growth-rate coverage but cannot establish historical model equivalence or complete the paper.
