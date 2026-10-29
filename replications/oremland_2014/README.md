# Oremland and Laubenbacher (2014)

**Completed qualified Sugarscape method reconstruction. Historical numerical agreement and a validated negative result are not established.**

[The method assessment](results/method-scope-assessment-2026-10-20) maps every Sugarscape method stage to completed native evidence and records reconstruction choices. It covers convergence, reduced-model rankings, genetic optimization, held-out transfer, and timing. The separate rabbits-and-grass example is outside this study.

[All eighteen searches](results/searches-complete-2026-10-20) complete 432,000 native evaluations with exact independent genetic-decision replay. [Held-out transfer](results/held-out-transfer-complete-2026-10-20) evaluates all 144 final policies across 28,800 full-model runs. Independent R arithmetic, archive verification, and figure review pass.

[The timing benchmark](results/cloud-timing-benchmark-2026-10-20) completes 18,639 native inputs. Published batch counts do not imply equal elapsed time on the new hardware. No historical timing-equivalence or global-optimality claim is made.

Earlier evidence directories retain their contemporaneous partial-study status. The assessment above supplies the current verdict without retroactively changing those records.

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
4. Remove agents with nonpositive wealth, following Appendix B prose. Algorithm 3 instead specifies negative wealth; see the paired diagnostic below.
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

