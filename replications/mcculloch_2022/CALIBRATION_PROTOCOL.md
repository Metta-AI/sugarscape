# Calibration protocol, declared before new calibration runs

Targets: section 4, Figures 5–6 of McCulloch et al. (2022).
`published_calibration.json` is a JSON transcription of the authors' released calibration artifacts,
with original source revision and file hashes. It contains ten history-matching waves and 10,000 posterior particles.
Only numeric NumPy scalar/dtype objects were allowed when decoding history-matching data;
the posterior pickle was checked to contain only primitive-data opcodes before conversion.

The independently implemented model has matched complete world states against the frozen source
for 16 experiments: seeds 0, 1, 42, 219 and parameters (1,1), (2,10), (4,7), (4,16), each for 100 steps.
This is an independent study-specific implementation in the fork, not a new mode of DTL's core engine.
It deliberately preserves the published code's initialization collisions and inactive grid occupants.

## History matching

Use the original 64-point parameter space: maximum metabolism 1–4 and maximum vision 1–16.
Each simulation lasts 30 steps. Observation is population 66.
Match `history_matching.py`: choose four evenly spaced input points (stride `ceil(n/4)`),
run 200 replicates at each, and average sample variances of absolute prediction errors.
The source uses that same averaged variance for both model discrepancy and ensemble uncertainty.
Total uncertainty is therefore twice that quantity. Observation variance is zero.
Evaluate each remaining point once; retain points with absolute error divided by uncertainty's square root below 3.
Stop when a wave removes no points. A 50-wave cap or empty retained space is a failure, not a successful calibration.

Preserve every seed and final population, uncertainty estimate, membership decision, and wave.
Report the observed wave count against 10, and the final parameter set against the authors' 15 points.
Do not force ten waves or restore eliminated points to match the published figure.

## Approximate Bayesian computation by rejection

Run two explicitly different experiments, each with 10,000 accepted particles:

1. **Full pipeline:** use the newly obtained history-matching space and final uncertainty.
2. **Conditional reproduction:** hold the authors' archived 15-point prior and variance 17.898567839195984 fixed.

Draw candidate parameters uniformly from the chosen prior. Accept when absolute population error is at most
the square root of total uncertainty. Retain rejected trials as well as accepted ones.
The original code initializes its attempt counter at one before its first attempt;
our counter reports actual simulator calls. The archived 32,270 attempts therefore represent 22,270 calls.

Report whether (4,7) is the modal point and the rank of (4,6), without changing that comparison after seeing results.
For the conditional reproduction, also compare the full categorical distribution using total variation distance.
Predeclared distribution-equivalence bound: a bootstrap 95% upper bound below 0.05,
using 5,000 independent multinomial resamples of both 10,000-particle samples, seed 271828.
This bounds aggregate probability-mass disagreement to five percentage points; it does not establish identical rankings.
Keep exact-ranking and distribution-equivalence verdicts separate.

These experiments cannot erase the already observed Figure 3 stabilization discrepancy.
They may support partial or negative replication, depending on results; do not label the entire paper positively replicated.
