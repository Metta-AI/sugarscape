# Third Table IV checkpoint

All 25 new original inputs pass fresh local trajectory audits, adding 125,025 observations.
Configurations match both the paper deposit and pinned supplementary archive byte-for-byte; execution payloads match the qualified pilots.
Native exits, finite metrics, consecutive ticks and complete endpoints pass.
The 11,878,779-byte archive matches its sealed SHA-256 after download from task-owned storage; every regular member passes readback.

Reconciliation follows the 312-input baseline checkpoint and explicitly rejects overlap.
The shared inventory has 337 unique inputs and 1,429,194 observations: 157 baselines and 180 sweep inputs.
Remaining scope is 243 baselines and 9,920 sweep inputs, plus full paper comparisons and unresolved death aggregation.

Table IV coverage is 177/500: 100 inputs at 0.37, 76 at 0.36 and one at 0.40.
There are three extinctions and 174 final populations above 250; none equals the initial population.
This execution-ordered prefix is not representative. No full-bin percentage comparison or completed-paper credit is claimed.
The existing bounded producer continues unchanged.

`audit_prefix.py` reopens the sealed archive and runs the full-trajectory auditor for each input.
`reconcile.py` uses the retained evidence directory, latest predecessor inventory and original 10,500-input partition.
