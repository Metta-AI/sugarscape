# Remaining sweep runner

This runner prepares the frozen 9,597 unassigned inputs in 19 shards.
It does not create nodes, submit commands, or authorize spending.
The separate $175 proposal remains pending. Existing assignments remain excluded, including inputs that finish after the plan was frozen.

Prepare one shard with the original archives and the latest audited inventory:

```sh
python replications/need_for_greed_2024/unassigned_sweep/prepare.py \
  /path/to/need-for-greed.zip /path/to/blueprints-selfishness.zip \
  /path/to/reconciliation.json /path/to/new-payload --batch 0
```

Preparation rejects overlaps with audited work or the existing 400-input assignment.
Every configuration must match both original archives and its frozen hash.
The original model, interpreter pins, per-input launcher and trajectory auditor remain unchanged.
`preparation.json` records every payload hash; the runner verifies these before execution.

Before any deployment, verify budget approval, the current CPU price, active assignments, and unique node/output ownership.
Reserve the entire attempt ceiling in the shared budget before dispatch, including qualification and failed attempts.
The proposal permits at most four concurrent eight-CPU workers and no automatic retries or extensions.
The dispatcher and budget ledger are not implemented here; preparation does not satisfy those launch gates.

The prepared Linux payload's entry command is `bash bootstrap.sh` from its own fresh directory.
The bootstrap imposes a 42,800-second outer timeout with 30 seconds of termination grace.
It captures Linux boot time before dependency installation; setup and both native qualification pairs consume the 41,400-second admission allowance.
Each qualification pair runs the first or last shard input through CPython and PyPy and requires byte-identical full trajectories.
Both original inputs count once. Parallel admission begins only after both pairs pass.

Each input retains its original 5,000-step horizon or natural extinction and a 1,800-second runtime limit.
Admission requires another 135 seconds for termination grace and the independent audit.
Inputs without the full allowance stay unstarted. The outer timeout also bounds checkpoint and terminal archival work.
Completed checkpoint archives remain immutable; interrupted outputs are preserved separately and receive no completion credit.
Export and idle allowances remain part of the separate global budget, not additional simulation time.

The public preparation CLI has been exercised against all 19 real shards and both original archives.
First and last shard payloads regenerate byte-for-byte; all 9,597 inputs are distinct and disjoint from the 512-input audited inventory.
Python lint and shell syntax checks pass. The new Linux bootstrap, deadline handling, and native qualification gates have not been executed.
Do not treat preparation evidence as runtime qualification or paper-replication credit.
