# Bounded historical-runtime handoff

The running task-local handoff waits for the current five-fold qualification. It does not start a historical fit on a partial or failed qualifier. It checks the frozen script/input hashes, then reopens all five saved outputs in a fresh R process. All 18,750 prediction/bound values and five final random states must match the original results exactly.

Only after those checks pass does it provision `relh-sugarscape-carrella-r405-cpu2-20261019-v1` with the pinned Rocker image. The actual rate must be at most $0.003/minute with at most 15 idle minutes; an unexpected rate stops that newly owned node before fitting. The [published CPU price](https://autoresearch.sfcompute.com/) projects $0.465 for 120 execution minutes, 20 setup/export minutes, and 15 idle minutes, below the $3 limit.

The remote script verifies the payload hash and R/mgcv/Matrix versions before execution. The original full interval workflow has a 7,200-second timeout, with a 7,500-second outer limit. Its output archive includes inputs, source, logs, runtime information, and terminal status, including unsuccessful executions. The existing bounded storage collector preserves up to 50 MiB of terminal evidence.

At publication, the handoff is waiting on qualification; no historical node or fit has started. Python lint and shell syntax checks pass. Those static checks do not establish successful provisioning, scientific execution, or storage export. Actual receipts and independent result audits remain required.
