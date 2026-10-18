# Verify saved estimator folds against the complete independent input table.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3L, !file.exists(args[[3]]))
source_dir <- args[[1]]
run <- args[[2]]
provenance <- jsonlite::read_json(file.path(source_dir, "provenance.json"))
stopifnot(provenance$kind == "independent_simulation_estimator_inputs",
          provenance$rows == 5000L)
for (name in names(provenance$files_sha256)) {
  stopifnot(digest::digest(file = file.path(source_dir, name), algo = "sha256") ==
              provenance$files_sha256[[name]])
}
parameters <- read.csv(file.path(source_dir, "data/sugarscape/params_sugarscape.csv"), check.names = FALSE)
parameters[["random-seed"]] <- NULL
summaries <- read.csv(file.path(source_dir, "data/sugarscape/sugarscape.csv"), check.names = FALSE)
summaries <- summaries[vapply(summaries, var, numeric(1)) > 0]
names(parameters) <- make.names(names(parameters), unique = TRUE, allow_ = FALSE)
names(summaries) <- make.names(names(summaries), unique = TRUE, allow_ = FALSE)
metrics <- read.csv(file.path(run, "metrics.csv"))
size <- unique(metrics$size)
stopifnot(length(size) == 1L, size %in% c(1250L, 5000L),
          nrow(metrics) == 5L, all(metrics$seed == 0L),
          identical(metrics$parameter, names(parameters)), ncol(summaries) == 146L)
data <- cbind(parameters, summaries)[seq_len(size), ]
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(0)
permutation <- sample(seq_len(size))
baseline <- matrix(NA_real_, 5L, 5L)
indices <- list()
for (fold in seq_len(5L)) {
  saved <- readRDS(file.path(run, paste0("fold-", fold, ".rds")))
  ids <- sort(permutation[seq.int((fold - 1L) * size / 5L + 1L, fold * size / 5L)])
  expected_test <- data[ids, ]
  expected_train <- data[-ids, ]
  rownames(expected_test) <- rownames(expected_train) <- NULL
  stopifnot(identical(saved$testing, expected_test),
            identical(saved$training, expected_train))
  truth <- as.matrix(expected_test[names(parameters)])
  baseline[fold, ] <- sqrt(colMeans(sweep(truth, 2L,
      colMeans(as.matrix(expected_train[names(parameters)])), "-")^2))
  indices[[fold]] <- data.frame(fold, original_row = ids - 1L)
}
stopifnot(max(abs(colMeans(baseline) - metrics$baseline_rmse)) < 1e-10)
dir.create(args[[3]], recursive = TRUE)
write.csv(do.call(rbind, indices), file.path(args[[3]], "held-out-row-index.csv"), row.names = FALSE)
jsonlite::write_json(list(
  independent_summary_sha256 = provenance$files_sha256[["data/sugarscape/sugarscape.csv"]],
  size = size, folds = 5L, predictors = 146L, parameters = 5L,
  exact_training_and_testing_cells_verified = size * 151L * 5L,
  maximum_baseline_rmse_error = max(abs(colMeans(baseline) - metrics$baseline_rmse)),
  scope = "Exact input provenance and fold allocation; held-out predictions require analyze_estimator.R separately."
), file.path(args[[3]], "audit.json"), auto_unbox = TRUE, pretty = TRUE)
cat("Verified independent input provenance and all five folds for", size, "inputs\n")
