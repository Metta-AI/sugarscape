# Frozen full-ensemble preparation

Two interpretations each contain 16 ordered pairings × 50 repetitions × 20,001 observations.
The released-code interpretation uses learning rate 0.9 and gamma 0.8; the paper-table interpretation uses 0.8 and 0.9.
Each pairing/repetition has a distinct prospective seed, reused across interpretations for paired sensitivity comparisons.
These are not historical author seeds. Neither interpretation will be selected retrospectively as the sole reported result.

`prepare_ensemble.py AUTHOR_MODEL NEW_OUTPUT` verifies the author source hash and generates all model files and the manifest.
Two complete preparations produce identical bytes in all 1,602 files. All 1,600 models reverse exactly to the author source after removing the declared seed and parameter edits.
The manifest pins every generated model. The original map and matrix extension remain required beside models at execution time.

No full ensemble has been launched. First qualify all pairings, then measure representative full-horizon reinforcement-learning runs on the execution host.
The 20,000-tick non-learning pilot alone is insufficient for a reliable runtime or cost estimate.

Retain all initial and subsequent observations for each run. Compare arithmetic means of the seven per-breed metrics across all 50 repetitions at every tick with Figures 3–9.
Do not replace individual trajectories with time averages or apply logs before averaging. Published panels use logarithmic display scales.
Show run-level uncertainty and digitization uncertainty separately. The 112 raster panels require calibrated numeric extraction before numeric agreement can be claimed.
Report failed or incomplete runs explicitly; they do not satisfy the required 50 repetitions and must not be silently omitted from means.
Record original failures and any bounded retries, preserving seeds and source hashes. The independent fork implementation and its validation remain separate outstanding work.
