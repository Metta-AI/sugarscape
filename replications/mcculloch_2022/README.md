# McCulloch et al. (2022): calibration on Sugarscape

Source: [Calibrating Agent-Based Models Using Uncertainty Quantification Methods](https://www.jasss.org/25/2/1.html),
DOI `10.18564/jasss.4791`, section 4, Figures 3–6.
Scope excludes the paper's territorial-bird and cattle-farm case studies.

**Completed study with mixed results:** validated negative replication of exact step-30 stabilization,
with agreement under the conditional-posterior distribution criterion.
See the [claim-by-claim report and limitations](REPORT.md). This is not a wholly positive paper replication.

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

## Study completion

All declared Sugarscape targets have been exercised and assessed in [REPORT.md](REPORT.md).
The full Figure 4 follow-up contains 11,130 independent simulations across 51 ensembles.
Its numerical stabilization claim remains underspecified; the report does not invent an equivalence threshold.

## Independent implementation validation

`independent.py` implements the released model without calling Mesa or the DTL engine.
It preserves source behavior, including initialization collisions and inactive grid occupants.
This study-specific implementation lives in this fork; it does not make DTL's core engine equivalent to the paper.

The complete-world comparison passed for 80 experiments over 100 steps each.
It includes the original 16 checks plus all 64 calibration parameter pairs at seed 1,000,000.
At every step it compares agent positions and sugar, all 2,500 cells, occupancy, population, and random-generator state.
Run it with `.venv/bin/python replications/mcculloch_2022/test_equivalence.py`.

An additional 660 independent runs matched **all 66,660 population observations** in the author-code ensemble exactly.
The [comparison record](https://github.com/Metta-AI/sugarscape/blob/e72314ec4d198476ca2351d6cb4e6b71e4078c07/replications/mcculloch_2022/results/independent-2026-10-15/comparison.json), raw trajectories, and source provenance are retained.
These checks reduce the risk of mistaking our implementation errors for a negative replication.
They do not resolve differences between the paper's prose and its released source, or recover unpublished original seeds.

The authors do not pin a Mesa version. Both 0.8.7 and 0.8.8 predate the February 2021 archived experiments.
Repeating the first 30 seeds at all three parameter pairs under Mesa 0.8.7 matched all 9,090 population observations
from Mesa 0.8.8 exactly. See [dependency validation](https://github.com/Metta-AI/sugarscape/blob/e72314ec4d198476ca2351d6cb4e6b71e4078c07/replications/mcculloch_2022/results/mesa087-2026-10-15/dependency-validation.json).
This rules out that specific version difference as an explanation; it does not identify the authors' original environment.

## Calibration outcome

Both 10,000-particle experiments completed under the [predeclared protocol](CALIBRATION_PROTOCOL.md).
See [raw trials, validation, and posterior comparison](https://github.com/Metta-AI/sugarscape/blob/801e782693f42d245bc915fed78e0de8016f3d52/replications/mcculloch_2022/results/calibration-2026-10-15/RESULTS.md).
The fixed-prior posterior passes the distribution criterion: total variation distance 0.0198,
with bootstrap 95% upper bound 0.0374 below 0.05.
The modal label differs by only three particles; this is not evidence of a substantive posterior disagreement.
History matching took eight waves and retained 21 combinations, versus ten waves and 15 in the archive.
That stochastic path difference alone is not a negative replication.

## Recorded outcome

See [750 recorded trajectories, summary, and plot](https://github.com/Metta-AI/sugarscape/blob/801e782693f42d245bc915fed78e0de8016f3d52/replications/mcculloch_2022/results/audit-2026-10-15/RESULTS.md).
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
That initial audit was partial. The completed calibration, variance curve, and validation are assessed in [REPORT.md](REPORT.md).

Raw trajectories remain in the [immutable experiment archive](https://github.com/Metta-AI/sugarscape/tree/960e703f24da4f498ca423bdaa5537c3200e5c8c/replications/mcculloch_2022/results). Summaries, figures, and source pins stay in this PR. Existing local trajectories are preserved. Restore the required input before reproducing an analysis:

```sh
git show 960e703f24da4f498ca423bdaa5537c3200e5c8c:replications/mcculloch_2022/results/audit-2026-10-15/runs.jsonl > /absolute/raw-trajectories.jsonl
```

Regenerate the summary and figure from that archived input:

```sh
.venv/bin/python replications/mcculloch_2022/analyze.py \
  /absolute/raw-trajectories.jsonl \
  --output /absolute/new/analysis/path
```

Use `run.py --engine dtl` or `--engine author-mesa` to execute either stage separately.

## Archived run records

Primary runners, analysis code, fixed study inputs, source provenance, and study findings remain tracked.
Dated run directories, checkpoint notes, copied runners, and generated source readbacks are preserved in [the experiment archive](https://github.com/Metta-AI/sugarscape/tree/801e782693f42d245bc915fed78e0de8016f3d52/replications/mcculloch_2022).
Regenerated evidence belongs in the ignored output directories.

Commands and provenance records may reference archived inputs or historical scripts. Restore those dependencies before running the corresponding analysis:

```sh
git restore --source=801e782693f42d245bc915fed78e0de8016f3d52 --worktree -- REPOSITORY_PATH
```

Replace `REPOSITORY_PATH` with the required archived file or directory. The restore leaves the index unchanged and the restored evidence ignored. The [original evidence archive](https://github.com/Metta-AI/sugarscape/tree/e72314ec4d198476ca2351d6cb4e6b71e4078c07/replications/mcculloch_2022) retains raw outputs removed in previous cleanups.
