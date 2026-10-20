# Frozen ranking experiments

The reduced-model batch contains 2,538,400 native runs in 44 disjoint shards.
It covers every distinct qualified reduced model, 100 frozen policies, both tax clocks, and each size's maximum simulation count from Table 2.
Counts are 88, 173, 427, 1,375, and 3,900 per policy/clock at widths 40, 30, 20, 10, and 5.

A separate 10,000-run full-size experiment uses seeds 101–150, compared with existing reference seeds 1–50.
It is queued after the reduced batch, keeping at most four workers active.
Figure 10 contains a full-size comparison below perfect agreement; comparing a result with itself would be an invalid substitute.
The source-driven addendum records this control before ranking analysis.

Each batch has a one-hour execution limit, 30-minute per-shard limit, four workers, and 512 MiB Java heap per worker.
Inputs are retained as gzip JSON Lines; each compressed and expanded stream has a recorded hash.
The unchanged batch evaluator reads the decompressed stream through standard input.
Before scientific execution, this actual pipeline reproduces all 400 published reference runs exactly, excluding elapsed time.

`reduced-protocol.json` preserves the original executed generation protocol and `prepare_reduced_rankings_executed.py` preserves its exact generator.
The current generator also supports the separate independent full-size experiment; its protocol is `independent-full-protocol.json`.
`ranking-analysis-addendum.json` declares the three nominal budgets, integer rounding alternatives, pooled/stratified comparisons, rank ties, and kappa weights.
It also records that the original uncertainty-bar procedure remains unresolved.

These are running/queued experiments, not completed ranking results. No additional study-completion credit is assigned.
