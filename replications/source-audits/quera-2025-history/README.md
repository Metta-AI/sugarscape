# Recovered historical experiment scripts

Git histories retain four deleted Sugarscape scripts whose exact commits, paths, and hashes appear in `audit.json`.
Retrieve each with `git show COMMIT:PATH` from its named author repository.
The files remain in external research evidence; no historical source is modified.

These are 2024 experiments with older APIs and settings, not verified generators of the 2025 paper figures.
The recovered `scripts/sugarscape_horizon.jl` divides total wealth by both agent count and simulation horizon.
That supplies a normalization hypothesis for the plotted gradient scale; it does not validate the hypothesis.
Its 30-step configuration and discrete metabolism differ from the paper’s later specification.
The older calibration script uses 200 iterations and ten Monte Carlo samples, unlike the paper’s 5,000 iterations and five samples.
Do not silently substitute these settings or claim the paper protocol has been recovered.
