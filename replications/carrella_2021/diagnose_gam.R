# Paired runtime diagnostic of point predictions, not a replacement estimator study.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2L, !file.exists(args[[2]]))
fold <- readRDS(args[[1]])
training <- as.data.frame(fold$training)
testing <- as.data.frame(fold$testing)
parameter_names <- colnames(fold$result$predictions)
x_names <- setdiff(names(training), parameter_names)
stopifnot(length(parameter_names) == 5L, length(x_names) == 146L)
dir.create(args[[2]], recursive = TRUE)
writeLines(capture.output(sessionInfo()), file.path(args[[2]], "session.txt"))
writeLines(as.character(packageVersion("mgcv")), file.path(args[[2]], "mgcv-version.txt"))
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(0)
counts <- vapply(training[x_names], function(x) length(unique(x)), integer(1))
small <- sort(names(counts)[counts < 10L])
valid <- setdiff(x_names, small)
small <- small[counts[small] > 1L]
metrics <- list()
for (parameter in parameter_names) {
  # Same smooth construction and fitting options as the pinned loess_fit function.
  expression <- paste(parameter, "~", "s(", paste(valid, collapse = ")+s("), ")")
  if (length(small) > 0L) {
    expression <- paste(expression, "+", paste("s(", small, ",k=", pmin(10L, counts[small]), ")", collapse = "+"))
  }
  model <- mgcv::bam(as.formula(expression), data = training, select = TRUE, discrete = TRUE)
  prediction <- as.numeric(predict(model, newdata = testing))
  stopifnot(length(prediction) == nrow(testing), all(is.finite(prediction)))
  write.csv(data.frame(truth = testing[[parameter]], prediction),
            file.path(args[[2]], paste0(parameter, ".csv")), row.names = FALSE)
  saveRDS(list(formula = expression, coefficients = coef(model), smoothing = model$sp,
               random_state = .Random.seed), file.path(args[[2]], paste0(parameter, ".rds")))
  metrics[[parameter]] <- data.frame(parameter, rmse = sqrt(mean((prediction - testing[[parameter]])^2)))
  cat("Completed", parameter, "\n")
  flush.console()
}
write.csv(do.call(rbind, metrics), file.path(args[[2]], "metrics.csv"), row.names = FALSE)
