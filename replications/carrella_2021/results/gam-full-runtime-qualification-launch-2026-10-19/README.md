# Full GAM runtime qualification launch

The earlier R 4.0.5 controls omit prediction intervals and cover individual folds. This launch qualifies a complete saved-fold replay before extending the historical-runtime sensitivity experiment.

`replay_gam_folds.R SAVED_FOLDS NEW_OUTPUT qualify|sensitivity` uses the original smooth construction and `mgcv::bam` options. It preserves the original 10,000 normal/residual draws per test observation, parameter order, fold order, and seed zero. All five folds and all five parameters remain included. Saved fold inputs deliberately hold floating-point parsing constant; this is not a complete historical parser reconstruction.

Qualification requires exact agreement for 6,250 predictions, 6,250 lower bounds, 6,250 upper bounds, and five fold-ending random states. It uses real original workflow outputs, not synthetic fixtures. Aggregation averages fold RMSE, coverage, and widths and retains the training-mean baseline. A mismatch fails the process rather than receiving completion credit.

The local launch uses one CPU thread and a 1,800-second process timeout. The command, frozen script hash, and all five input hashes are retained. This is a launch record, not a completed qualification or a new paper result. No historical-runtime job has started. The original author-environment uncertainty remains explicit even if a plausible older runtime passes.
