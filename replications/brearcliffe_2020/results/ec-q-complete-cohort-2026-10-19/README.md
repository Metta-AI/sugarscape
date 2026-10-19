# Complete EC/Q cohort

All 50 released-code inputs complete 20,000 ticks plus initial state: 1,000,050 observations. The combined audit verifies 353 inputs and preserves every prior 303-input audit record exactly.

The downloaded 33,423,465-byte archive has SHA-256 `134a31c224bef33318dd398bb90b154b3de1c9a083f67e0ad1c425f1eb2143a4`. All 500 run files match the snapshot hashes. The initial local audit failed because 102 prior provenance files and 102 map files were missing. `restore_prior.py` restored their exact bytes from retained, hash-verified archives without overwriting existing files. The initial failure, restoration receipt, fresh extraction, and successful re-audit remain retained.

Independent R verifies 320,016 means, 320,016 sample standard deviations, and all fourteen endpoint bootstrap intervals. Maximum scaled differences are 1.30e-15, 3.58e-14, and 5.59e-16, respectively. Resampling uses the recorded 20,000 whole-run draws; this checks arithmetic, not independent random-number generation.

The corrected Figure 3–9 comparison retains 3,781 visible and 95 unresolved curve records. Eight of fourteen endpoint mean ranges overlap the paper raster intervals. The remaining six are B wealth, A vision, B combat deaths, B starvation deaths, B mean age, and A maximum age. Each pointwise bootstrap interval overlaps its paper raster range. These intervals are exploratory and not simultaneous; paper between-run uncertainty and historical seeds remain unknown.

This pairing uses Q-learning, so the manuscript/released-code learning-rate and discount-rate disagreement remains relevant. Neither this comparison nor the completed cohort establishes equivalence, a validated negative replication, or whole-paper completion. Nine released-code cohorts, paper-table sensitivity, and an independent fork implementation remain outstanding.
