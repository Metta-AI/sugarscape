# Second Table IV checkpoint

All 25 newly completed inputs pass fresh local trajectory audits, covering 125,025 observations.
Original configurations match the paper deposit and pinned supplementary archive byte-for-byte.
The execution payload matches the qualified pilot payload. Native exits, finite metrics, consecutive ticks, and complete endpoints pass.
The 11,751,294-byte checkpoint matches its sealed SHA-256 after download from task-owned object storage.
Every regular archive member passes extraction readback.

Reconciliation uses the latest 237-input baseline-terminal inventory and explicitly rejects overlap.
No pilots or earlier checkpoints are counted again.
The combined inventory contains 262 unique original inputs and 1,194,358 observations: 107 baselines and 155 sweep inputs.
There are 293 baseline and 9,945 sweep inputs outstanding.

Table IV coverage is 152 of 500 inputs: 100 at selfishness 0.37, 51 at 0.36, and one at 0.40.
These inputs contain three extinctions and 149 final populations above 250; none equals 250.
This execution-ordered prefix is not representative of the full bin. No full-bin percentage comparison or completed-paper credit is claimed.
The existing bounded producer continues unchanged.

`audit_prefix.py` reopens the archive and runs the existing full-trajectory auditor on all 25 inputs.
`reconcile.py` verifies the original 10,500-input partition and joins the new audit to the latest retained inventory.
Both scripts use their retained evidence directory and pinned predecessor reports.
