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
