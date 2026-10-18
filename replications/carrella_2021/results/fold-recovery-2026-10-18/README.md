# Exact completed-fold recovery control

The existing estimator runner saves complete folds and outgoing random-number states.
A bounded control reuses the first three folds from the independently validated 1,250-input
semiautomatic ABC run and computes the remaining two with the original estimator functions.

All five resulting fold objects are identical to the unmodified baseline, including
6,250 parameter predictions, intervals, training/test data, and outgoing random-number states.
The aggregate object and metrics are identical too.
A different seed is rejected before output creation.

The recovery wrapper requires the original method, size, seed, source directory,
and installed-package inventory. Cached folds must contain identical training/test data.
It restores each reused fold's outgoing random state and uses a fresh destination.
New completed folds are written to a pending file and atomically renamed.
Unreadable or mismatched checkpoints fail loudly; no partial results receive completion credit.
The protocol pins the unchanged author setup and original wrapper, plus every cached file.

This validates the full five-fold recovery mechanism on the declared ABC control.
It does not yet demonstrate recovered random-forest or generalized additive model results.
Those live processes were not interrupted or restarted.
When a bounded run ends, its complete folds can be preserved and recovery validated against this control;
a partial current fold still requires recomputation.
The neural-network workflow separately retains its finer observation checkpoints.

`evidence.tar.gz` preserves source, the three-fold cache, all resumed outputs,
verification, logs, protocol, and rejected wrong-seed command.
Every archived file was compared byte-for-byte with retained external evidence.
The full five-fold run completed under a 1,800-second cap.
No additional paper completion is claimed.
