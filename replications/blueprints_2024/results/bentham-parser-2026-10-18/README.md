# Complete Bentham released-parser equivalence

The unchanged v2024.1 `plots/plot.py` reads all 500 original native trajectories through its public command-line interface. Its source bytes match the pinned Git revision. All 2,635,068,222 input bytes are hash-verified before delivery.

Named pipes expose the full original JSON contents without a second raw-file copy. One feeder follows the frozen directory enumeration; the parser's complete filename log confirms exactly the same 500-file order. No JSON fields, model code, parser code, metric definitions, or seeds are substituted.

The parser consumes 2,500,500 observations and reproduces all 30,006 independently aggregated metric values within the existing `rtol=1e-12, atol=1e-8` comparison. Population, starvation, and combat means match exactly. Maximum absolute errors are 5.68e-14 for time to live, 4.95e-10 for total wealth, and 1.42e-13 for age at death. Its classification is 0 extinct, 0 worse, 500 better.

This closes the released-parser check left open by the Bentham figure comparison. The historical Figure 6 death-definition discrepancy remains: published curves match all-cause deaths, while the release plots starvation plus combat. Other paper experiments remain incomplete.

The first feeder attempt stalled while creating 500 blocked writers, before parser launch. Its script, process sample, and interruption receipt are retained without result credit. The successful feeder uses one writer and an unchanged parser subprocess, bounded by 600 seconds internally and 660 seconds externally.

`run.py` expects the sibling `blueprints-bentham-timeseries-001` inputs and provenance, plus the pinned author checkout. Use a fresh directory because named pipes are created exclusively. `command.json`, `supplied.json`, parser stdout/stderr, native output, and export hashes retain the executed workflow. Decompressed exports are byte-identical to originals.
