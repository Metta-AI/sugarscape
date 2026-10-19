# Independent bootstrap-forest folds 3 and 4

Both saved folds exactly match the original seed-zero held-out partition and pinned independent inputs.
The audit verifies 1,510,000 training/test cells and 10,000 parameter predictions.
Prediction errors, interval coverage and widths reproduce within 1e-10; separate Python arithmetic also verifies errors.
No observation is removed.

Every archived member matches retained evidence bytes.
Reauditing extracted folds reproduces both audit JSON and prediction CSV byte-for-byte.
The saved folds, audit scripts/commands, predictions, input provenance, continuation protocol and estimator runner are included.

Four of five bootstrap-forest folds are now audited: 20,000 predictions and 3,020,000 input-cell checks.
The unchanged bounded final fold remains active.
Partial folds do not establish the five-fold Table 8 score or a completed study.
