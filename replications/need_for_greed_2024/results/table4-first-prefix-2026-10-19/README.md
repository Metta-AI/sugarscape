# First Table IV batch prefix

Twenty-five newly completed inputs pass fresh local trajectory audits, covering 115,402 observations.
All configurations match both the paper deposit and the pinned supplementary archive byte-for-byte.
The execution payload matches the qualified pilot payload. All native exits succeed, and all raw scalar and array metrics pass finite-value checks.
The 10,953,484-byte checkpoint was downloaded from task-owned object storage and matches its sealed SHA-256.
Every regular archive member passes extraction readback; source, configuration, runtime, full trajectory, and terminal checks pass for each input.

Reconciliation includes the two previously audited runtime pilots once each, adding 27 original inputs and 125,404 observations.
The shared inventory now contains 219 unique inputs and 1,013,026 observations: 89 baselines and 130 sweep inputs.
There are 311 baseline and 9,970 sweep inputs outstanding. Later checkpoints must deduplicate by original configuration entry.

Table IV coverage is 127 of 500 inputs: 100 at selfishness 0.37, 26 at 0.36, and one at 0.40.
These completed inputs contain three extinctions and 124 final populations above 250; none equals 250.
This execution-ordered prefix is not representative of the full bin. No percentage comparison or full-table result is claimed.
The unchanged bounded producer continues; there is no completed-paper credit.

`audit_prefix.py` reopens the checkpoint and runs the existing full-trajectory auditor on all 25 inputs.
`reconcile.py` joins the new audit, prior inventory, and qualified pilots with explicit duplicate rejection.
The scripts use their retained evidence directory, whose original configurations and prior reports remain pinned in the study.
