# Complete independent bootstrap-forest estimator

All five folds over 5,000 independent simulations are complete.
The input auditor checks 3,775,000 training/test cells against the pinned simulation table and original partition.
The prediction auditor validates all 25,000 parameter predictions, interval coverage, widths, and normalized scores.
Separate Python arithmetic reproduces all five aggregate metrics within 1e-10.
No observations are excluded.

The archive retains all five folds, metrics, package versions, session details, continuation source, run log, and both auditors.
Every archive member matches its retained source bytes.
Both R auditors were rerun against extracted archived folds; their outputs match the original audits byte-for-byte.
No terminal launcher exit receipt is available; no successful process-exit claim is inferred.

The complete paired comparison now covers all 75 finite published scores across 15 estimator/size combinations.
Historical score discrepancies and independent-model stochastic fidelity remain unresolved.
This completes the estimator ensemble, not the paper replication.
