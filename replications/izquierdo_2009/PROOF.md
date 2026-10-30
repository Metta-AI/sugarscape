# Constructive replication of the Sugarscape ergodicity argument

This argument concerns the formal, ideal-random model in the
[Sugarscape appendix](https://www.jasss.org/12/1/6/appendixB/EpsteinAxtell1996.html).
It does not assert that a particular finite-state pseudorandom generator produces an irreducible chain after its internal state is omitted.
The executable choice tapes demonstrate admissible paths under the formal model's independent uniform choices.

## Assumptions and state boundary

Observe states after replacement, including the initial state.
There are 250 agents on distinct cells of a 50×50 torus.
Capacity is fixed, integer-valued, and between zero and four; growback adds one up to capacity before movement.
Movement includes the current cell, maximizes sugar, and minimizes distance among maximizers.
Agents move in random sequential order, harvest, metabolize, and lose one unit of remaining lifetime.
An agent with nonpositive wealth or remaining life dies.
Replacement occurs after all movement; newborns begin at age zero.
Every vacant location and allowed integer attribute value has positive conditional probability.

The allowed newborn ranges are vision 1–6, metabolism 1–4, wealth 5–25, and lifetime 60–100.
These are the appendix's ranges and growback–movement–replacement ordering.
Remaining life represents maximum age minus current age; the chosen boundary makes each movement consume one lifetime unit.

Let D contain zero-capacity cells whose four immediate cardinal neighbors also have zero capacity.
The audit finds 305 such cells in Figure 2 and 306 in Figure 1.
The argument needs only |D| ≥ 250 and capacity at most four, so the raster discrepancy does not affect it.
The radius-three marker anomaly likewise cannot affect these conditions.

## Finite state space

An agent is born with wealth at most 25 and can gain at most three net units per step.
Its maximum lifetime is at most 100.
If its remaining life is l, its age is at most 100−l; therefore w + 3l ≤ 325.
At the observation boundary, surviving agents have positive integer wealth and remaining life.
Each landscape sugar value lies between zero and its fixed capacity.

Consequently the number of possible states is bounded above by

`5^2500 × choose(2500,250) × (6 × 4 × 325 × 100)^250`.

This bound deliberately overcounts impossible combinations but is finite.
Restrict S to states reachable from an allowed initial state, as in the paper.
Successors of reachable states remain in S, so S is closed.

## Stationary desert agents

A vision-one agent in D sees only zero sugar, including its current cell.
Its current cell uniquely minimizes distance, so it does not move and harvests zero.
No agent outside a particular zero-capacity cell can move into that cell:
if any visible sugar is positive, zero is not maximal; otherwise staying wins the distance tie.
Thus a desert agent's vacated site remains available during the remaining movement phase.

At every replacement, at most 249 cells are occupied.
Since |D| ≥ 250, at least one site in D is available.
Choosing that site, vision one, metabolism one, wealth five, and maximum age 99 is always an admissible positive-probability choice.
Such an agent remains stationary and starves after five movements, long before age death.

## Reach a pristine regenerating state

Begin at any i in S. For 104 steps, choose the desert replacement rule just described whenever an agent dies.
Every agent present in i dies within 100 movements, regardless of its wealth or movement history.
Every descendant is a stationary desert agent, and later replacements remain in D.
Therefore, after step 100 all agents are stationary in D with vision and metabolism one.

During the next four growbacks, no sugar is harvested anywhere.
Every cell reaches capacity because capacity is at most four.
At step 104, all agents have wealth r in {1,2,3,4,5} and remaining life 94+r.
The landscape is pristine and stays so while these desert agents remain.

## Synchronize mortality

Take step 104 as relative time zero. An agent with wealth r next dies at relative time r.
At each subsequent replacement, return it to the same vacant site, with vision and metabolism one and maximum age 99.
Newborn wealth five or six produces a lifespan of exactly five or six steps.

Choose interim lifespans using this complete table:

| Current wealth r | Interim lifespans after its next death | Sum | Time of final replacement |
| --- | --- | --- | --- |
| 1 | 5,5,5,5,5 | 25 | 26 |
| 2 | 6,6,6,6 | 24 | 26 |
| 3 | 5,6,6,6 | 23 | 26 |
| 4 | 5,5,6,6 | 22 | 26 |
| 5 | 5,5,5,6 | 21 | 26 |

All interim agents die by starvation before age can matter.
At relative time 26, give every newborn wealth five and maximum age 99.
Four movements later, every agent has wealth one and remaining life 95.
All 250 remain at distinct desert sites, and the landscape remains pristine.
This is an exterminating pristine state at absolute step 134.

On step 135, all 250 agents starve during movement without harvesting anything.
All cells are therefore unoccupied at the start of replacement.
Choose newborn positions and attributes to match any prescribed allowed initial state j₀.
The distinct target positions can be assigned in any replacement order, and every required choice has positive probability.
The landscape is still pristine, so the resulting complete state equals j₀.

## Irreducibility

For any i,j in S, the construction reaches any chosen initial state from i in 135 steps with positive probability.
By definition of S, some initial state j₀ reaches j along a finite positive-probability path.
Concatenate the construction from i to that j₀ with its path to j.
Thus every i reaches every j, proving irreducibility of S.

This is a general argument over S. The three saved executions illustrate it; they do not quantify over S by sampling.

## Aperiodicity

Choose a specific exterminating pristine state e with wealth one and remaining life 95 at 250 fixed desert sites.
It is reachable after four steps from an allowed initial state with wealth five and maximum age 99.
From e, all agents die on the next movement.
Replacing them at their old sites with wealth five and maximum age 99 returns to e after five total steps.
Replacing them with wealth six and maximum age 100 returns to e after six total steps.

Both return paths have positive probability and preserve the complete state, not just population or wealth totals.
The period of e divides gcd(5,6)=1, so e is aperiodic.
Irreducibility transfers that period to every state in S.

## Consequence and limit of the result

A finite irreducible aperiodic chain has one strictly positive stationary distribution, and its state distribution converges to it from every initial state.
Long-run occupation frequencies converge to the same distribution almost surely.
Mapping states to wealth distributions preserves both conclusions for that statistic.
This reproduces the appendix's structural conclusion.

Neither the proof nor the controlled paths bound the mixing time or justify convergence after a practical simulation horizon.
In particular, the existence of extremely improbable regeneration paths is not evidence that an ordinary finite simulation has mixed.
