# Elite-age and founder-history observation protocol

This extends measurement coverage for Figures 1 and 2 without changing model rules.
The author seed and exact elite tie/rounding convention remain unknown.

- Both fixed scenarios, seeds 1–100, 50,000 cycles, recording every 100 cycles plus cycle one.
- Low fertility uses f=85 and cost=0; birth cost uses f=10 and cost=40.
- Elite means the wealthiest ceil(population/10) living agents. Equal wealth is ordered by birth identifier.
- Record elite count, total wealth, and mean age, plus each living member of the first thirty births (initial agent has identifier zero).
- Figure 2's birth-cost comparison uses the first twelve identifiers; retaining thirty does not change the experiment.
- No death interpolation or absent-founder zero imputation. Missing later records indicate absence from the living founder subset.
- Each aggregate trajectory must exactly match the corresponding prefix of the already completed 100,000-cycle same-seed ensemble.
- Retain all runs, failures, source/binary/protocol hashes, raw trajectory and observation hashes, and native exits.
- Compare Figure 1 curves descriptively against the fresh 100-seed distributions at shared times. Preserve vector-coordinate and unknown-seed limits.
- Do not treat an approximate plotted trajectory as an exact-seed oracle or infer acceptance thresholds from these new runs.

System-level measurement verification precedes the ensemble: both seed-zero 3,000-cycle dense trajectories match the original binary byte-for-byte.
Independent sorting of the complete early founder populations reconstructs elite output in 598 cycles across the two scenarios.
These checks establish observation parity, not author-model equivalence.
