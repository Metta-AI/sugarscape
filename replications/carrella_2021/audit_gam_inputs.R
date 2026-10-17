# Map each fold's largest reproduction-wealth error back to all archived inputs.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3L, !file.exists(args[[3]]))
parameters <- read.csv(file.path(args[[2]], "data/sugarscape/params_sugarscape.csv"), check.names = FALSE)
parameters[["random-seed"]] <- NULL
summaries <- read.csv(file.path(args[[2]], "data/sugarscape/sugarscape.csv"), check.names = FALSE)
summaries <- summaries[vapply(summaries, var, numeric(1)) > 0]
names(parameters) <- make.names(names(parameters), unique = TRUE, allow_ = FALSE)
names(summaries) <- make.names(names(summaries), unique = TRUE, allow_ = FALSE)
reference <- cbind(parameters, summaries)
stopifnot(nrow(reference) == 5000L, ncol(reference) == 151L)
dir.create(args[[3]], recursive = TRUE)
records <- list()
for (index in seq_len(5L)) {
  fold <- readRDS(file.path(args[[1]], paste0("fold-", index, ".rds")))
  training <- as.data.frame(fold$training)
  testing <- as.data.frame(fold$testing)
  prediction <- fold$result$predictions[, "wealth.reproduction"]
  error <- (prediction - testing$wealth.reproduction)^2
  selected <- which.max(error)
  point <- testing[selected, names(reference), drop = FALSE]
  matches <- which(apply(reference, 1L, function(row) all(row == unlist(point))))
  stopifnot(length(matches) == 1L)
  values <- as.numeric(point[1, names(summaries)])
  lower <- vapply(training[names(summaries)], min, numeric(1))
  upper <- vapply(training[names(summaries)], max, numeric(1))
  ranges <- data.frame(predictor = names(summaries), value = values, training_min = lower,
                       training_max = upper, outside = values < lower | values > upper)
  write.csv(ranges, file.path(args[[3]], paste0("fold-", index, "-ranges.csv")), row.names = FALSE)
  records[[index]] <- data.frame(fold = index, test_row = selected, source_input_zero_based = matches - 1L,
                                 truth = testing$wealth.reproduction[selected], prediction = prediction[selected],
                                 squared_error_fraction = error[selected] / sum(error),
                                 matching_fields = ncol(reference), predictors_outside_training_range = sum(ranges$outside))
}
result <- do.call(rbind, records)
write.csv(result, file.path(args[[3]], "source-mapping.csv"), row.names = FALSE)
print(result)
