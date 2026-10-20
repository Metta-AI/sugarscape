# Complete Rule M/Rule M cohort launch

Forty-eight previously unstarted inputs, repetitions02–49, are assigned to the local bounded dispatcher.
Together with the two audited first-batch inputs, these target all fifty repetitions of the released-code Rule M/Rule M pairing.
Session84521 owns the dispatcher: two workers,600seconds per input plus30seconds wrapper allowance,7,200-second admission horizon,1GiB Java heap per worker.
The runner requires2GiB free storage before each input and limits each input's output to50MiB.

`assign_ensemble.py` validates the frozen manifest and audited remaining rows, excludes explicit reservations, and emits a hash-pinned assignment.
The generated48-input assignment matches the separately prepared assignment byte for byte. Before launch, every selected row was checked against the newly audited remaining manifest.
The first dispatcher batch and archive readback passed before this cohort began. `launch-gate.json` pins those checks.

These48 inputs are now reserved for this dispatcher. Future cloud assignments must exclude its `execution-plan.json` input IDs, even before all inputs finish.
Successful child exits still require independent full-trajectory audits before coverage credit. Partial and unstarted work must remain explicit.
No completed cohort or paper replication is claimed by this launch.
