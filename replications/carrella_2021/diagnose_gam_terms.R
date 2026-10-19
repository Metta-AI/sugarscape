# Decompose the retained outlier without changing its inputs or fitting formula.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 4L, !file.exists(args[[4]]))
fold <- readRDS(args[[1]])
reference <- readRDS(args[[2]])
variant <- args[[3]]
output <- args[[4]]
dir.create(output, recursive = TRUE)
parameter <- "wealth.reproduction"
parameters <- names(fold$result$predictions)
predictors <- setdiff(names(fold$training), parameters)
counts <- vapply(fold$training[predictors], function(x) length(unique(x)), integer(1))
small <- sort(names(counts)[counts < 10L])
valid <- setdiff(predictors, small)
small <- small[counts[small] > 1L]
expression <- paste(parameter, "~", "s(", paste(valid, collapse = ")+s("), ")")
if (length(small) > 0L) {
  expression <- paste(expression, "+", paste("s(", small, ",k=", pmin(10L, counts[small]), ")", collapse = "+"))
}
stopifnot(identical(expression, reference$formula))
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(0)
model <- mgcv::bam(as.formula(expression), data = fold$training, select = TRUE, discrete = TRUE)
prediction <- as.numeric(predict(model, newdata = fold$testing))
retained <- fold$result$predictions[[parameter]]
prediction_delta <- max(abs(prediction - retained))
stopifnot(prediction_delta < 1e-8)
terms <- predict(model, newdata = fold$testing, type = "terms")
intercept <- unname(coef(model)["(Intercept)"])
stopifnot(is.finite(intercept), nrow(terms) == length(prediction))
reconstructed <- rowSums(terms) + intercept
stopifnot(max(abs(prediction - reconstructed)) < 1e-8)
selected <- which.max((retained - fold$testing[[parameter]])^2)
stopifnot(selected == 131L, fold$testing[[parameter]][selected] == 92)
design <- predict(model, newdata = fold$testing[selected, , drop = FALSE], type = "lpmatrix")
stopifnot(abs(as.numeric(design %*% coef(model)) - prediction[selected]) < 1e-8)
rows <- lapply(seq_along(model$smooth), function(i) {
  smooth <- model$smooth[[i]]
  stopifnot(length(smooth$term) == 1L, smooth$label %in% colnames(terms))
  name <- smooth$term
  observed <- fold$testing[[name]][selected]
  bounds <- range(fold$training[[name]])
  data.frame(predictor = name, term = smooth$label, contribution = terms[selected, smooth$label],
             value = observed, training_min = bounds[1], training_max = bounds[2],
             outside_training_range = observed < bounds[1] || observed > bounds[2],
             effective_degrees_freedom = sum(model$edf[smooth$first.para:smooth$last.para]))
})
contributions <- do.call(rbind, rows)
contributions <- contributions[order(abs(contributions$contribution), decreasing = TRUE), ]
write.csv(contributions, file.path(output, "contributions.csv"), row.names = FALSE)
write.csv(data.frame(truth = fold$testing[[parameter]], retained, prediction, reconstructed),
          file.path(output, "predictions.csv"), row.names = FALSE)
saveRDS(model, file.path(output, "model.rds"))
report <- list(variant = variant, parameter = parameter, observations = length(prediction),
               selected_test_row = selected, selected_truth = 92, selected_prediction = prediction[selected],
               intercept = intercept,
               maximum_retained_prediction_difference = prediction_delta,
               maximum_term_reconstruction_difference = max(abs(prediction - reconstructed)),
               smooth_terms = nrow(contributions), coefficients = length(coef(model)),
               effective_degrees_freedom = sum(model$edf), mgcv = as.character(packageVersion("mgcv")),
               scope = "Point-fit decomposition diagnostic; unchanged inputs and formula. No data exclusion, refitting control, or paper-level verdict.")
writeLines(jsonlite::toJSON(report, pretty = TRUE, auto_unbox = TRUE, digits = 17), file.path(output, "audit.json"))
writeLines(capture.output(sessionInfo()), file.path(output, "session.txt"))
print(report)
print(head(contributions, 10))
