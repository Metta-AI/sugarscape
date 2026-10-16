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

The full twenty-seed pre-conference batch and infection-observation replays are complete; results follow below.
The paper's exact assessment times and source revision remain unverified; this result is not yet a validated negative replication.

[Infection observation replays](results/disease-extinction-seed-observations-2026-10-15/eradication-audit.json) for seeds 12881 and 22744 completed successfully.
All 1,002 native trajectory records match their original runs byte for byte.
Infections reach zero at timesteps 30 and 42 respectively and never return through timestep 500.
Both populations recover. Thus these released runs do not contain a continuing epidemic at the stopping horizon.
Exact historical-rule/configuration alignment remains unresolved; this evidence alone does not establish a paper-level negative replication.

## Complete pre-conference seed comparison

The [pre-conference twenty-seed batch](results/preconference-disease-published20-2026-10-15/audit.json) also completed successfully and passes the independent 10,020-observation audit.
[All forty runs](results/preconference-disease-published20-2026-10-15/revision-comparison.json) retain their original seeds, configurations, and complete trajectories.
Neither revision produces an extinction by the released 500-step horizon.
Pre-conference seeds 12881 and 22744 finish at populations 801 and 984, with minima 51 and 110.
The post-conference disease changes therefore do not explain the two reported extinction outcomes by themselves.
Earlier source/configuration provenance and the paper's assessment horizon still require investigation.

## Seasonal identity tracking and remaining seed runs

All twenty published seasonal seeds and their observational replays are complete. The twenty-seed reproduction batch remains in progress.
Each completed batch receives an independent full-trajectory audit.
The seasonal batch then replays every seed with agent observations and requires byte-identical native trajectories before accepting those observations.
The generalized batch auditor has also revalidated the completed disease batch without changing its outcomes.

The [baseline seasonal cohort analysis](results/seasonal-cohort-pilot-2026-10-15/cohorts.json) verifies the actual cell-season convention at all 501 observations.
Actual seasons follow the y-coordinate halves, despite the separate x-based hemisphere label.
The analysis tracks the original agents in the wet half immediately before each seasonal flip, excluding replacement agents from migration counts.
After the first flip, 100 of 199 cohort agents enter the newly wet half during the next 50 steps; 93 of those migrants are absent by the window's end.
An endpoint-only count would miss those migrations, so both events and final survival/location are reported separately.
Nine transition cohorts are retained. Presence in the dry half alone is not classified as hibernation, and no numerical paper-similarity threshold is inferred.

## Complete seasonal ensemble

[Retained evidence](results/seasonal-published20-2026-10-15) covers all twenty Table 3 seeds, with 10,020 native observations and byte-identical observer replays.
`analyze_seasonal_ensemble.py OBSERVED OUTPUT` requires every original seed and analyzes nine complete seasonal windows per seed.
The executable ensemble analysis reproduces the independently assembled summary byte-for-byte.

Across 180 windows, 33,612 wet-half cohort memberships include 14,369 migrations; 11,852 migrant memberships are absent at the window's end.
Memberships can include the same agent in different windows and are not independent samples.
Migrants have higher mean vision than non-migrants in all twenty seeds.
Pooled membership means are 4.015 versus 3.247 vision and 1.428 versus 1.741 sugar metabolism.
Survivors ending in the dry half average 2.930 vision and 1.045 metabolism.
These associations support the paper's directional description of vision and migration under the tested released configuration.

Absence does not establish starvation: the configured maximum lifespans range from 60 to 100 steps.
Dry-half presence does not establish the paper's hibernation behavior.
Historical revision equivalence, cause-specific mortality, and a predeclared quantitative interpretation of the paper's qualitative similarity criterion remain unresolved.
This is additional measured evidence, not a completed paper-level replication.

## Cause-specific seasonal mortality pilot

The observer now copies native death records before the original statistics method clears them, without changing simulation rules or random draws.
`audit_deaths.py BASELINE OBSERVED` first requires native trajectory parity, then reconciles disappearing identities and every native per-step cause count.
`analyze_seasonal_deaths.py OBSERVED OUTPUT` joins those causes to original wet-half cohorts across all nine complete seasonal windows.

[Seed 14133 evidence](results/seasonal-deaths-pilot-2026-10-15) preserves 501 byte-identical native observations and 4,204 individual death records.
The full run contains 2,775 starvation deaths and 1,429 aging deaths, with no combat or disease deaths.
Cohort results separate migration, survival, starvation, and aging without counting replacement agents as survivors.
Native cause labels identify proximate deaths; they do not establish the causal effect of seasons.
The complete twenty-seed cause-specific analysis is now available below.

## Complete seasonal death analysis

[All twenty seeds](results/seasonal-deaths-published20-2026-10-15/summary/summary.json) pass native trajectory parity, identity reconciliation, and per-step death-cause count checks across 10,020 observations.
The observer records the original implementation's cause labels before statistics clears the death registry.
Each seed is analyzed with `audit_deaths.py` and `analyze_seasonal_deaths.py`; `summarize_seasonal_deaths.py OBSERVED COHORTS OUTPUT` verifies all original seeds and evidence hashes.

Across 180 windows, 33,612 original wet-half cohort memberships partition into 21,883 aging deaths, 8,140 starvation deaths, and 3,589 survivors.
No cohort member dies of combat or disease. Aging exceeds starvation in every seed.
These counts explain why disappearance cannot be equated with starvation in this released configuration.
They neither rule out seasonal starvation nor estimate its causal effect.
Memberships may repeat an agent across windows; counts are not independent samples.
The paper's qualitative replication verdict and exact historical configuration remain unresolved.
