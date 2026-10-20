# Algorithm 1 native workflow qualification

Three complete optimizer workflows exercise the paper’s genetic search using the qualified, unchanged native full-size model.
This is method implementation evidence, not optimization convergence or Figure 11 replication.

Each workflow uses 12 candidates, two evaluated generations, 50 common simulator seeds, and optimizer seed 20261020.
Tax phase is 0; payments follow the unclipped formula; death follows the prose’s nonpositive rule.
Each candidate has 200 rate indices in `{0,1,2,3}`, mapped to rates `{0,.25,.5,.75}`.

| Workflow | Tournament interpretation | Hamming radius | Native runs | Dominance / neighborhood / random selections |
| --- | --- | --- | --- | --- |
| run | Candidate dominates every comparison member | .25 | 1200 | 1 / 0 / 21 |
| nondominated-run | No comparison member dominates candidate | .25 | 1200 | 11 / 0 / 11 |
| neighbor-run | Candidate dominates every comparison member | .75 | 1200 | 2 / 15 / 5 |

The paper does not give these search budgets or a neighborhood definition.
Both tournament interpretations remain explicit sensitivities; neither is selected because its output resembles a published plot.
Comparison samples contain five distinct current positions and may include tournament candidates.
Mutation always changes the selected rate; an odd remaining slot accepts only the first child.
Identical objective values retain both candidates. Common simulator seeds are reused for all policies and generations.
The final unevaluated offspring are retained but excluded from the reported frontier.
Every run’s `choices.json` and `protocol.json` record these decisions.

Independent artifact replay recomputes objectives from native outputs and reconstructs every genetic decision from the optimizer seed.
Across all runs, 33 matings and 2085 mutated components pass. Every final evaluated frontier contains three candidates.
A complete replay of the corrupted-offspring archive fails at the offspring comparison; its traceback and exit status are retained.
This audit validates recorded native outputs and search decisions; it is not an independent simulator implementation.

The restored workspace lacked the previous model and class paths. The preflight failure preceded simulation and is retained.
The evaluator was restored from committed sources; model, Java source, and compiled class hashes match the earlier qualification exactly.
All 400 original native requests reproduce every original result field except elapsed time.
The explicit NetLogo 5.3.1 / Java 11 runtime and declared absent jar remain in the restored manifest.
No new cloud resources were allocated.

`summary.json` records archive sizes and hashes. Every archive member was read back and compared byte-for-byte with its original file.
Archives retain requests, native results, terminal statuses, populations, genetic decisions, exact runner, and protocols.
To repeat the audit, extract a run archive into a fresh directory and run:

```sh
python ../../audit_optimizer.py /path/to/extracted/run /path/to/new-audit.json
```

Executing a new search also requires the qualified NetLogo runtime and an updated manifest containing its verified local paths.
Historical author settings, optimizer convergence, reduced-model optimization, and reduced-to-full-model frontier transfer remain unresolved.
