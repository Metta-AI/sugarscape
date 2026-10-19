# Disease-count correction: full native controls

The original declaration orders disease count before maximum disease length.
`Core/Init.hs` reversed them. The correction changes the destructuring and returned
tuple order; all other 59 source files and the observer remain unchanged relative
to each baseline. `source-overrides` contains the exact corrected file.

Both 100-step Animation V-1 controls reproduce their existing native baselines
byte-for-byte across all CSV files and resolved parameters. This holds for the
historical grid and the coordinate/observation-corrected grid.

| First seed 602352629, Animation V-2 | Count correction only | Combined corrections |
| --- | ---: | ---: |
| Generated disease entries | 25 | 25 |
| Distinct diseases | 24 | 24 |
| First zero-infection time with survivors | 69 | 61 |
| Population at step 1,000 | 205 | 200 |
| Infected at step 1,000 | 0 | 0 |

The generated lengths are 1–10. The historical generator still permits duplicate
entries; the correction does not silently force uniqueness. The four full native
trajectories contain 10,689 snapshot agent observations. Independent checks verify
source pins, the exact edit, control parity, resolved disease pools, timestamps,
snapshot infection/population/resource counts, and environment totals. Published
gzip exports reproduce the complete audit JSON exactly.

These are first-seed results, not an ensemble finding or validated whole-paper
negative replication. The remaining 99 seeds per version use the frozen original
seed list and retain these index-zero trajectories without rerunning them. The
sequential worker has one CPU, 2 GiB, a 4 GiB disk guard, and a three-hour outer limit.
See `../disease-count-ensemble-launch-2026-10-17` for its exact protocol and launch.

To repeat the independent first-output audit, rebuild the pinned native trees,
restore CSV files, and put each variant's outputs under its `first` directory:

```
python audit_disease_count_correction.py CORRECTION_ROOT NATIVE_HOME NEW_AUDIT.json
```

`NATIVE_HOME` corresponds to the recorded `/root/sugarscape` and includes the
historical observer builds and original/corrected V-1 baseline outputs. The audit
requires the complete four-run marker. The original field-order error and all
historical outputs remain preserved separately.