[The 100-seed extension](https://github.com/Metta-AI/sugarscape/tree/0cbc06af5cc0448de517591b16385130cde2ec40/replications/oremland_2014/results/100-seed-controls-2026-10-18) completed all 1,600 runs in 228.50 seconds under a 1,800-second bound, one active JVM processor, and 512 MiB heap.
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

[The policy-indexing evidence](https://github.com/Metta-AI/sugarscape/tree/0cbc06af5cc0448de517591b16385130cde2ec40/replications/oremland_2014/results/policy-indexing-2026-10-18) includes a full 1,600-run uniform regression: all 81,600 observations are byte-identical to the earlier scalar-tax implementation.

One generated policy completed 400 full runs across 100 seeds, both clock phases, and both payment treatments.
The independent audit reconstructs all 500,936 tax events from agent attributes, patch capacity, cycle, and supplied rates.
It checks every payment, per-step event count, aggregate revenue, and 10,200 paired survivor states.
The native runs also verify a 50×50 torus through distance queries across both boundaries.

The runs visited 139 of 200 policy entries. The remaining 61 are explicitly listed in the audit; no event-level coverage is claimed for them.
The policy uses Python `random.Random(20261018)` with 200 draws of `randrange(4) / 4`; its actual rate vector and hash are retained.
This is a generated diagnostic policy, not one of the paper's original controls.
The public launcher repeats seed 1 exactly: 204 state observations and 4,846 tax events agree with the larger ensemble.

## Batch evaluation for optimization

[The batch evaluator](https://github.com/Metta-AI/sugarscape/tree/0cbc06af5cc0448de517591b16385130cde2ec40/replications/oremland_2014/results/batch-evaluator-2026-10-18) executes each full 50-step request without per-step observation and event exports.
All 400 final survivor states, populations, tax totals, and refund totals exactly match the previously audited heterogeneous workflows.
The final implementation took 17.12 seconds; the detailed-observation run took 68.31 seconds.
This comparison includes observation/export overhead and is not a reproduction of Table 2 timings.

`RunPolicyBatch.java` takes the model path, a JSON Lines request file, and a fresh JSON Lines output path.
Each request provides `id`, integer `seed`, `phase` (0 or 4), Boolean `clipped`, and 200 `policy` rates.
The retained manifest supplies the exact bounded Java command, compilation command, classpath, and source/runtime hashes.
`audit_policy_batch.py` validates every input and output line against the rich-workflow reference.

[The optimizer specification audit](results/optimizer-specification-2026-10-18) records the printed rules, missing choices, and dissertation attachment inventory.

## Full-size convergence reconstruction

[The completed ensemble](results/convergence-2026-10-18) contains 20,000 native runs and 59,400 prefix summaries.
All 40,000 request/result lines pass the audit; 2,400 independently recomputed means and sample standard deviations agree within 1e-10.
From 50 to 100 seeds, mean deaths change by at most 0.91 agents; death sample standard deviations change by up to 24.00% of their 100-seed values.
These are conditional measurements, not a numerical pass/fail criterion or a validated negative replication.

`prepare_convergence.py` freezes 100 heterogeneous policies before execution: 34 with mean rate 0.125, 33 with 0.25, and 33 with 0.375.
Each policy is uniform over quarter-rate vectors conditional on its exact total; integer dynamic-program counts are checked against inclusion-exclusion coefficients.
The original vectors, generating distribution, and group allocation are unavailable. These are declared reconstruction choices.

Each policy runs on 100 common seeds under both clock phases: 20,000 native 50-step runs.
Four disjoint workers have 512 MiB Java heaps and 1,800-second limits each.
The launcher freezes the model and its hash-checked landscape together, records runtime hashes, and refuses an existing execution directory.

```sh
python prepare_convergence.py /path/to/new-convergence
python run_convergence.py /path/to/java-home /path/to/NetLogo-5.3.1/app \
  /path/to/new-model/oremland.nlogo /path/to/new-convergence --timeout /path/to/timeout
python analyze_convergence.py /path/to/new-convergence /path/to/new-analysis
```

The auditor requires every request/result pair, seed, policy, phase, terminal status, and frozen input hash.
It exports all prefix means and both standard-deviation conventions, every policy's 50-versus-100 changes, and first-half/second-half differences with standard errors.
Mortality is measured as deaths among the original 200 agents. Clipped revenue is derived from recorded refunds; it is not another simulation.
Policies share seeds, so uncertainty summaries describe variation within each policy, not 100 independent policy replications.
No numerical pass threshold is inferred after seeing the results. Agreement remains conditional on the reconstructed controls and model.

## Reduced-model sensitivity experiments

[Native qualification](results/reduction-qualification-2026-10-18) covers all six widths and two map/vision-rounding conventions.
Twenty-four parameter cases produce 12 distinct model/landscape pairs.
All 96 complete workflows pass audits of 4,896 states, every initial patch, retained tax classes, and 30,976 tax events.
The full-size model and its earlier seed-1/2 detailed results remain exact.

Population scales with area; low vision maps to one cell in reduced models, while tax class remains based on original vision.
High vision uses the declared nearest/floor scaling, with the paper's radius-two assignment at widths 10 and 5.
The protocol lists each source-coordinate mapping and radius; these alternatives are not recovered author settings.

```sh
python build_reduced_models.py /path/to/qualified-full/oremland.nlogo /path/to/new-reductions
python run_ensemble.py /path/to/java-home /path/to/NetLogo-5.3.1/app \
  /path/to/new-reductions/20-pixel_centers-nearest/oremland.nlogo /path/to/new-run \
  --seeds 2 --seconds 120 --timeout /path/to/timeout policy /path/to/policy.txt
```

The archive includes the executed qualification launcher for all distinct models and the independent `audit_reductions.py` workflow.
[The frozen ranking experiments](results/ranking-protocol-2026-10-18) contain 2,538,400 reduced runs and 10,000 separate full-size runs.
Their inputs reuse the declared convergence policies; full-size comparison seeds are independent of the reference.

```sh
python prepare_rankings.py /path/to/audited-reductions /path/to/completed-convergence /path/to/new-rankings reduced
python run_rankings.py /path/to/java-home /path/to/NetLogo-5.3.1/app /path/to/new-rankings \
  --timeout /path/to/timeout --gzip /path/to/gzip
python prepare_rankings.py /path/to/audited-reductions /path/to/completed-convergence /path/to/new-full-rankings independent-full
```

Run the independent full-size batch after the reduced batch to preserve the four-worker limit.
The inputs and runtime pipeline are qualified. Completed ranking snapshots follow; original uncertainty bars remain outstanding.

## Audited ranking results and seed-design diagnostic

[The first ranking snapshot](results/ranking-prefix-2026-10-18) contains four complete model cases and 172,200 native runs.
All 344,400 input/output records pass coverage and provenance checks.
Every declared analysis convention is retained in 1,920 ranking rows, verified with 96,000 independent rank checks and exact rational kappa calculations.

At 40×40, the pooled full-budget death ranking under the first tax clock has linear kappa 0.933 and quadratic kappa 0.995.
The discrepancy from Figure 10 remains unresolved. Passing arithmetic checks does not establish fidelity of the reconstructed controls, model, or random-stream design.

```sh
python audit_ranking_model.py /path/to/rankings 40-pixel_centers-nearest /path/to/new-model-audit
python analyze_ranking_model.py /path/to/completed-convergence /path/to/new-model-audit /path/to/new-model-analysis
```

The auditor requires all four terminal shards for the selected model; it never silently analyzes a partial model.
The analyzer retains pooled and each fixed-mean-rate stratum, average and ordinal ties, linear and quadratic weights, and both integer budget roundings.
Raw integer objective sums determine ranks, avoiding floating-point tie artifacts from means.

[A post hoc independent-stream diagnostic](results/independent-streams-protocol-2026-10-18) addresses shared-seed coupling.
Its 37,600 frozen requests have unique seeds across all policies, phases, runs, and reference/comparison groups.
It compares independent 50×50 and 40×40 samples with its own independent full-size reference, preserving the other declared choices.
Its completed results and independent audit are reported below; no paper completion credit is claimed.

```sh
python prepare_independent_streams.py /path/to/qualified-reductions /path/to/completed-convergence /path/to/new-stream-diagnostic
```

Use `run_rankings.py` only after the preceding batch terminates to retain the four-worker limit.
The ordinary ranking auditor's consecutive-seed contract does not apply to this diagnostic; its unique-seed outputs require a separate audit.

## Historical provenance limits

The original author implementation, original 100 controls and random streams, and historical reduction and optimizer settings remain unavailable.
Completed convergence and ranking ensembles above evaluate explicit reconstruction choices; they do not establish the authors’ original controls or uncertainty bars.
Figure 11’s transfer method and Table 2’s batch-count timing method are now complete. Historical frontier identity and timing agreement remain unproven.

The full-size landscape is resolved. Reduced-grid conventions now have explicit, qualified sensitivity cases; their agreement with the original author implementation remains unproven.
Under the prose death rule, negative-payment clipping leaves paired survivor states unchanged. This does not extend to the algorithm’s negative-only death rule.
The clock-phase ambiguity can affect population and must be considered separately.

## Extinction failure and qualified recovery

The first small-grid ranking batch failed because an inherited GUI histogram evaluates maximum wealth on an empty population.
[The plot-free headless evaluator](results/headless-batch-evaluator-2026-10-18) removes GUI callbacks after loading the unchanged model.
All 400 full-size reference results remain exact; the original failed 5x5 input now completes all 50 steps with zero survivors.
The original evaluator reproduces the failure on that same input. Failed prefixes and logs are retained.

[All four 10x10 and 5x5 ensembles have completed under the qualified adapter](results/ranking-recovery-2026-10-18), preserving their original policies, seeds, maps, and horizons.
This repeats retained prefixes under the corrected evaluator rather than combining different evaluator versions within an ensemble.
The 2,110,000-run recovery has four workers, a one-hour global bound, and 30-minute shard bounds.
Its actual compressed-input pipeline passed all 400 reference comparisons before starting scientific work.
No failed or pending run receives completion credit.

[The ranking extension](results/ranking-extension-2026-10-18) independently audits another 256,200 reduced-model runs and 10,000 full-size runs.
Together with the earlier prefix, seven reduced models cover 428,400 audited runs.
The independent full-size comparison uses seeds 101–150 against reference seeds 1–50.
At full budget, pooled average-rank death concordance is 0.9481/0.9520 with linear weights for phases 0/4; quadratic weights give 0.9963/0.9972.
These are conditional reconstruction results. The original policy distribution, implementation, reduction choices, and published error bars remain unresolved.

## Independent random-stream diagnostic

[All 37,600 diagnostic runs](results/independent-streams-2026-10-18) pass audit with globally unique seeds and a separate 50x50 reference ensemble.
The auditor reconstructs the frozen seed assignment and validates 75,200 request/result lines.
For pooled average ranks with linear weights, independent-seed 40x40 mortality concordance is 0.8686/0.8695 for clock phases 0/4.
Within mean-tax-rate strata, it ranges from 0.5285 to 0.7844.
This post hoc sensitivity changes observed agreement but does not establish author conventions, reproduce uncertainty bars, or validate a negative replication.

## Death-boundary source conflict

Appendix B prose specifies death at zero sugar; Algorithm 3, line 19 specifies death only below zero.
All preceding ensembles follow the prose. Their conclusions remain conditional on that choice.
[The paired diagnostic](results/death-boundary-protocol-2026-10-18) preserves the original 37,600 independent-stream requests and changes only the comparison.
Its native qualification verifies 408 states and confirms surviving zero-sugar agents under the algorithm rule.
[All 37,600 paired runs now pass audit](results/death-boundary-complete-2026-10-18). Mortality changes in 37,223 pairs.
Algorithm-rule 40x40 pooled average-rank linear mortality concordance is 0.5854/0.5511, versus 0.8686/0.8695 under the prose rule.
The source ambiguity remains unresolved; neither sensitivity earns paper-completion or validated-negative credit.

## Native optimizer qualification

[The Algorithm 1 reconstruction](results/optimizer-qualification-2026-10-20) now executes policy search through the qualified native simulator.
Three bounded workflows evaluate 3,600 native simulations, each lasting 50 steps.
Independent replay reconstructs objectives, nondominated survivors, parent selection, crossover, mutation, and final evaluated frontiers from retained records.
A corrupted-offspring control must fail that replay. Restored runtime outputs match all 400 earlier qualification inputs, excluding elapsed time.

The paper leaves the population budget, generation budget, neighborhood definition, and some tournament semantics unspecified.
These workflows declare 12 candidates, two generations, 50 common seeds, and normalized Hamming neighborhoods.
They compare two dominance interpretations and exercise neighborhood selection with a separate radius sensitivity.
Mutation selects a different rate; odd population slots keep the first child. These are reconstruction choices, not recovered historical settings.
The final unevaluated children are retained separately from the reported evaluated frontier.

Qualification validates optimizer execution. The completed production campaign below adds reduced-to-full transfer; convergence to a global optimum is not established.

```sh
python run_optimizer.py /path/to/qualified-runtime-manifest.json /path/to/protocol.json /path/to/new-run
python audit_optimizer.py /path/to/new-run /path/to/new-audit.json
```

[The frozen transfer campaign](results/frontier-transfer-protocol-2026-10-20) now covers all six published grid widths and three optimizer seeds.
It completes 432,000 native evaluations, followed by full-model evaluation of every final frontier on 200 held-out seeds.
The budget, reduction conventions, comparisons, and execution bounds were fixed before inspecting results.
The completed campaign is included in the qualified method assessment above.

[The held-out transfer evaluator](results/transfer-qualification-2026-10-20) passes 1,800 native simulations and independent statistical replay.
A corrupted standard error is rejected. Fresh archive extraction reproduces the audit exactly.
Production transfer is gated on all 18 searches completing and passing audit; a bounded dependent watcher performs no retries.


The [replacement timing gate](https://github.com/Metta-AI/sugarscape/tree/0cbc06af5cc0448de517591b16385130cde2ec40/replications/oremland_2014/results/timing-recovery-gate-2026-10-20) additionally waits for the recovered trade ensemble.
The original passive watcher was stopped before benchmark admission; no native timing run was interrupted or duplicated.
Timing inputs, repetitions, warmups, and analysis remain unchanged.


[Held-out reporting qualification](results/transfer-report-qualification-2026-10-20) independently recomputes all objectives, standard errors, and dominance decisions from 1,800 native qualification runs.
The corrected plot is visually inspected and preserves every numeric row. These controls use only full-size models.
A separate watcher applies the same reporting path after all eighteen production searches and transfers pass audit.
The production transfer comparison and visual review now pass; the completed report is linked above.

## Archived raw outputs

[The immutable experiment archive](https://github.com/Metta-AI/sugarscape/tree/c1ad995a3e8c6dc7b91686e30fd772c4876cdd18/replications/oremland_2014/results) retains raw runs and verbose diagnostics. They remain unchanged in existing local checkouts; summaries, source inputs, and analysis code stay tracked. Restore any required input with `git show c1ad995a3e8c6dc7b91686e30fd772c4876cdd18:PATH > /absolute/output/path`, replacing `PATH` with its repository-relative path.

## Experiment evidence

Code, fixed study inputs, protocols, and written experiment summaries remain in this branch.
Generated run outputs, logs, checkpoints, and binary archives are excluded from the review diff.
The [immutable evidence archive](https://github.com/Metta-AI/sugarscape/tree/0cbc06af5cc0448de517591b16385130cde2ec40/replications/oremland_2014) preserves the pre-cleanup files.
To restore an input, run `git show 0cbc06af5cc0448de517591b16385130cde2ec40:REPOSITORY_PATH > OUTPUT_PATH` from this repository.
Use the documented runners to regenerate outputs; local output directories remain untracked.
