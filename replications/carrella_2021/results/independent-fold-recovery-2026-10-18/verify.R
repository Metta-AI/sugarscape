args <- commandArgs(trailingOnly = TRUE)
root <- args[[1]]
suffix <- args[[2]]
references <- c(lm = "carrella-independent-lm-002/lm-1250", rfboot = "carrella-independent-rfboot-001/rfboot-1250")
checks <- list()
for (method in names(references)) {
  original <- file.path(dirname(root), references[[method]])
  resumed <- file.path(root, paste0(method, "-resumed", suffix))
  for (name in c(paste0("fold-", 1:5, ".rds"), "complete.rds")) {
    stopifnot(identical(readRDS(file.path(original, name)), readRDS(file.path(resumed, name))))
  }
  stopifnot(identical(readLines(file.path(original, "metrics.csv")), readLines(file.path(resumed, "metrics.csv"))))
  checks[[method]] <- list(folds_identical = 5L, predictions = 6250L, random_states_identical = TRUE, aggregate_identical = TRUE, metrics_identical = TRUE, recomputed_folds = if (method == "lm") 3:5 else integer())
}
jsonlite::write_json(checks, file.path(root, paste0("verification", suffix, ".json")), pretty = TRUE, auto_unbox = TRUE)
