# Audit complete saved-fold replays without refitting the statistical model.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 4L, !file.exists(args[[4]]))
inputs <- args[[1]]
run <- args[[2]]
paper_path <- args[[3]]
output <- args[[4]]
stopifnot(file.exists(file.path(run, "complete.txt")))
reported <- read.csv(file.path(run, "metrics.csv"))
reported_folds <- read.csv(file.path(run, "fold-metrics.csv"))
metrics <- changes <- list()
hashes <- list()
for (fold in seq_len(5L)) {
  input_path <- file.path(inputs, paste0("fold-", fold, ".rds"))
  replay_path <- file.path(run, paste0("fold-", fold, ".rds"))
  saved <- readRDS(input_path)
  replay <- readRDS(replay_path)
  parameters <- names(saved$result$predictions)
  stopifnot(length(parameters) == 5L, nrow(saved$training) == 1000L,
            nrow(saved$testing) == 250L, ncol(saved$training) == 151L,
            ncol(saved$testing) == 151L, is.integer(replay$random_state),
            length(replay$random_state) == 626L)
  values <- lapply(c("predictions", "lows", "highs"), function(key) {
    stopifnot(identical(names(replay[[key]]), parameters))
    m <- as.matrix(replay[[key]])
    stopifnot(identical(dim(m), c(250L, 5L)), all(is.finite(m)))
    m
  })
  prediction <- values[[1]]
  low <- values[[2]]
  high <- values[[3]]
  truth <- as.matrix(saved$testing[parameters])
  training <- as.matrix(saved$training[parameters])
  stopifnot(all(is.finite(c(truth, training))), all(low <= high))
  metrics[[fold]] <- data.frame(fold, parameter = parameters,
    rmse = sqrt(colMeans((prediction - truth)^2)),
    baseline_rmse = sqrt(colMeans(sweep(truth, 2L, colMeans(training), "-")^2)),
    coverage = colMeans(truth >= low & truth <= high),
    interval_width = colMeans(high - low))
  changes[[fold]] <- do.call(rbind, lapply(seq_along(values), function(j) {
    key <- c("predictions", "lows", "highs")[[j]]
    original <- as.matrix(saved$result[[key]])
    stopifnot(identical(colnames(original), parameters), identical(dim(original), dim(values[[j]])),
              all(is.finite(original)))
    delta <- values[[j]] - original
    data.frame(fold, quantity = key, parameter = parameters,
      changed_values = colSums(delta != 0), max_absolute_change = apply(abs(delta), 2L, max),
      root_mean_squared_change = sqrt(colMeans(delta^2)),
      final_rng_state_identical = identical(replay$random_state, saved$random_state))
  }))
  hashes[[fold]] <- list(fold = fold, input_sha256 = digest::digest(file = input_path, algo = "sha256"),
                        replay_sha256 = digest::digest(file = replay_path, algo = "sha256"))
}
metrics <- do.call(rbind, metrics)
changes <- do.call(rbind, changes)
aggregate_metrics <- aggregate(cbind(rmse, baseline_rmse, coverage, interval_width) ~ parameter,
                               data = metrics, FUN = mean)
aggregate_metrics$performance <- 1 - aggregate_metrics$rmse / aggregate_metrics$baseline_rmse
stopifnot(nrow(reported) == 5L, !anyDuplicated(reported$parameter),
          setequal(reported$parameter, aggregate_metrics$parameter), nrow(reported_folds) == 25L)
reported <- reported[match(aggregate_metrics$parameter, reported$parameter), ]
fold_keys <- paste(metrics$fold, metrics$parameter)
reported_keys <- paste(reported_folds$fold, reported_folds$parameter)
stopifnot(!anyDuplicated(reported_keys), setequal(fold_keys, reported_keys))
reported_folds <- reported_folds[match(fold_keys, reported_keys), ]
columns <- c("rmse", "baseline_rmse", "coverage", "interval_width")
expected <- c(as.matrix(metrics[columns]), as.matrix(aggregate_metrics[c(columns, "performance")]))
actual <- c(as.matrix(reported_folds[columns]), as.matrix(reported[c(columns, "performance")]))
scaled_error <- abs(actual - expected) / pmax(1, abs(expected))
stopifnot(all(is.finite(scaled_error)), max(scaled_error) < 1e-12)
paper <- jsonlite::fromJSON(paper_path, simplifyVector = FALSE)
column <- match("GAM", unlist(paper$columns))
rows <- Filter(function(row) identical(row[[1]], "Sugarscape ABM 1,250"), paper$rows)
stopifnot(length(rows) == 5L)
published <- setNames(vapply(rows, function(row) as.numeric(row[[column]]), numeric(1)),
                      vapply(rows, function(row) row[[2]], character(1)))
stopifnot(setequal(names(published), aggregate_metrics$parameter))
aggregate_metrics$published <- unname(published[aggregate_metrics$parameter])
aggregate_metrics$matches_printed_precision <- round(aggregate_metrics$performance, 3L) == aggregate_metrics$published
report <- list(folds = 5L, held_out_rows = 1250L, predictions_and_bounds_checked = 18750L,
  metric_values_checked = length(expected), maximum_scaled_metric_error = max(scaled_error),
  metric_tolerance = 1e-12, changed_prediction_and_bound_values = sum(changes$changed_values),
  final_rng_states_identical = all(changes$final_rng_state_identical),
  published_matches = sum(aggregate_metrics$matches_printed_precision),
  paper_table_sha256 = digest::digest(file = paper_path, algo = "sha256"),
  hashes = hashes,
  reported_metrics_sha256 = digest::digest(file = file.path(run, "metrics.csv"), algo = "sha256"),
  reported_fold_metrics_sha256 = digest::digest(file = file.path(run, "fold-metrics.csv"), algo = "sha256"),
  comparison = aggregate_metrics,
  scope = "Complete saved-fold arithmetic and runtime sensitivity audit. Input source fidelity is established separately. Historical author environment and random states remain unknown; discrepancies are not validated negatives.")
dir.create(output, recursive = TRUE)
write.csv(metrics, file.path(output, "fold-metrics.csv"), row.names = FALSE)
write.csv(aggregate_metrics, file.path(output, "metrics.csv"), row.names = FALSE)
write.csv(changes, file.path(output, "modern-runtime-differences.csv"), row.names = FALSE)
jsonlite::write_json(report, file.path(output, "audit.json"), auto_unbox = TRUE, pretty = TRUE, digits = 17)
print(report)
