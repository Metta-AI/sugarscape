# Compare all held-out predictions on author and independent simulation statistics.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3L, !file.exists(args[[3]]))
author_dir <- args[[1]]
independent_dir <- args[[2]]
output_dir <- args[[3]]
author_metrics <- read.csv(file.path(author_dir, "metrics.csv"))
independent_metrics <- read.csv(file.path(independent_dir, "metrics.csv"))
size <- unique(author_metrics$size)
stopifnot(length(size) == 1L, size %in% c(1250L, 5000L),
          identical(author_metrics$size, independent_metrics$size),
          identical(author_metrics$parameter, independent_metrics$parameter))
parameters <- author_metrics$parameter
dir.create(output_dir, recursive = TRUE)
rows <- list()
for (i in 1:5) {
  author <- readRDS(file.path(author_dir, paste0("fold-", i, ".rds")))
  independent <- readRDS(file.path(independent_dir, paste0("fold-", i, ".rds")))
  stopifnot(identical(author$training[parameters], independent$training[parameters]),
            identical(author$testing[parameters], independent$testing[parameters]))
  for (parameter in parameters) {
    truth <- author$testing[[parameter]]
    a <- author$result$predictions[[parameter]]
    b <- independent$result$predictions[[parameter]]
    stopifnot(length(truth) == size / 5L, length(a) == size / 5L,
              length(b) == size / 5L, all(is.finite(c(truth, a, b))))
    rows[[length(rows) + 1L]] <- data.frame(
      fold = i, row = seq_along(truth), parameter = parameter, truth = truth,
      author_prediction = a, independent_prediction = b,
      author_squared_error = (a - truth)^2,
      independent_squared_error = (b - truth)^2)
  }
}
all_rows <- do.call(rbind, rows)
stopifnot(nrow(all_rows) == size * length(parameters))
connection <- gzfile(file.path(output_dir, "paired-predictions.csv.gz"), "wt")
write.csv(all_rows, connection, row.names = FALSE)
close(connection)
summaries <- lapply(parameters, function(parameter) {
  selected <- all_rows[all_rows$parameter == parameter, ]
  a <- author_metrics[author_metrics$parameter == parameter, ]
  b <- independent_metrics[independent_metrics$parameter == parameter, ]
  author_rmse <- mean(vapply(split(selected, selected$fold), function(fold) sqrt(mean(fold$author_squared_error)), numeric(1)))
  independent_rmse <- mean(vapply(split(selected, selected$fold), function(fold) sqrt(mean(fold$independent_squared_error)), numeric(1)))
  stopifnot(abs(author_rmse - a$rmse) < 1e-8,
            abs(independent_rmse - b$rmse) < 1e-8,
            identical(a$baseline_rmse, b$baseline_rmse))
  data.frame(parameter = parameter, observations = nrow(selected),
             author_rmse = author_rmse, independent_rmse = independent_rmse,
             baseline_rmse = a$baseline_rmse,
             author_performance = 1 - author_rmse / a$baseline_rmse,
             independent_performance = 1 - independent_rmse / b$baseline_rmse,
             author_largest_error_share = max(selected$author_squared_error) / sum(selected$author_squared_error),
             independent_largest_error_share = max(selected$independent_squared_error) / sum(selected$independent_squared_error))
})
write.csv(do.call(rbind, summaries), file.path(output_dir, "summary.csv"), row.names = FALSE)
# This predeclared row diagnostic applies only to the 1,250-input fold allocation.
if (size == 1250L) {
  parameter <- "wealth.reproduction"
  price <- "snap.450.mean.prices"
  outliers <- lapply(c(author = author_dir, independent = independent_dir), function(directory) {
    fold <- readRDS(file.path(directory, "fold-2.rds"))
    stopifnot(fold$testing[[parameter]][131] == 92)
    bounds <- range(fold$training[[price]])
    data.frame(truth = fold$testing[[parameter]][131],
               prediction = fold$result$predictions[[parameter]][131],
               price = fold$testing[[price]][131], training_min = bounds[1], training_max = bounds[2])
  })
  outliers <- do.call(rbind, outliers)
  outliers$variant <- rownames(outliers)
  write.csv(outliers, file.path(output_dir, "fixed-outlier-row.csv"), row.names = FALSE)
}
