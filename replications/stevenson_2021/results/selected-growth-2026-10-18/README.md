# Growth rates of selected reproductive traits

Both 100-seed ensembles complete 3,000 cycles, yielding 600,000 native observations with exact timestamps, population accounting, and zero resource-conservation error.
Each begins with one homogeneous founder carrying the selected traits: infertility/birthcost10/0 or1/0.
This measures growth of the selected traits, not growth during the 830-founder selection transient.

The fitting convention was frozen before execution and matches the previous fixed-society diagnostic: continuous logistic growth, all cycles1–3000, unweighted least squares, three fixed initial rates, and retained optimization attempts.
All 200 trajectories produce converged finite fits. All 600 residual sums independently reconstruct within 1.8e-14 relative difference using Python math functions and native populations.

| Traits | Mean fitted rate | Across-seed SD | Paper Table 1 rate | Mean root-mean-square residual, agents |
| --- | ---: | ---: | ---: | ---: |
| 10/0 | 0.238694 | 0.010038 | 0.170 | 34.73 |
| 1/0 | 0.972369 | 0.015263 | 1.542 | 464.14 |

These results do not reproduce the printed rates under this declared fitting convention.
The author's fitting protocol remains unknown. Large residuals in the chaotic-parameter case also warn against treating a converged logistic fit as a faithful dynamical model.
The discrepancy remains unresolved; it is not a validated negative replication or new completion credit.
No fit window, initialization, or acceptance threshold was changed after observing outcomes.
Across-seed intervals describe this reconstruction only; they do not interpret the paper's percentage uncertainties.

The archive retains all native trajectories and individual observations, commands, source, input protocol, hashes, and completed-run ledger.
The qualified binary's SHA-256 matches the homogeneous controls retained in the evolutionary evidence.
Every archived member passes hash readback. The exact analyzer source and all optimizer attempts are retained separately.
