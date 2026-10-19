# Complete replay analysis qualification

The public `audit_replayed_gam.R INPUT_FOLDS REPLAY_RUN PAPER_TABLE NEW_OUTPUT` command validates five saved folds without refitting.
It recomputes 100 fold metrics and 25 aggregate metrics directly from 6,250 held-out predictions and their 12,500 interval bounds.
It checks finite values, column alignment, interval ordering, exported metrics, and source hashes before publishing an audit.

The complete modern-runtime replay passes with maximum scaled metric error 4.26e-15 against a 1e-12 serialization tolerance.
All 18,750 predictions and bounds remain exactly equal to the original modern results; all five final random states also match.
All five GAM scores differ from Table 8's printed precision. This is an existing discrepancy, not a new negative-replication verdict.

Two complete public-command executions produce byte-identical audit artifacts. A copied export with one performance score increased by 0.1 is rejected before an output directory is created.
Exact commands and exit codes appear in `validation.json`; the rejection log remains retained.

The historical R 4.0.5 replay is still running. This qualification establishes the analysis path, not historical results or the author's environment.
The audit compares saved inputs whose source fidelity was established separately; it does not reconstruct the original dataset itself.
