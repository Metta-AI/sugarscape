# McCulloch et al. (2022): calibration on Sugarscape

Source: [Calibrating Agent-Based Models Using Uncertainty Quantification Methods](https://www.jasss.org/25/2/1.html),
DOI `10.18564/jasss.4791`, section 4, Figures 3–6.
Scope excludes the paper's territorial-bird and cattle-farm case studies.

## Source and model audit

The released source is [Urban-Analytics/uncertainty](https://github.com/Urban-Analytics/uncertainty),
revision `0d67e5441c00c41deb834e30d09cf66429b1e676`.
The files in `sugarscape_cg/` are unchanged copies from its `sugarscape/sugarscape_cg/` directory.
The authors' MIT license and Mesa's Apache notice are retained there.
The wrapper supplies deterministic seeds through Mesa's model construction; the original model has no seed constructor argument.

The paper's parameter pairs are (maximum metabolism, maximum vision): `(1,1)`, `(2,10)`, `(4,7)`.
Initial population is described as 100. Growth is one sugar unit per cell per tick.
Figure 3 uses 30 replicates of 100 steps and states every run stabilizes by step 30.
The reported variances at step 30 are 13.0, 12.05, and 18.34.
Although the text says approximately 200 replicates, `ensemble_sizer.py` records these values at 220 replicates.
Original random seeds are not supplied; identical historical trajectories cannot be recovered from the published settings alone.

Source inspection reveals consequential differences:

| Feature | Released Mesa model | DTL engine |
| --- | --- | --- |
| Landscape | Supplied 50×50 integer map | Generated peaks by default; map loading available |
| Boundary | Bounded | Toroidal by default; configurable |
| Vision | Manhattan diamond through Mesa's von Neumann neighborhood | Cardinal rays by default; radial option is Euclidean |
| Starting sugar | Independent integers 6–24 inclusive | Different default range; configurable |
| Placement | Coordinates sampled with replacement | Distinct cells, balanced across quadrants |
| Agent identifiers | Starting position; duplicate positions overwrite scheduled agents | Unique integer identifiers |
| Trait sampling | Independent random draws | Balanced, shuffled endowments |

Duplicate positions also leave unscheduled agents on Mesa's grid. This is a property of the released implementation,
not an intentional correction in our reproduction. It must be distinguished from the paper's prose.

## Predeclared first experiment

This is a model audit, not the completed calibration replication.
Run the unmodified author model for seeds 0–219, at all three parameter pairs, for 100 steps.
Run DTL for seeds 0–29 at each pair, with the same map, bounded world, sugar range, and unlimited lifespan.
Movement is unrestricted up to maximum vision, avoiding an independent movement cap.
Other initialization and movement differences remain explicit; this DTL run is a comparison baseline, not an equivalent model.

For Figure 3, count exact population stability over ticks 30–100 in the first 30 seeds.
The reported all-runs statement requires 30/30 for each pair in this new ensemble.
A counterexample is evidence against generalizing the claim, not proof about the authors' unpublished original seeds.
For Figure 4, report sample variance and its difference from the published value.
No quantitative equivalence threshold is asserted without the original observations or a justified uncertainty model.
Neither variance proximity nor stabilization alone establishes Figures 5–6.

## Run

From the repository root:

```sh
uv venv --no-project --python 3.11 .venv
uv pip sync --python .venv/bin/python replications/mcculloch_2022/requirements.lock
PYTHONHASHSEED=0 .venv/bin/python replications/mcculloch_2022/run.py \
  --output /absolute/new/evidence/path --reference-seeds 220 --dtl-seeds 30 --workers 4
```

Use a new output directory each time. Runs retain their seed, all 101 population observations,
DTL configurations and logs, source hashes, interpreter/platform, command, revision, and working-tree state.
The runner aborts on simulation failures or malformed/incomplete trajectories.
`runs.jsonl` contains one Pydantic-validated result per simulation.

## Remaining work

1. Compare the measured trajectories and preserve discrepancies.
2. Specify a paper-specific engine mode only after resolving source-versus-prose ambiguities.
3. Compare independent engine ensembles against the released model with declared uncertainty criteria.
4. Reproduce history matching and approximate Bayesian computation for Figures 5–6.
5. Review all four targets before counting this paper as replicated.

## Recorded outcome

See [750 recorded trajectories, summary, and plot](results/audit-2026-10-15/RESULTS.md).
The author-code run finished all 660 trajectories before the DTL stage failed its completeness check.
Investigation found that DTL swapped imported sugar/spice and emitted an uninitialized tick-zero record.
The prerequisite engine fix also corrects rectangular-map dimensions and allocation.
The 90 DTL runs were then rerun against the fixed engine in a separate evidence directory.
Both source provenances are retained; no failed run was relabeled as successful.
`author-runner.py.txt` preserves the original runner, verified against its recorded SHA-256.
It is an archival source snapshot; use the current `run.py` for new experiments.
Twelve complete simulations (first and last seed for each model/parameter pair) were replayed;
all 101-point population trajectories matched their recorded results exactly.

The author's `(4,7)` population continues declining after step 30 in 27 of the first 30 seeds.
DTL differs substantially even after the import fix; the source-audit differences remain unresolved.
This is **partial reproduction with discrepancies**, not a completed paper replication.

Regenerate the summary and figure from committed raw trajectories:

```sh
.venv/bin/python replications/mcculloch_2022/analyze.py \
  replications/mcculloch_2022/results/audit-2026-10-15/runs.jsonl \
  --output /absolute/new/analysis/path
```

Use `run.py --engine dtl` or `--engine author-mesa` to execute either stage separately.
