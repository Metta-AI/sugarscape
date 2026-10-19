# Rule M claim-level contrasts

The manuscript's page 14 describes higher Rule M wealth, vision, and metabolism against the three learning methods.
This analysis covers every relevant released-code matchup in both breed orientations: six complete cohorts, 300 already-audited inputs.
It adds no simulation coverage and does not substitute for the unfinished paper-table interpretation.

At tick 20,000, Rule M minus its opponent is positive for all 18 metric/matchup contrasts.
Every corresponding 95% pointwise whole-run bootstrap interval lies above zero.
Higher metabolism means greater sugar consumption, so that positive contrast represents a resource cost.
The intervals preserve within-run pairing and use each cohort's existing 20,000 resampling draws.
They are not simultaneous intervals or uncertainty estimates for the authors' unavailable runs.

| Pairing (group A / group B) | Endpoint wealth difference | Pointwise 95% interval | Later ticks with positive mean difference |
| --- | ---: | ---: | ---: |
| rule-m-ec | 175.474 | 156.031 to 193.253 | 18,106/20,000 |
| rule-m-q | 202.999 | 196.793 to 209.171 | 20,000/20,000 |
| rule-m-sarsa | 207.226 | 200.017 to 214.454 | 20,000/20,000 |
| ec-rule-m | 195.278 | 179.165 to 209.526 | 18,042/20,000 |
| q-rule-m | 209.916 | 203.576 to 216.145 | 20,000/20,000 |
| sarsa-rule-m | 208.197 | 200.803 to 215.708 | 20,000/20,000 |

The full-curve calculation retains every tick from 1 through 20,000; initial-state differences are reported separately.
Rule M's wealth advantage over Q-learning and SARSA holds across all those ensemble-mean ticks.
EC leads early: Rule M/EC has 1,894 negative ticks between ticks 5 and 1,898; EC/Rule M has 1,958 between ticks 1 and 1,964.
Thus the endpoint finding should not be described as a wealth advantage at every time point.
This transient does not by itself establish a paper-negative result.

Python reopened and hashed all 300 native trajectories against both the cumulative audit and cohort summaries.
Independent R reopened those same raw trajectories and checked all 1,800 endpoint values with zero difference, including breed and metric mapping.
R independently recomputed 234 contrast, bootstrap, and curve-sign summary values; maximum scaled error was 3.553e-15.
The protocol, raw endpoint matrix, trajectory/source hashes, Python analysis, and R verifier are retained here.
This claim-level analysis was specified after cohort plots were available; it is not preregistered confirmatory inference.

The released-code endpoint results support the stated directional comparisons.
Whole-paper assessment still requires the remaining pairings, both parameter interpretations, all figure comparisons, and investigation of source discrepancies.
