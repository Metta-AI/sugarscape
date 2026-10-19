# Broader vision-cache qualification

The native geometry check compares all six cached radii at every patch against freshly reconstructed `patches at-points` sets. All 15,000 patch/radius combinations match, including boundaries. It compares set membership; movement ordering and trajectories require the separate simulation comparisons.

The frozen sample selects population `10 + 50*i` and landscape `4*i`, for `i=0..10`, from the existing 550-input sizing archive. It covers all eleven population levels and eleven distinct landscapes without selecting on outcomes. Original settings and seeds are retained.

The bounded local batch runs baseline/cached/cached/baseline: 44 complete 10,000-tick executions if successful. Each process has a 300-second limit and 768 MiB heap, for a 1,200-second total process bound. The batch is running; no completion or speedup credit is assigned. The first baseline overlapped the brief geometry check, so timing is observational on shared hardware.

The prepared full-state audit checks all Gini histories, original exported-world fields including random state, twelve final metrics, and the archived targets. It excludes only export timestamps and the added cache column. Successful full-batch validation remains pending.

Existing production models and cloud jobs are unchanged. No full-grid spending estimate or paper-completion count changes.
