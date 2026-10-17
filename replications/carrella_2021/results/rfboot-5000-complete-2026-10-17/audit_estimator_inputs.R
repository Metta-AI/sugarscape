# Reconstruct all five original folds and audit complete estimator results.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3L, !file.exists(args[[3]]))
source_dir <- args[[1]]
run <- args[[2]]
output <- args[[3]]
parameters <- read.csv(file.path(source_dir, "data/sugarscape/params_sugarscape.csv"), check.names = FALSE)
parameters[["random-seed"]] <- NULL
summaries <- read.csv(file.path(source_dir, "data/sugarscape/sugarscape.csv"), check.names = FALSE)
summaries <- summaries[vapply(summaries, var, numeric(1)) > 0]
names(parameters) <- make.names(names(parameters), unique = TRUE, allow_ = FALSE)
names(summaries) <- make.names(names(summaries), unique = TRUE, allow_ = FALSE)
data <- cbind(parameters, summaries)
metrics <- read.csv(file.path(run, "metrics.csv"))
method <- unique(metrics$method)
stopifnot(nrow(data) == 5000, ncol(data) == 151, length(method) == 1,
          method %in% c("neuralnet", "rfboot"), all(metrics$size == 5000), all(metrics$seed == 0))
key <- if (method == "neuralnet") "medians" else "predictions"
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(0)
permutation <- sample(seq_len(5000))
errors <- coverage <- width <- baseline <- matrix(NA_real_, 5, 5)
for (fold in seq_len(5)) {
  x <- readRDS(file.path(run, paste0("fold-", fold, ".rds")))
  ids <- sort(permutation[((fold - 1) * 1000 + 1):(fold * 1000)])
  expected_test <- data[ids, ]
  expected_train <- data[-ids, ]
  rownames(expected_test) <- rownames(expected_train) <- NULL
  stopifnot(identical(x$testing, expected_test), identical(x$training, expected_train))
  pred <- as.matrix(x$result[[key]])
  truth <- as.matrix(expected_test[names(parameters)])
  low <- as.matrix(x$result$lows)
  high <- as.matrix(x$result$highs)
  stopifnot(identical(dim(pred), c(1000L, 5L)), identical(dim(low), dim(pred)),
            identical(dim(high), dim(pred)), all(is.finite(c(pred, truth, low, high))), all(low <= high))
  errors[fold, ] <- sqrt(colMeans((pred - truth)^2))
  coverage[fold, ] <- colMeans(truth >= low & truth <= high)
  width[fold, ] <- colMeans(high - low)
  baseline[fold, ] <- sqrt(colMeans(sweep(truth, 2, colMeans(as.matrix(expected_train[names(parameters)])), "-")^2))
  stopifnot(max(abs(errors[fold, ] - x$result$errors)) < 1e-10,
            max(abs(coverage[fold, ] - x$result$contained)) < 1e-10,
            max(abs(width[fold, ] - x$result$interval_size)) < 1e-10)
}
complete <- readRDS(file.path(run, "complete.rds"))
performance <- 1 - colMeans(errors) / colMeans(baseline)
stopifnot(identical(metrics$parameter, names(parameters)),
          max(abs(colMeans(errors) - complete$errors)) < 1e-10,
          max(abs(colMeans(coverage) - complete$contained)) < 1e-10,
          max(abs(colMeans(width) - complete$interval_size)) < 1e-10,
          max(abs(colMeans(errors) - metrics$rmse)) < 1e-10,
          max(abs(colMeans(baseline) - metrics$baseline_rmse)) < 1e-10,
          max(abs(performance - metrics$performance)) < 1e-10,
          max(abs(colMeans(coverage) - metrics$coverage)) < 1e-10,
          max(abs(colMeans(width) - metrics$interval_width)) < 1e-10)
published <- if (method == "neuralnet") c(.588, .502, .510, .519, .736) else c(.474, .538, .448, .465, .797)
comparison <- data.frame(parameter = names(parameters), rmse = colMeans(errors),
  baseline_rmse = colMeans(baseline), performance, published,
  matches_printed_precision = round(performance, 3) == published,
  coverage = colMeans(coverage), interval_width = colMeans(width))
report <- list(method = method, folds = 5, held_out_rows = 5000,
  predictions_audited = 25000, input_cells_checked = 3775000,
  exact_original_fold_alignment = TRUE, comparison = comparison,
  scope = "Complete original-data estimator workflow. Discrepancies are unresolved, not validated negatives. No whole-paper credit.")
writeLines(jsonlite::toJSON(report, pretty = TRUE, auto_unbox = TRUE, digits = 17), output)
print(report)
