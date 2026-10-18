# Oremland and Laubenbacher (2014)

**Incomplete reconstruction. No published aggregate result has been replicated.**

[Optimization of Agent-Based Models: Scaling Methods and Heuristic Algorithms](https://www.jasss.org/17/2/6.html), JASSS 17(2), 6, DOI 10.18564/jasss.2472.
The paper studies tax-policy ranking under model reduction and the transfer of optimized controls to the original Sugarscape model.

This study adapts NetLogo 5.3.1's bundled *Sugarscape 2 Constant Growback* model to the printed full-size algorithm.
It is an independent reconstruction, not recovered author code or a claim about the authors' NetLogo version.
The original model's Info tab retains Uri Wilensky's attribution and license in the generated model.
The retained 50×50 capacity file matches every published Figure 8 cell.

## Implemented behavior

The world has 2,500 patches, 200 initial agents, and no reproduction.
Initial sugar is uniform integer 5–25, metabolism 1–4, and vision 1–5.
The native NetLogo movement procedure selects unoccupied cardinal visible cells, including the current cell, by maximum sugar, nearest distance, and random ties.
Agents act sequentially in NetLogo's randomized `ask` order.

The adaptation changes the bundled model's growback-before-movement and immediate-death behavior to the printed order:

1. All agents move, harvest, and metabolize.
2. All patches regrow by one, up to capacity.
3. Collect scheduled taxes.
4. Remove agents with nonpositive wealth.
5. Advance time.

The model runs all 50 steps, including after extinction.
A policy has 200 entries, indexed by `20 * cycle + 5 * class + capacity`.
Cycles are 0–9; classes are LL, LH, HL, HH; capacities are 0–4.
Low vision is 1–3 and low metabolism is 1–2, following Appendix B.
The native model selects the current patch capacity and agent class at each tax step.
Literal payment is `min(wealth, ceiling(rate * wealth))`.
A separate clipping sensitivity changes only payment to its maximum with zero.
Two clock phases are explicit: phase 0 taxes after moves 1, 6, ..., 46; phase 4 taxes after moves 5, 10, ..., 50.
Neither phase is presented as the established author convention.

## First execution

Sixteen complete 50-step workflows use seed 1, four uniform rates `{0, .25, .5, .75}`, two clock phases, and both payment treatments.
All 408 paired survivor-state hashes match, across 816 observations.
Paired revenue differences equal recorded negative-wealth refunds, ranging from 0 to 7 sugar units.
The survivor state includes each agent's identity, position, wealth, metabolism, and vision, plus every patch's position, current sugar, and capacity.

[The 100-seed extension](results/100-seed-controls-2026-10-18) completed all 1,600 runs in 228.50 seconds under a 1,800-second bound, one active JVM processor, and 512 MiB heap.
All 40,800 paired survivor-state hashes match across 81,600 observations. Revenue differences equal recorded refunds and range from 0 to 12 sugar units.
Literal zero-rate taxation produces negative revenue in 193 of 200 runs; its range is −12 to 0. Clipped zero-rate revenue is zero throughout.
The seed-1 trajectory is byte-identical to the earlier qualification, and compressed evidence passes lossless readback.
It is a diagnostic ensemble, not the paper's 100 heterogeneous control schedules.
The separate auditor requires every seed, condition, and timestep, exact paired state hashes, monotone population, and the analytical revenue identity.

## Reproduce

The retained NetLogo 5.3.1 distribution and Java 11 are required.
Use fresh output directories; source, model, runtime, commands, trajectories, and terminal status are retained.
The launcher uses the distribution's explicit application classpath. A wildcard also loads unrelated application jars and failed workspace construction during qualification.
The distribution declares an absent `hamcrest-core-1.1.jar`; the manifest records that absence separately from hashes of present jars.
Compilation and native execution still fail normally on missing required dependencies.
NetLogo 5.3.1 exposes job-manager shutdown through its concrete `JobManager`; the harness uses that version's lifecycle API.

```sh
python build_model.py \
  '/path/to/NetLogo-5.3.1/app/models/Sample Models/Social Science/Sugarscape/Sugarscape 2 Constant Growback.nlogo' \
  /path/to/verified/sugar-map.txt /path/to/new-model
python run_ensemble.py /path/to/java-home /path/to/NetLogo-5.3.1/app \
  /path/to/new-model/oremland.nlogo /path/to/new-run \
  --seeds 100 --seconds 1800 --timeout /path/to/timeout uniform
python audit_ensemble.py /path/to/new-run/runs/trajectory.csv 100 /path/to/new-run/audit.json
```

## Heterogeneous-policy execution

`RunPolicy.java` executes a supplied 200-line rate file and records every native tax event.
The launcher selects it with the `policy` subcommand:

```sh
python run_ensemble.py /path/to/java-home /path/to/NetLogo-5.3.1/app \
  /path/to/new-model/oremland.nlogo /path/to/new-policy-run \
  --seeds 100 --seconds 1800 --timeout /path/to/timeout policy /path/to/policy.txt
python audit_policy.py /path/to/new-policy-run 100 /path/to/new-policy-run/audit.json
```

[The policy-indexing evidence](results/policy-indexing-2026-10-18) includes a full 1,600-run uniform regression: all 81,600 observations are byte-identical to the earlier scalar-tax implementation.

One generated policy completed 400 full runs across 100 seeds, both clock phases, and both payment treatments.
The independent audit reconstructs all 500,936 tax events from agent attributes, patch capacity, cycle, and supplied rates.
It checks every payment, per-step event count, aggregate revenue, and 10,200 paired survivor states.
The native runs also verify a 50×50 torus through distance queries across both boundaries.

The runs visited 139 of 200 policy entries. The remaining 61 are explicitly listed in the audit; no event-level coverage is claimed for them.
The policy uses Python `random.Random(20261018)` with 200 draws of `randrange(4) / 4`; its actual rate vector and hash are retained.
This is a generated diagnostic policy, not one of the paper's original controls.
The public launcher repeats seed 1 exactly: 204 state observations and 4,846 tax events agree with the larger ensemble.

## Remaining paper scope

The original author implementation, original 100 controls and random streams, model-reduction conventions, and optimizer implementation remain unavailable.
Uniform-rate controls do not establish Figure 9's convergence claim, Figure 10's policy-ranking agreement, Figure 11's Pareto-frontier transfer, or Table 2's historical timings.
These figures and the optimization experiments remain required; no paper-completion credit is assigned.

The full-size landscape is resolved, but smaller-grid nearest-neighbor coordinates, population scaling, and vision/class mapping still need explicit treatment.
Negative-payment clipping cannot explain a population mismatch when it is the only changed rule and random draws remain coupled.
The clock-phase ambiguity can affect population and must be considered separately.
