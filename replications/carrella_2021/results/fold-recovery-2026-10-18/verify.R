root <- "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-fold-resume-001"
baseline <- "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-independent-sabc1d-001/sabc_1d-1250"
for (name in c(paste0("fold-", 1:5, ".rds"), "complete.rds")) {
  stopifnot(identical(readRDS(file.path(baseline, name)), readRDS(file.path(root, "resumed", name))))
}
stopifnot(identical(readLines(file.path(baseline, "metrics.csv")), readLines(file.path(root, "resumed/metrics.csv"))))
jsonlite::write_json(list(folds_identical = 5L, predictions_compared = 6250L,
                         random_states_identical = TRUE, aggregate_identical = TRUE,
                         metrics_identical = TRUE, reused_folds = 1:3, recomputed_folds = 4:5,
                         completed_study = FALSE), file.path(root, "verification.json"), pretty = TRUE, auto_unbox = TRUE)
