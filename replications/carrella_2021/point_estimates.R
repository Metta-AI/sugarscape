# Reproduce the linear-regression column of Table 8 from archived simulation data.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2L)
source_dir <- args[[1]]
output_dir <- args[[2]]
stopifnot(!file.exists(output_dir))
dir.create(output_dir, recursive = TRUE)
parameters <- read.csv(file.path(source_dir, "params_sugarscape.csv"), check.names = FALSE)
parameters[["random-seed"]] <- NULL
summaries <- read.csv(file.path(source_dir, "sugarscape.csv"), check.names = FALSE)
summaries <- summaries[vapply(summaries, var, numeric(1)) > 0]
stopifnot(nrow(parameters) == 5000L, ncol(parameters) == 5L, ncol(summaries) == 146L)
names(parameters) <- make.names(names(parameters), unique = TRUE, allow_ = FALSE)
names(summaries) <- make.names(names(summaries), unique = TRUE, allow_ = FALSE)
data <- cbind(parameters, summaries)
results <- list()
predictions <- list()
for (sample_kind in c("Rounding", "Rejection")) {
  for (size in c(1250L, 5000L)) {
    current <- data[seq_len(size), ]
    RNGkind(kind = "Mersenne-Twister", normal.kind = "Inversion", sample.kind = sample_kind)
    set.seed(0)
    order <- sample(seq_len(size))
    groups <- split(order, rep(seq_len(5L), each = size / 5L))
    for (parameter in names(parameters)) {
      errors <- numeric(5L)
      baseline_errors <- numeric(5L)
      for (fold in seq_len(5L)) {
        # The author filters row membership, preserving original row order.
        testing_indices <- which(seq_len(size) %in% groups[[fold]])
        training <- current[-testing_indices, ]
        testing <- current[testing_indices, ]
        fitted <- lm(reformulate(names(summaries), response = parameter), data = training)
        predicted <- predict(fitted, newdata = testing)
        actual <- testing[[parameter]]
        baseline <- mean(training[[parameter]])
        stopifnot(all(is.finite(predicted)))
        errors[[fold]] <- sqrt(mean((predicted - actual)^2))
        baseline_errors[[fold]] <- sqrt(mean((baseline - actual)^2))
        predictions[[length(predictions) + 1L]] <- data.frame(
          sample_kind, size, parameter, fold, row = testing_indices,
          actual, predicted, baseline
        )
      }
      results[[length(results) + 1L]] <- data.frame(
        sample_kind, size, parameter, rmse = mean(errors), baseline_rmse = mean(baseline_errors),
        performance = 1 - mean(errors) / mean(baseline_errors)
      )
    }
  }
}
write.csv(do.call(rbind, results), file.path(output_dir, "performance.csv"), row.names = FALSE)
write.csv(do.call(rbind, predictions), file.path(output_dir, "predictions.csv"), row.names = FALSE)
writeLines(capture.output(sessionInfo()), file.path(output_dir, "session.txt"))
print(do.call(rbind, results))
