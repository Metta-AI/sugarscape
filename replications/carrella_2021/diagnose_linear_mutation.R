# Refit the complete mutation-probability point-estimation workflow on both datasets.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 5L, !file.exists(args[[5]]))
folders <- c(author = args[[1]], independent = args[[2]])
author <- read.csv(args[[3]])
author <- author[author$sample_kind == "Rejection" & author$size == 1250 & author$parameter == "pmut", ]
independent <- read.csv(args[[4]])
independent <- independent[independent$parameter == "pmut", ]
stopifnot(nrow(author) == 1250L, nrow(independent) == 1250L)
output <- args[[5]]
dir.create(output)
reports <- list()
terms_rows <- list()
prediction_rows <- list()
for (i in 1:5) {
  expected_a <- author[author$fold == i, ]
  expected_b <- independent[independent$fold == i, ]
  stopifnot(nrow(expected_a) == 250L, nrow(expected_b) == 250L,
            identical(expected_b$test_row, 1:250),
            identical(expected_a$actual, expected_b$truth),
            all(diff(expected_a$row) > 0))
  selected <- which.max((expected_a$predicted - expected_a$actual)^2)
  original_row <- expected_a$row[selected]
  for (variant in names(folders)) {
    fold <- readRDS(file.path(folders[[variant]], paste0("fold-", i, ".rds")))
    parameters <- names(fold$result$predictions)
    predictors <- setdiff(names(fold$training), parameters)
    stopifnot(length(parameters) == 5L, length(predictors) == 146L,
              nrow(fold$training) == 1000L, nrow(fold$testing) == 250L,
              max(abs(fold$testing$pmut - expected_a$actual)) < 1e-14)
    model <- lm(reformulate(predictors, response = "pmut"), data = fold$training)
    predicted <- as.numeric(predict(model, newdata = fold$testing))
    expected <- if (variant == "author") expected_a$predicted else expected_b$prediction
    stopifnot(all(is.finite(predicted)), max(abs(predicted - expected)) < 1e-10)
    terms <- predict(model, newdata = fold$testing, type = "terms")
    constant <- attr(terms, "constant")
    reconstructed <- rowSums(terms) + constant
    stopifnot(all(is.finite(reconstructed)), max(abs(predicted - reconstructed)) < 1e-10)
    squared <- (predicted - fold$testing$pmut)^2
    key <- paste(variant, i, sep = "-")
    reports[[key]] <- data.frame(variant, fold = i, observations = 250L,
      rmse = sqrt(mean(squared)), selected_test_row = selected, original_row = original_row,
      truth = fold$testing$pmut[selected], prediction = predicted[selected],
      selected_squared_error_share = squared[selected] / sum(squared),
      maximum_retained_prediction_error = max(abs(predicted - expected)),
      maximum_term_reconstruction_error = max(abs(predicted - reconstructed)),
      rank = model$rank, columns = length(coef(model)), constant = constant)
    prediction_rows[[key]] <- data.frame(variant, fold = i, test_row = 1:250,
      original_row = expected_a$row, truth = fold$testing$pmut,
      prediction = predicted, squared_error = squared)
    for (name in colnames(terms)) {
      terms_rows[[length(terms_rows)+1L]] <- data.frame(variant, fold = i,
        selected_test_row = selected, original_row = original_row, predictor = name,
        training_min = min(fold$training[[name]]), training_max = max(fold$training[[name]]),
        observed = fold$testing[[name]][selected], contribution = terms[selected, name])
    }
  }
}
write.csv(do.call(rbind, reports), file.path(output, "folds.csv"), row.names = FALSE)
write.csv(do.call(rbind, prediction_rows), file.path(output, "predictions.csv"), row.names = FALSE)
write.csv(do.call(rbind, terms_rows), file.path(output, "terms.csv"), row.names = FALSE)
writeLines(capture.output(sessionInfo()), file.path(output, "session.txt"))
print(do.call(rbind, reports))
