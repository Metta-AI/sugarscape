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
Literal payment is `min(wealth, ceiling(rate * wealth))`.
A separate clipping sensitivity changes only payment to its maximum with zero.
Two clock phases are explicit: phase 0 taxes after moves 1, 6, ..., 46; phase 4 taxes after moves 5, 10, ..., 50.
Neither phase is presented as the established author convention.

## First execution

Sixteen complete 50-step workflows use seed 1, four uniform rates `{0, .25, .5, .75}`, two clock phases, and both payment treatments.
All 408 paired survivor-state hashes match, across 816 observations.
Paired revenue differences equal recorded negative-wealth refunds, ranging from 0 to 7 sugar units.
The survivor state includes each agent's identity, position, wealth, metabolism, and vision, plus every patch's position, current sugar, and capacity.

The 100-seed extension uses the same full workflows and is bounded to 1,800 seconds, one active JVM processor, and 512 MiB heap.
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
  --seeds 100 --seconds 1800 --timeout /path/to/timeout
python audit_ensemble.py /path/to/new-run/runs/trajectory.csv 100 /path/to/new-run/audit.json
```

## Remaining paper scope

The original author implementation, original 100 controls and random streams, model-reduction conventions, and optimizer implementation remain unavailable.
Uniform-rate controls do not establish Figure 9's convergence claim, Figure 10's policy-ranking agreement, Figure 11's Pareto-frontier transfer, or Table 2's historical timings.
These figures and the optimization experiments remain required; no paper-completion credit is assigned.

The full-size landscape is resolved, but smaller-grid nearest-neighbor coordinates, population scaling, and vision/class mapping still need explicit treatment.
Negative-payment clipping cannot explain a population mismatch when it is the only changed rule and random draws remain coupled.
The clock-phase ambiguity can affect population and must be considered separately.
