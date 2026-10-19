# Homogeneous-method breed endpoint contrasts

All four released-code homogeneous pairings are complete: 50 seeds each, 200 runs, and 4,000,200 observations already in the audited inventory.
This diagnostic adds no simulation inputs or completed-study credit.

The paper discusses generally similar diagonal outcomes, with EC/EC breed A the same or slightly better (page 14).
It specifies no numerical equivalence margin.
All 28 paired endpoint intervals include zero. This does not establish breed equivalence or the claimed EC breed advantage.
The EC/EC results exactly retain the earlier breed-contrast diagnostic; no labels or seeds were changed.
Positive A-minus-B differences do not uniformly indicate better outcomes, particularly for metabolism and death counts.

| Pairing | Metric | A minus B mean | Pointwise 95% paired bootstrap interval |
| --- | --- | ---: | --- |
| rule-m-rule-m | sugar | -3.27378 | [-7.10483, 0.479078] |
| rule-m-rule-m | vision | -0.00646153 | [-0.0398737, 0.0287885] |
| rule-m-rule-m | metabolism | 0.00736491 | [-0.00512018, 0.0198153] |
| rule-m-rule-m | combat | 17.62 | [-2.04, 37.8805] |
| rule-m-rule-m | starvation | 18.44 | [-122.52, 157.721] |
| rule-m-rule-m | age | -6.15216 | [-12.6495, 0.222044] |
| rule-m-rule-m | max_age | -12.66 | [-335.224, 313.206] |
| ec-ec | sugar | -530.202 | [-1569.25, 527.08] |
| ec-ec | vision | -0.2893 | [-0.828351, 0.255404] |
| ec-ec | metabolism | 0 | [0, 0] |
| ec-ec | combat | 1748.94 | [-1791.8, 5227.35] |
| ec-ec | starvation | -0.46 | [-4.42, 3.46] |
| ec-ec | age | -570.146 | [-1700.52, 579.407] |
| ec-ec | max_age | -2082.78 | [-5809.55, 1717.58] |
| q-q | sugar | -32.9179 | [-72.8235, 8.26614] |
| q-q | vision | 0.00815 | [-0.02365, 0.0401012] |
| q-q | metabolism | 0.0017 | [-0.0005, 0.004] |
| q-q | combat | 6.2 | [-1.48, 13.88] |
| q-q | starvation | 27 | [-22.0605, 78.141] |
| q-q | age | -23.3464 | [-90.7757, 46.1246] |
| q-q | max_age | -170.48 | [-1454.59, 1116.23] |
| released-sarsa-sarsa | sugar | -5.89745 | [-73.5332, 62.9165] |
| released-sarsa-sarsa | vision | -0.00295 | [-0.03435, 0.0288] |
| released-sarsa-sarsa | metabolism | -0.002 | [-0.0042, 5e-05] |
| released-sarsa-sarsa | combat | 0.56 | [-6.78, 7.72] |
| released-sarsa-sarsa | starvation | 33.76 | [-6.7, 74.8005] |
| released-sarsa-sarsa | age | -8.85415 | [-155.695, 139.307] |
| released-sarsa-sarsa | max_age | 0 | [0, 0] |

The analysis was selected after viewing the paper and cohort results. It retains all 50 seeds and existing 20,000 whole-run resamples per cohort.
Intervals preserve within-run breed dependence; they are pointwise and exclude uncertainty in the paper's historical sample.
The analysis cannot identify activation-order effects or validate historical plotting provenance.

Python reopens and hashes all 200 full raw trajectories against the canonical 1,152-input audit and each frozen cohort summary.
Independent R reopens the same trajectories and checks 2,800 endpoint values, then recomputes 252 summary quantities.
Raw endpoints agree exactly; maximum scaled summary error is 2.86e-15.

An initial whole-curve diagnostic failed strict sign-count agreement near floating-point equality.
Its scripts, outputs, and numerical diagnostic are retained in `sugarscape-replication-evidence/brearcliffe-homogeneous-contrast-diagnostic-001`.
The published comparison is endpoint-only; no equality threshold was tuned to produce agreement.
This arithmetic verification does not independently execute the simulation or validate the bootstrap random-number generator.

Reproduce with Python 3.11 and NumPy 1.26.4: `python analyze.py`.
Then run R 4.6.1 with jsonlite: `Rscript verify.R <this-directory>`.
Scripts reference retained local raw evidence; source hashes are recorded in `contrasts.json`.
