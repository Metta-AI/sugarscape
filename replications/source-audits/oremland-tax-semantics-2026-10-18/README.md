# Tax-before-death semantics

The journal's [Algorithm 3](https://www.jasss.org/17/2/6/algorithm3.png) and the dissertation's Algorithm 6 agree on the relevant order and formula.
Algorithm 6 appears on PDF page 104, printed page 90, in the [2014 dissertation](https://vtechworks.lib.vt.edu/handle/10919/25138).
Both sources move, harvest, and metabolize all agents; regrow patches; collect scheduled taxes; remove nonpositive-wealth agents; then advance time.

Let `w` be wealth after metabolism and `r` the scheduled rate in `{0, 0.25, 0.5, 0.75}`.
The literal payment is `p = min(w, ceil(r*w))`.
For negative integer `w`, `ceil(r*w) >= w`, hence `p = w < 0` regardless of the rate.
For example, `w = -1` and `r = 0` produce payment `-1`, followed by wealth `0` and death.
The formula therefore records a negative payment even under a zero-rate schedule if an agent reaches that tax step with negative wealth.
This is a consequence of the printed algorithm, not evidence that the authors' executable behaves this way.

## Consequence for a fixed control schedule

Consider a second implementation that changes only payment to `max(0, min(w, ceil(r*w)))`.
It preserves the published move/regrowth/tax/death order and uses the same random stream and scheduled rates.

- At nonnegative wealth, both payments are identical.
- At negative wealth, literal taxation sets wealth to zero; clipping leaves wealth negative.
- Both cases remove that agent in the same subsequent death phase.
- Surviving agents, patch states, and occupancy after the death phase therefore agree exactly.

Induction over steps gives identical surviving-agent trajectories and death counts for every fixed control schedule.
This statement assumes the payment change introduces no random draws, reorders no agents, and changes no other rule.
It does not cover policies that adapt to collected revenue or an optimizer that selects a different control because its revenue objective changed.
It also does not cover moving the death phase earlier: earlier removal can change which cells other agents can occupy.

The revenue difference is exactly the sum of the absolute negative wealths on taxed death steps.
Under Appendix B's integer rules, an agent starts a step with wealth at least 1, harvests a nonnegative amount, and metabolizes at most 4.
Negative post-metabolism wealth is therefore one of `-1`, `-2`, or `-3`.
With 200 initial agents and no reproduction, each agent can contribute at most once.
Thus clipped revenue minus literal revenue lies between 0 and 600 over a complete 50-step run.
This is an upper bound, not a measured effect size; the realized difference depends on the schedule and trajectory.

## Implementation and interpretation

A literal printed-algorithm reconstruction should retain negative payments and report them explicitly.
A clipping sensitivity run should preserve all other rules and report the paired revenue difference.
If that isolated change produces different death counts or survivor states, the implementation or random-stream coupling is wrong.
A revenue mismatch smaller than 600 cannot by itself identify the authors' treatment of negative wealth.

The initial clock value and first tax cycle remain unresolved.
A zero-based 50-step loop taxes at clock values 0, 5, ..., 45; taxation after every fifth completed move taxes after moves 5, 10, ..., 50.
Both have ten tax cycles but apply them to different states.
The two alternatives need separate declared experiments; choosing whichever matches a plotted result would not establish historical implementation fidelity.

No model run, published aggregate reproduction, or negative replication is claimed here.
The original author executable, original control schedules, and reduced-grid conventions are still missing.

Figure attribution: Matthew Oremland and Reinhard Laubenbacher, *Optimization of Agent-Based Models: Scaling Methods and Heuristic Algorithms*, JASSS 17(2), 6 (2014), Algorithm 3, DOI 10.18564/jasss.2472.
