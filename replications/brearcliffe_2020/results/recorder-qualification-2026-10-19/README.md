# Native recorder qualification

The first full pilot finished with 20,001 observations and exit code 0, but its recorder altered the simulation's random stream.
A native BehaviorSpace comparison at ticks 0–100 matched only 470 of 1,616 population/metric values; differences began at tick 1.
The failed full pilot, its original recorder, and the comparison remain retained.

NetLogo's agentset reporters randomize traversal. The recorder evaluated them on the model's random stream.
Wrapping only measurement in `with-local-randomness` restores the random state afterward, as documented in NetLogo 6.1.1's bundled dictionary.
The corrected recorder matches all 1,616 native BehaviorSpace values exactly, with identical initial model, seed, and parameters.
No behavioral source or parameters changed to obtain agreement.

An initial audit also incorrectly assumed replacement keeps exactly 400 agents at every observed tick.
The actual model can lose agents during a tick before replacements restore the count; the accounting audit now records observed population ranges.
This accounting correction does not alter the simulation.

Two separately bounded full-extent runs are now active: corrected recorder and native BehaviorSpace.
Each uses the same seed and 20,000-tick extent, 600-second timeout, 1 GiB Java heap, and 50 MiB output cap.
The complete comparison remains pending; short-run agreement does not establish it.
