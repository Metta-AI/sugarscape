# Replacing Sugarscape (Kremer-Herman and Gupta, SimuTools 2023)

Status: incomplete study. These are operational replays, not validated positive or negative paper replications.

The [author-hosted paper](https://digital-terraria-lab.github.io/assets/papers/kremer-herman:2023:replacing-sugarscape.pdf) describes three baseline experiments, twenty additional seeds, seventeen example configurations, and trade/lending comparisons. `published_targets.json` records the seed-level targets and hashes all seventeen released examples.

## Source provenance

The author's [released implementation](https://github.com/digital-terraria-lab/sugarscape) has earliest stable revision `032abd2d2338aadc5ad0287dae7520539f7af57b` (December 20, 2023). This revision is not verified as the exact paper version. No simulation rules are modified. Results use Python 3.11.14 and `PYTHONHASHSEED=0`.

`run.py` reads the original example configuration, retains its bytes and source hashes in the evidence, and invokes the native command-line application. Overrides are seed, headless mode, logging, debug output, and horizon. Figure 2 requires 2,500 steps for reproduction; the other pilots retain the released 500-step horizons. Figure 1/3 screenshot times remain unknown.

## Completed baseline execution

| Released example | Observations | Minimum population | Maximum population | Final population |
| --- | ---: | ---: | ---: | ---: |
| Seasonal migration | 501 | 230 | 250 | 241 |
| Constrained reproduction | 2,501 | 357 | 1,197 | 1,104 |
| Disease | 501 | 143 | 860 | 822 |

All three complete at their requested horizons. Evidence includes raw trajectories, exact configurations, stdout/stderr, source hashes, and runtime manifests. Population, consecutive timesteps, seed, all scalar metrics, and all array elements are checked.

The paper describes disease survivors falling to roughly 20; this release reaches 143. Its reproduction figure also appears to settle below this run's final population. These are unresolved discrepancies. Historical source/configuration differences, model implementation, and measurement must be investigated before a negative verdict.

## Observation without changing trajectories

`observe.py` imports the pinned model, extracts the native CLI defaults, applies the native configuration functions, seeds the native random generator, and runs the native lifecycle. A subclass records agent IDs, coordinates, age, vision, metabolism, infection counts, season, and hemisphere after initialization and each timestep. It does not draw random numbers or modify agents.

`audit_observation.py` requires byte-identical native trajectories before accepting supplemental observations. Both disease and seasonal runs pass all 501 observations. Disease infections reach zero at timestep 247 and remain absent at termination. This matches the qualitative eradication/recovery sequence, but not the reported survivor minimum.

Seasonal analysis retains both coordinates and the released cell labels. Source inspection finds initial season assignment uses the y coordinate while the hemisphere label uses x. This needs auditing before interpreting north/south occupancy; no coordinate convention has been silently corrected.

## Run

Use Python with Pydantic 2 and an unmodified checkout at the pinned release. Output directories must not exist.

```bash
python replications/replacing_2023/run.py ENGINE disease_basic 12345 OUTPUT
PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 python replications/replacing_2023/observe.py ENGINE OUTPUT OBSERVED
python replications/replacing_2023/audit_observation.py OUTPUT OBSERVED
```

## Remaining work

- Establish historical source/configuration equivalence and investigate the disease and reproduction discrepancies.
- Analyze seasonal migration, survival, and hibernation from agent observations; verify spatial/season conventions.
- Run and assess all twenty additional published seeds for all three scenarios.
- Define transparent qualitative assessment criteria before classifying those runs. The authors provide no numerical similarity margin.
- Complete the seventeen example validations and trade/lending carrying-capacity comparisons.
- Integrate validated behavior into the Metta-AI engine; these pinned-source replays establish the reference evidence first.

## Pre-conference source diagnostic

The conference took place December 14–15, 2023. The stable archive was created December 20.
[Source audit](historical-source-audit.json) verifies that every top-level archived Python file matches upstream commit `955860e9b6e4d509f4e8fb19439d588659df919c`.
That revision includes December 20 changes to disease modifiers and universal income, but precedes the separate movement/vision change.
The [retained patch](preconference-to-archive.patch) records model changes from the last pre-conference revision, `d57d39dd034fe5926ad51ed5f3f7b6837a2210ac`.
All three example configurations are byte-identical across these revisions.

The last pre-conference revision was selected by chronology, before observing its results; it is not a verified paper pin.
Its disease baseline completes 500 steps with minimum population 136 and final population 956.
The observation replay is byte-identical across all 501 native records.
This revision still does not reproduce the paper's approximately twenty survivors; chronology alone does not resolve the mismatch.
Both releases and their evidence remain retained. No version is selected merely because it produces a closer result.

`run_published_seeds.py` now executes all twenty Table 3 seeds, in printed order, through the same verified runner.
The archived-release disease batch is running. It records each complete trajectory and does not assign subjective similarity verdicts.
The two explicitly reported extinction seeds, 12881 and 22744, provide concrete outcomes to compare once the batch completes.

The pre-conference constrained-reproduction run also completes all 2,500 steps.
[Full comparison](results/preconference-2026-10-15/reproduction-comparison/comparison.json) finds identical populations at every one of 2,501 observations.
Only `meanHappiness` differs, at 2,500 observations; every other logged field agrees.
Thus these December changes cannot explain the reproduction-population mismatch.
Both runs have population 840 at timestep 60 and 1,071 at timestep 100, rather than the paper's described first major decline in that interval.
Descriptive windows and a [comparison plot](results/preconference-2026-10-15/reproduction-comparison/revision-comparison.png) are retained without treating those windows as statistical equivalence tests.

## Complete twenty-seed disease replay

The [archived-release batch](results/disease-published20-2026-10-15/audit.json) completed all twenty original Table 3 seeds at the released 500-step horizon.
Independent validation checks all 10,020 observations, native source/configuration hashes, original seed ordering, initial populations, finite metrics, and complete trajectories.
No seed becomes extinct. The paper's reported extinction seeds, 12881 and 22744, finish with 801 and 860 agents respectively.
Their minimum populations are 51 and 135.
All raw trajectories, run manifests, logs, and outcomes are retained; no seed is excluded.

The full twenty-seed pre-conference batch and infection-observation replays of those two seeds are running.
The paper's exact assessment times and source revision remain unverified; this result is not yet a validated negative replication.

[Infection observation replays](results/disease-extinction-seed-observations-2026-10-15/eradication-audit.json) for seeds 12881 and 22744 completed successfully.
All 1,002 native trajectory records match their original runs byte for byte.
Infections reach zero at timesteps 30 and 42 respectively and never return through timestep 500.
Both populations recover. Thus these released runs do not contain a continuing epidemic at the stopping horizon.
Exact historical-rule/configuration alignment remains unresolved; this evidence alone does not establish a paper-level negative replication.
