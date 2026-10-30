# Raimbault et al. (2019): Space Matters

Paper: [Space Matters: Extending Sensitivity Analysis to Initial Spatial Conditions in Geosimulation Models](https://www.jasss.org/22/4/10.html).
Scope: Sugarscape results; Schelling experiments are excluded.
Status: **24/24 Table 4 values reproduced from archived data; all55,000 fixed-reference inputs replayed; generated-landscape ensemble remains unfinished**.
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
[Full comparisons and coverage](https://github.com/Metta-AI/sugarscape/blob/1d5c092ec4e2b5c49312535ed7011cbe731368f9/replications/raimbault_2019/results/archive-2026-10-15/results.json) preserve every grid distance and input hashes.

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
Historical revisions and the complete reference replay establish the 10,000-step archive horizon.
Model setup also draws continuous metabolism and sugar endowments, with integer vision and lifetime.
The released OpenMOLE script requests 100 repeats, whereas the archived reference has 50.
New runs must follow the validated experiment rather than silently using a mismatched current script.

## Verified replay and remaining work

[The completed reference replay](https://github.com/Metta-AI/sugarscape/tree/1d5c092ec4e2b5c49312535ed7011cbe731368f9/replications/raimbault_2019/results/reference-complete-2026-10-18) covers all 55,000 inputs at 10,000 steps.
All 110,000 Gini comparisons match the archived reference exactly, and all 53 source/dependency hashes verify.
Duplicate and incomplete inputs receive no credit.

[The generated production batch](https://github.com/Metta-AI/sugarscape/tree/06a270a7c616162cf410c30338be68e531ebd1fb/replications/raimbault_2019/results/generated-production-complete-2026-10-18) covers 8,000 original inputs at the same horizon.
All 16,000 Gini comparisons match exactly. Of 80,000 morphology comparisons, 31 differ within the predeclared absolute tolerance of 1e-12.
These inputs all have population ten; this ordered batch does not represent the complete generated-landscape ensemble.
The 2,727,994-input experiment and fresh spatial conclusions remain incomplete.

[The broader vision-cache comparison](https://github.com/Metta-AI/sugarscape/tree/06a270a7c616162cf410c30338be68e531ebd1fb/replications/raimbault_2019/results/vision-cache-strata-complete-2026-10-19) preserves 330,000 history values and 91,905 original world rows, including random state.
Median total process time falls from 130.1 to 102.4 seconds on the frozen 44-execution sample.
Full-grid performance remains unproven; production retains the author implementation and existing cost estimate.

## Archived run records

Primary runners, analysis code, fixed study inputs, source provenance, and study findings remain tracked.
Dated run directories, checkpoint notes, copied runners, and generated source readbacks are preserved in [the experiment archive](https://github.com/Metta-AI/sugarscape/tree/06a270a7c616162cf410c30338be68e531ebd1fb/replications/raimbault_2019).
Regenerated evidence belongs in the ignored output directories.

Commands and provenance records may reference archived inputs or historical scripts. Restore those dependencies before running the corresponding analysis:

```sh
git restore --source=06a270a7c616162cf410c30338be68e531ebd1fb --worktree -- REPOSITORY_PATH
```

Replace `REPOSITORY_PATH` with the required archived file or directory. The restore leaves the index unchanged and the restored evidence ignored. The [original evidence archive](https://github.com/Metta-AI/sugarscape/tree/1d5c092ec4e2b5c49312535ed7011cbe731368f9/replications/raimbault_2019) retains raw outputs removed in previous cleanups.
