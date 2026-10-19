# Second checkpoint from the informed baseline recovery

Twenty-five disjoint original inputs pass fresh full-trajectory audits, adding 62,242 observations.
All source, configuration, seed, terminal, full-hash, finite-value, consecutive-tick and complete-endpoint gates pass.
The 5,972,514-byte archive matches its producer seal and completed object-storage export.
All six execution payload files match the frozen recovery payload byte-for-byte.

The formerly timed-out egoistic input completes in 2,093.8178 seconds, within its 3,600-second bound.
Its complete trajectory matches the prior full hash and all 4,630,527 preserved bytes from the earlier timed-out run.
It contains 5,001 observations through step 5,000, ending at population 1,352.
The earlier failure evidence remains intact. The 1,800-second limit was insufficient; recovery did not change the source, configuration, seed or trajectory.

Reconciliation against the prior 287-input inventory rejects all overlap.
The resulting inventory has 312 unique inputs and 1,304,169 observations: 157 baselines and 155 sweep inputs.
There are 243 baselines remaining. The separately reconciled third Table IV checkpoint extends sweep coverage afterward.
The existing bounded producer continues unchanged; this checkpoint does not complete the paper.

`audit_archive.py` accepts the retained evidence root, sealed archive and a new output path.
It checks the recovered input against both its previous full hash and preserved partial bytes.
`reconcile.py` uses the retained evidence directory and pinned predecessor inventory.
