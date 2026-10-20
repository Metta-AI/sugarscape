# Second initializer attempt: bounded boot command

The prior 900-second queue attempt remains stopped and retained. No simulation ran in that attempt.
This second attempt separates queue waiting from paid execution. The same task-owned H100 was freshly verified stopped with no active command.
A boot command is registered as `cmd-mcadf`; the provider confirms `pending_wake` and a maximum duration of 60 minutes.
The node is now queued with a four-hour hold. The boot command starts automatically when the node is ready and does not carry into a later wake.

The exact prepared payload is downloaded from a commit-pinned public repository URL and SHA-256 checked before extraction or execution.
A fresh local download confirms all 66,444 bytes. The native protocol and its nine variants are unchanged.
Released and combined baseline hash gates remain mandatory. Neither this registration nor queue status establishes native completion.

The initial duration value `3600` was interpreted as minutes and rejected before registration. The explicit `1h` value succeeded; both receipts remain retained.
Registration alone did not wake the stopped node. A create request was rejected because the node already existed; a bounded `run /bin/true` wake request then queued it.
The harmless wake request does not run a model. Provider state confirms only the registered model command is pending wake.

A local readiness watcher permits four hours queued and at most 900 seconds in provisioning states.
The provider enforces the 60-minute execution limit; the inner timeout is 3,570 seconds plus a 30-second kill grace.
The task-local collector permits one terminal archive of at most 256 MiB and a 900-second export allowance.
No automatic model retries are enabled.

A new $10 reservation conservatively retains the earlier $10 reservation pending reconciliation.
At $0.084/minute, 900 seconds provisioning, 3,600 execution, 900 export, and 900 idle total $8.82; queue waiting is separate.
The continuation ledger now reserves $48 and leaves $52 unreserved.
Native compilation, full-world/transition audits, and final storage readback remain pending.
