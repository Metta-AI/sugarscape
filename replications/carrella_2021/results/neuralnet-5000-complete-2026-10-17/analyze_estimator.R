# Independently audit held-out predictions from the complete original-estimator workflow.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2L, !file.exists(args[[2]]))
input <- args[[1]]
output <- args[[2]]
metrics <- read.csv(file.path(input, "metrics.csv"))
method <- unique(metrics$method)
stopifnot(length(method) == 1L)
key <- if (method %in% c("rejection", "sabc_4d", "sabc_1d", "loclin", "neuralnet")) "medians" else "predictions"
folds <- lapply(1:5, function(i) readRDS(file.path(input, paste0("fold-", i, ".rds"))))
rows <- lapply(seq_along(folds), function(i) {
  fold <- folds[[i]]
  prediction <- as.matrix(fold$result[[key]])
  truth <- as.matrix(fold$testing[colnames(prediction)])
  low <- as.matrix(fold$result$lows)
  high <- as.matrix(fold$result$highs)
  stopifnot(identical(dim(prediction), dim(truth)), identical(dim(low), dim(truth)),
            identical(dim(high), dim(truth)), all(is.finite(c(prediction, truth, low, high))),
            all(low <= high), nrow(fold$training) + nrow(truth) == unique(metrics$size))
  data.frame(fold = i, test_row = rep(seq_len(nrow(truth)), ncol(truth)),
             parameter = rep(colnames(truth), each = nrow(truth)), truth = as.vector(truth),
             prediction = as.vector(prediction), low = as.vector(low), high = as.vector(high))
})
predictions <- do.call(rbind, rows)
checked <- do.call(rbind, lapply(metrics$parameter, function(parameter) {
  values <- predictions[predictions$parameter == parameter, ]
  rmse <- mean(vapply(split(values, values$fold), function(f) sqrt(mean((f$prediction - f$truth)^2)), numeric(1)))
  coverage <- mean(values$truth >= values$low & values$truth <= values$high)
  width <- mean(values$high - values$low)
  recorded <- metrics[metrics$parameter == parameter, ]
  stopifnot(nrow(values) == recorded$size, all.equal(rmse, recorded$rmse),
            all.equal(coverage, recorded$coverage), all.equal(width, recorded$interval_width),
            all.equal(1 - rmse / recorded$baseline_rmse, recorded$performance))
  data.frame(parameter, observations = nrow(values), rmse, coverage, interval_width = width)
}))
dir.create(output, recursive = TRUE)
write.csv(predictions, file.path(output, "predictions.csv"), row.names = FALSE)
write.csv(checked, file.path(output, "validated_metrics.csv"), row.names = FALSE)
cat("Validated", nrow(predictions), "held-out parameter predictions across five folds\n")
