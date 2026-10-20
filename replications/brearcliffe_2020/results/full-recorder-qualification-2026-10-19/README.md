# Full-horizon recorder qualification

The corrected recorder and native NetLogo BehaviorSpace agree exactly on all 320,016 numeric fields across 20,001 observations.
Both runs use Rule M versus EC and prospective seed 20261019 through tick 20,000.
The custom recorder completed in 220.450 seconds; BehaviorSpace completed in 222.884 seconds. Both exited zero.

The archive contains both full trajectories, commands, terminal receipts, original matrix extension, seeded model, and recorder sources.
Every extracted file matched its source byte for byte. Running `verify-full.py CUSTOM_DIRECTORY NATIVE_DIRECTORY OUTPUT.json` on that extraction reproduced the comparison exactly.
`validation.json` pins the archive and every retained file. The prior failed recorder evidence remains in the preceding result directory.

Population A ranges from 399 to 400; population B remains 400. All fields are finite and cumulative deaths are nondecreasing.
This qualifies measurement for one seed and pairing. It does not validate an independent model or reproduce the paper's 800-run ensemble.
A linear projection at this pairing's runtime is about 49 CPU-hours for 800 runs; other methods and worker contention remain unmeasured.
