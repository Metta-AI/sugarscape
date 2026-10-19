# Migration and pollution spatial diagnostics

Three 1,000-step trajectories use seed 602352629 and snapshots every ten steps.
Two additional historical-observer executions verify that denser cell exports do
not change the model. All 60 historical source files remain byte-identical.
The observer adds cell snapshots and a named migration configuration with vision
range 1–15, preserving the original 1–10 configuration.

| Configuration | Final population | Agent observations | Cell observations |
| --- | ---: | ---: | ---: |
| Original migration | 139 | 14,515 | 257,651 |
| Migration, vision range 1–15 | 146 | 15,031 | 257,651 |
| Original pollution | 191 | 19,980 | 257,651 |

For both historical configurations, agent records, every-step summaries, trade
records, resolved parameters, and endpoint cells exactly match the original observer.
All 303 spatial snapshots independently reconcile population, agent resources,
environment resources, and pollution with their summaries. The published gzip
exports reproduce the complete audit JSON after extraction.

`original_exports_exact: false` for `migration_vision15` means this additional
configuration has no historical-observer comparison, not a failed parity control.
The resolved-parameter comparison confirms that only the vision range changes.
The appendix's suggestion is interpreted as a maximum of 15, not fixed vision 15.

The migration figure separates cell occupancy from pre-event agent observations.
Both views retain the original coordinate-aliasing defect. The pollution figure
uses one scale across four times; absent aliased cells appear white. These are
first-seed diagnostics, not a 100-run result or proof of the qualitative claims.
No wave-presence threshold was chosen from the output. Independent Weaver source
identity and runtime, corrected-source sensitivity, and explicit qualitative
comparison remain outstanding.

Rebuild the pinned original model and observer using `run.sh`; it executes five
native trajectories under the recorded one-CPU, 3 GiB, 30-minute bound. Restore
CSV files with `gzip -dk` before the independent audit:

```
python audit_spatial.py SPATIAL_NATIVE_ROOT ORIGINAL_OBSERVER_ROOT NEW_OUTPUT
```

`SPATIAL_NATIVE_ROOT` contains the pinned `source`, compiled `observe`, observer,
protocol, completion marker, and the `reference` and `spatial` output folders.
The audit verifies both historical source trees, the original binary, and the
exact observer-only edits. Original unit tests are compiled unchanged; no new
unit or integration tests were added.
