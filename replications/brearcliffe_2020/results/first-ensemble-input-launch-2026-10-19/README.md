# First frozen ensemble input launch

The public runner `run_ensemble_input.py` is executing `released-code-pair-01-repeat-00` from the frozen manifest.
This is Rule M versus EC through 20,000 ticks, with the manifest's prospective seed rather than the qualification seed.
Session 26606 owns this local run. It has a 600-second wall limit, 1 GiB Java heap, 50 MiB output cap and 2 GiB free-space preflight.

The runner checks the manifest, generated model, recorder class, map and matrix extension hashes before launch.
`provenance.json` retains the exact command and hashes of all runtime JARs.
On success it requires 20,001 consecutive finite observations and writes a trajectory hash. A partial output or terminal exit alone is not a completed input.

The execution remains pending. Do not duplicate or restart it without checking the live process and terminal evidence.
This first input exercises the complete runner; a complete paper replication requires all 800 inputs per interpretation and comparisons against the published results.
