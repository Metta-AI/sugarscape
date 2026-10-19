# Q-learning versus SARSA wealth direction

The paper's discussion describes a small Q-learning wealth advantage when the two reinforcement-learning methods compete (PDF page 14).
This post hoc check measures Q-learning minus SARSA sugar at tick 20,000 and the sign of the mean difference over the complete trajectory.
Both released-code orientations contain 50 complete runs. Paper-table orientations remain outstanding; these results do not identify historical settings.

| Orientation | Q-learning mean | SARSA mean | Paired difference | Pointwise 95% bootstrap interval |
| --- | ---: | ---: | ---: | --- |
| Q-learning / SARSA | 2,590.1212 | 1,662.64705 | 927.47415 | 870.430315–987.41614125 |
| SARSA / Q-learning | 2,572.57115 | 1,664.249 | 908.32215 | 848.07358875–968.1167675 |

All 50 endpoint differences are positive in each orientation. Both intervals are strictly above zero, supporting the endpoint direction.
This does not validate the qualitative word “small,” causal attribution to off-policy learning, or an advantage at every timestep.
The Q/SARSA mean difference is negative on 86 early ticks, from tick 4 through 92; SARSA/Q has four negative ticks between 15 and 20.
All other post-initial ticks have positive mean differences; there are no exact ties.

The analysis reopens and hashes all 100 source trajectories against the cumulative audit and cohort summaries.
It uses the existing 20,000 whole-run bootstrap resamples, preserving covariance between competing groups within each run.
Independent R reopens those same raw files: all 200 endpoint values agree exactly, and 30 summary checks have maximum scaled error 1.777e-15.
The intervals are pointwise, with no simultaneous-coverage claim. The protocol was written after related cohort results were available.
No new simulation coverage or completed-paper credit is added.
