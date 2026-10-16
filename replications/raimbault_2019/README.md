# Raimbault et al. (2019): Space Matters

Paper: [Space Matters: Extending Sensitivity Analysis to Initial Spatial Conditions in Geosimulation Models](https://www.jasss.org/22/4/10.html).
Scope: Sugarscape results; Schelling experiments are excluded.
Status: **24/24 Table 4 values reproduced from archived data; three archived simulations exactly reproduced; ensemble unfinished**.
This is not yet a completed paper replication.

## Sources and exact reanalysis

Author code: [JusteRaimbault/SpaceMatters](https://github.com/JusteRaimbault/SpaceMatters),
revision `270cc7f112b3a999b10e02b0f9525038d6d4754d`.
Data: [Harvard Dataverse, doi:10.7910/DVN/9JI57U](https://doi.org/10.7910/DVN/9JI57U), CC0-1.0.
The embedded NetLogo model has a separate CC BY-NC-SA 3.0 notice; the dataset license does not replace it.

The independent Python analysis follows the authors' `distancesToRef` definition:
twice the squared Minkowski distance divided by the sum of sample variances of the two phase diagrams.
Reference Gini values are averaged across replicates before comparison.
Missing grid/parameter combinations are excluded from the paired comparison, as in the released R code;
every exclusion is counted in the result manifest.

All six summaries at each of q=1,2,3,10 match Table 4 at published precision.
The Euclidean mean, median, minimum, and maximum are 1.29594, 1.52272, 0.08909, and 2.98273.
[Full comparisons and coverage](results/archive-2026-10-15/results.json) preserve every grid distance and input hashes.

Run with Python and NumPy 1.26.4:

```sh
python3 replications/raimbault_2019/fetch_sources.py --output /absolute/new/data
python3 replications/raimbault_2019/analyze_archive.py \
  /absolute/new/data/reference.csv /absolute/new/data/generated.csv --output /absolute/new/analysis
```

The downloader verifies immutable file contents against `sources.json`.
The approximately 30 MB source data remain in the chosen directory instead of being duplicated in the Git repository.

## Design details requiring fidelity

The archived reference contains 55,000 simulations: 1,100 parameter combinations with 50 repeats each.
Population takes 11 values (10 through 510 in steps of 50), not the ten bins described in the paper.
The generated-grid archive contains 54,560 aggregated combinations across 50 grids, rather than a complete 55,000.
Thirty-two grids have all 1,100 points; fourteen lack 20 points each, and four lack 40 each.
These facts explain the source dimensions; they do not themselves establish an incorrect substantive conclusion.

The `.source` file for the fixed reference includes an incorrect link to the generated-grid data.
The correct fixed-reference artifact is Dataverse file 3596481, persistent identifier `doi:10.7910/DVN/9JI57U/NIJ2BN`.
Its original CSV format is fetched explicitly.

The NetLogo model replaces dying agents, so population remains fixed while wealth evolves.
The current model averages Gini over the last 1,000 steps; its configured run length is also 1,000.
Historical revisions ran 10,000 steps, so the archive horizon needs verification.
Model setup also draws continuous metabolism and sugar endowments, with integer vision and lifetime.
The released OpenMOLE script requests 100 repeats, whereas the archived reference has 50.
New runs must follow the validated experiment rather than silently using a mismatched current script.

## Fresh simulation pilot and provenance investigation

The first archived reference input completes 1,000 steps with constant population under NetLogo 5.3.1.
Its terminal Gini is 0.3942307692 versus archived 0.2445487365.
Its moving-window Gini is 0.2939769248 versus archived 0.3017667641.
[Trajectory and comparison](results/replay-pilot-2026-10-15/comparison.json) retain this unresolved mismatch.
**This was a horizon mismatch, not a negative replication.** The 10,000-step replay below resolves this input.

The archive filename is dated March 28, 2017; that date does not prove which revision generated its contents.
Commit `b71d1cf73f036749a83335b6a13cabf345599039` added explicit seeding and corrected resource initialization on April 3, 2017.
Commit `74ade6eaa77af4caa65183a2eba6a3ded4708e0f` changed the horizon from 10,000 to 1,000 on September 27, 2018.
The model header identifies NetLogo 5.1.0, while this pilot uses 5.3.1; the original execution runtime remains unverified.
The historical horizon is confirmed for the first input by exact replay; additional input checks remain in progress.

The Java adapter invokes the released setup and records each step without editing the model.
Place `NetLogo.jar` before the wildcard classpath: `NetLogoLite.jar` otherwise shadows full workspace classes in this installation.
The initial compilation failure is preserved with the successful execution log.

```sh
/path/to/jdk/bin/java -Djava.awt.headless=true \
  -cp '/path/to/netlogo/app/NetLogo.jar:/path/to/netlogo/app/*' \
  replications/raimbault_2019/Replay.java \
  /path/to/SpaceMatters/sugarscape/HEADLESS_Sugarscape.nlogo \
  /path/to/reference.csv 0 10000 /absolute/new/trajectory.csv
```

Run from the author model directory, using absolute paths for the adapter and artifacts.
The adapter requires an explicit choice between the two documented horizons, 1,000 and 10,000 steps.
It changes only `total-time-steps` after the released setup and records every simulated tick.

## Historical horizon validated

At 10,000 steps, the first archived input reproduces terminal Gini **0.24454873646209388**
and last-1,000-step mean Gini **0.3017667640537167**, both exactly equal to the archive's recorded NetLogo outputs.
Independent Python recomputation of the window mean differs by 2.22e-16 from NetLogo's summation.
The first 1,000 trajectory rows are identical to the earlier pilot.
[Raw trajectory, execution log, and comparison](results/horizon-validation-2026-10-15) preserve the successful replay.
Thus the initial mismatch is explained by the later horizon change, without changing seed, behavior, parameters, or runtime.
Rows 1 and 54,999 also reproduce both archived NetLogo Gini outputs exactly.
[Additional comparisons](results/horizon-validation-2026-10-15/additional-comparisons.json) include complete trajectories and independently recomputed window means.
These three inputs validate the corrected replay path; they do not complete the spatial ensemble.

## Remaining work

1. Run the original NetLogo 5 model and morphology extension against archived seeds.
2. Validate and implement the study-specific simulation behavior in this fork.
3. Recreate the spatial layouts, reference ensembles, and generated-grid ensembles with declared uncertainty criteria.
4. Reproduce the phase-diagram contrasts and distance summaries from fresh simulations.

Archived-data reanalysis alone does not satisfy these simulation requirements.
