# Unassigned sweep runner preparation

The [public preparation CLI](../../unassigned_sweep) generated all 19 frozen shards from both original deposited archives.
All 9,597 inputs are unique, disjoint from the 512-input audited inventory, and excluded from the existing 400-input assignment.
All 9,711 generated payload-file hashes verify. First and last shard payloads independently regenerate byte-for-byte, including their preparation receipts.
The validation pins the final three implementation files. Earlier draft preparation remains preserved externally without being substituted for this final-version evidence.

The new runner starts its admission clock before setup, uses a hard outer timeout, and requires complete CPython/PyPy qualification trajectories before parallel admission.
Per-input admission reserves termination and audit time. Payload hashes are verified before execution.
Existing simulations, their runners, and historical evidence remain unchanged.

Checks: all 19 real preparation CLI commands, two exact repeats, Ruff, and `bash -n`.
The new Linux bootstrap, clock/deadline behavior, and native qualification flow remain unexecuted.
Global dispatch/budget reservation is not implemented; budget approval and launch gates remain required.
No node was allocated and no new simulation ran. This adds no paper-completion credit.
