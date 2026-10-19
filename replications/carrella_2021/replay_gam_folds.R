# Full saved-fold replay: retain original smooths, interval draws, and RNG order.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3L, !file.exists(args[[2]]))
source_dir <- args[[1]]
output <- args[[2]]
qualify <- identical(args[[3]], "qualify")
stopifnot(args[[3]] %in% c("qualify", "sensitivity"))
dir.create(output, recursive = TRUE)
writeLines(capture.output(sessionInfo()), file.path(output, "session.txt"))
write.csv(as.data.frame(installed.packages()[, c("Package", "Version")]),
          file.path(output, "packages.csv"), row.names = FALSE)
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(0)
metrics <- list()
for (i in seq_len(5L)) {
  saved <- readRDS(file.path(source_dir, paste0("fold-", i, ".rds")))
  training <- as.data.frame(saved$training)
  testing <- as.data.frame(saved$testing)
  parameters <- names(saved$result$predictions)
  x_names <- setdiff(names(training), parameters)
  stopifnot(nrow(training) == 1000L, nrow(testing) == 250L,
            length(parameters) == 5L, length(x_names) == 146L)
  counts <- vapply(training[x_names], function(x) length(unique(x)), integer(1))
  small <- sort(names(counts)[counts < 10L])
  valid <- setdiff(x_names, small)
  small <- small[counts[small] > 1L]
  predictions <- lows <- highs <- list()
  fold_metrics <- list()
  for (parameter in parameters) {
    expression <- paste(parameter, "~", "s(", paste(valid, collapse = ")+s("), ")")
    if (length(small) > 0L) {
      expression <- paste(expression, "+", paste("s(", small, ",k=", pmin(10L, counts[small]), ")", collapse = "+"))
    }
    model <- mgcv::bam(as.formula(expression), data = training, select = TRUE, discrete = TRUE)
    current <- predict(model, newdata = testing, se = TRUE)
    residual <- residuals(model)
    draws <- lapply(as.list(current$se), function(sd) {
      rnorm(mean = 0, sd = sd, n = 10000) + sample(residual, size = 10000, replace = TRUE)
    })
    prediction <- current$fit
    low <- prediction + vapply(draws, quantile, numeric(1), probs = 0.025)
    high <- prediction + vapply(draws, quantile, numeric(1), probs = 0.975)
    stopifnot(all(is.finite(c(prediction, low, high))), all(low <= high))
    predictions[[parameter]] <- prediction
    lows[[parameter]] <- low
    highs[[parameter]] <- high
    fold_metrics[[parameter]] <- data.frame(fold = i, parameter,
      rmse = sqrt(mean((prediction - testing[[parameter]])^2)),
      baseline_rmse = sqrt(mean((mean(training[[parameter]]) - testing[[parameter]])^2)),
      coverage = mean(testing[[parameter]] >= low & testing[[parameter]] <= high),
      interval_width = mean(high - low))
    if (qualify) {
      stopifnot(identical(as.numeric(prediction), as.numeric(saved$result$predictions[[parameter]])),
                identical(as.numeric(low), as.numeric(saved$result$lows[[parameter]])),
                identical(as.numeric(high), as.numeric(saved$result$highs[[parameter]])))
    }
    cat("Completed fold", i, parameter, "\n")
    flush.console()
  }
  if (qualify) stopifnot(identical(.Random.seed, saved$random_state))
  saveRDS(list(predictions = as.data.frame(predictions), lows = as.data.frame(lows),
               highs = as.data.frame(highs), random_state = .Random.seed),
          file.path(output, paste0("fold-", i, ".rds")))
  metrics[[i]] <- do.call(rbind, fold_metrics)
}
metrics <- do.call(rbind, metrics)
write.csv(metrics, file.path(output, "fold-metrics.csv"), row.names = FALSE)
aggregate_metrics <- aggregate(cbind(rmse, baseline_rmse, coverage, interval_width) ~ parameter,
                               data = metrics, FUN = mean)
aggregate_metrics$performance <- 1 - aggregate_metrics$rmse / aggregate_metrics$baseline_rmse
write.csv(aggregate_metrics, file.path(output, "metrics.csv"), row.names = FALSE)
writeLines(if (qualify) "All 18750 predictions and interval bounds and five final random states match exactly." else
  "Full five-fold sensitivity replay completed; historical author environment remains unverified.",
  file.path(output, "complete.txt"))
