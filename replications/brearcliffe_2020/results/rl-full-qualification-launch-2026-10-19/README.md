# Full-horizon learning-method qualification launch

Compare Q-Learning versus SARSA through all 20,000 ticks using both the corrected recorder and native BehaviorSpace.
The fixed prospective seed is 20261019, with released-code learning rate 0.9 and gamma 0.8.
The sequential dispatcher has a 1,200-second total bound and 600 seconds per execution, with a 1 GiB Java heap and 100 MiB output cap.
Session 72781 owns this local dispatcher. No full-ensemble run is included.

Require both executions to exit zero, exactly 20,001 observations, and exact equality of all 320,016 numeric fields.
This supplements the separate 1,000-tick checks across all sixteen pairings and the completed Rule M/EC full-horizon comparison.
Measured wall time is host-specific and includes recorder/runtime overhead; it is not a historical performance replication.
