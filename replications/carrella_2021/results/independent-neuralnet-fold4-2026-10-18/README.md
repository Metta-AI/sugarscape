# Independent neural-network fold 4

The completed fourth fold reproduces its seed-zero train/test partition against provenance-verified independent simulation inputs.
All 755,000 input cells and 5,000 held-out predictions are checked; prediction error, coverage, and interval widths reconstruct within 1e-10.
The auditor uses the fourth contiguous segment of the original seed-zero permutation, preserving the original split design.

The raw fold, predictions, audit source, commands, input provenance, run protocol, checkpointed launcher, and runtime inventory are retained.
Every archive member passes hash readback. The producer remains running on the fifth fold and was not restarted.

Four of five independent folds are now audited: 20,000 predictions and 3,020,000 input-cell checks.
These partial results do not establish the aggregate estimator score, reproduce Table 8, or complete the paper.
