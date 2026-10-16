# Carrella model integration requirements

The pinned author model is not equivalent to this fork's existing trade/reproduction configuration.
These differences must be preserved in a study-specific implementation before claiming an independent simulator replication.
Source: `CarrKnight/nofreelunch` commit `0400f750063215d06659a203f777b21da2e99231`, `data/sugarscape/Sugarscape trade.nlogo`.
The comparison below uses this branch's root `agent.py` and `sugarscape.py`.

| Behavior | Author implementation | Existing fork behavior |
| --- | --- | --- |
| Activation | Separate shuffled phases: growback; movement, harvest, metabolism, death; trade; reproduction; utility refresh | Each agent performs movement, harvest, metabolism, trade, reproduction, and other actions in one turn |
| Reproduction | One-parent cloning when cached utility exceeds the threshold; child placed in an empty radius-three patch | Sex/fertility compatibility with a neighboring mate; child endowments and placement depend on both parents |
| Inheritance | Parent halves both holdings; child inherits those halves and traits | Parent-specific endowment contributions and trait inheritance |
| Mutation | Independent probability for each metabolism and vision; +/-1; metabolism lower bound one; vision upper bound six | No equivalent three-trait cloning/mutation path |
| Trade neighborhood | Moore neighbors; each caller visits each neighboring turtle once in that invocation | Configured neighbors with repeated transactions until trade conditions fail |
| Trade acceptance | Both potential utilities at least cached utilities; no explicit marginal-rate crossing check | Welfare or marginal-rate improvement plus non-crossing and resource-survival checks |
| Reproduction utility | Cached value from last refresh or successful trade; harvest does not refresh it | Fertility uses current resources and other constraints |
| Inequality | Unrounded Gini of Cobb–Douglas utility | Three-decimal Gini of sugar plus spice |
| Price observation | Retains previous mean when current transaction list is empty | Existing logging follows its own per-agent price aggregation |

Cobb–Douglas exponents are each resource's metabolism divided by total metabolism.
Utility is zero if either holding is nonpositive.
Movement maximizes utility after harvesting candidate resources, breaks ties by distance, then randomly among equal-distance winners.
The native map uses two concentric, integer-capacity peaks per resource with radii 4, 8, 12, and 16.
Existing map and movement configuration must be compared cell-by-cell before reuse.
The author trade procedure also retains potential-holding variables across calls; equal marginal rates do not assign new potentials.
That edge case requires a native scenario before deciding its independent implementation.

## Verified native phase behavior

`SemanticsProbe.java MODEL NEW_OUTPUT` runs complete native ticks through the unmodified model.
Both controlled worlds start with one agent holding ten units of each resource, metabolism one per resource, and no landscape resources.
Reproduction threshold is five, mutation is disabled, and trade is enabled with no initial partner.
The only difference between worlds is cached utility: one versus ten.

After one tick, both have nine units of each resource in total.
The first world retains one agent; the second has two, demonstrating that reproduction reads cached utility rather than current holdings.
Both retain an initialized mean price of seven despite zero transactions, demonstrating carry-forward price observations.
These are controlled whole-model semantics checks, not ordinary sampled trajectories or paper-level replication results.
The archived 5,000-input replay remains the source for the original parameter distribution.

## Implementation boundary

Use an explicit study-owned model and scheduler, preserving existing fork behavior for its other studies.
Do not silently approximate asexual cloning with the fork's sexual reproduction or change cached utility to a freshly computed value.
A correct independent implementation must first pass native phase scenarios and map checks, then the declared ensemble/statistics comparison.
Matching native stochastic trajectories additionally requires matching NetLogo's random generator and activation/random-draw conventions.
Different-runtime seed labels alone do not establish paired random trajectories.
