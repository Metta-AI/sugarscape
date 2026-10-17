# Run one complete five-fold estimation workflow using the pinned author's functions.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 5L)
source_dir <- args[[1]]
method <- args[[2]]
size <- as.integer(args[[3]])
seed <- as.integer(args[[4]])
output_dir <- args[[5]]
stopifnot(size %in% c(1250L, 5000L), !file.exists(output_dir))
dir.create(output_dir, recursive = TRUE)
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(seed)
source(file.path(source_dir, "setup.R"))
parameters <- as.data.frame(readr::read_csv(file.path(source_dir, "data/sugarscape/params_sugarscape.csv"), show_col_types = FALSE))
parameters[["random-seed"]] <- NULL
summaries <- as.data.frame(readr::read_csv(file.path(source_dir, "data/sugarscape/sugarscape.csv"), show_col_types = FALSE))
summaries <- summaries[vapply(summaries, var, numeric(1)) > 0]
names(parameters) <- make.names(names(parameters), unique = TRUE, allow_ = FALSE)
names(summaries) <- make.names(names(summaries), unique = TRUE, allow_ = FALSE)
stopifnot(nrow(parameters) == 5000L, ncol(parameters) == 5L, ncol(summaries) == 146L)
total_data <- cbind(parameters, summaries)[seq_len(size), ]
parameter_names <- names(parameters)
settings <- switch(method,
  rejection = list(fitting = abc_testing, method = "rejection", semiauto = FALSE),
  sabc_4d = list(fitting = abc_testing, method = "rejection", semiauto = TRUE),
  sabc_1d = list(fitting = abc_testing, method = "rejection", semiauto = TRUE,
                 satr = list(function(x) outer(x, Y = 1, "^"))),
  loclin = list(fitting = abc_testing, method = "loclinear", semiauto = FALSE, hcorr = TRUE),
  neuralnet = list(fitting = abc_testing, method = "neuralnet", semiauto = FALSE, hcorr = TRUE),
  lm = list(fitting = linear_regression_fit, x_names = names(summaries), degree = 1),
  rf = list(fitting = randomForest_fit, x_names = names(summaries)),
  rfboot = list(fitting = randomForest_caretboot_fit, x_names = names(summaries)),
  loess = list(fitting = loess_fit, x_names = names(summaries), bam = TRUE),
  stop("Unknown estimator")
)
fitting <- settings$fitting
settings$fitting <- NULL
fold_index <- 0L
# This callback retains complete fold output; the original cross-validation function
# still chooses all partitions and computes the aggregate metrics.
record_fold <- function(training_set, testing_set, parameter_colnames, ...) {
  fold_index <<- fold_index + 1L
  fold_result <- do.call(fitting, c(list(training_set = training_set, testing_set = testing_set,
                                       parameter_colnames = parameter_colnames), settings))
  saveRDS(list(training = training_set, testing = testing_set, result = fold_result,
               random_state = .Random.seed), file.path(output_dir, paste0("fold-", fold_index, ".rds")))
  cat("Completed fold", fold_index, "for", method, size, "\n")
  flush.console()
  fold_result
}
write.csv(as.data.frame(installed.packages()[, c("Package", "Version")]),
          file.path(output_dir, "packages.csv"), row.names = FALSE)
writeLines(capture.output(sessionInfo()), file.path(output_dir, "session.txt"))
writeLines(c(method, size, seed, source_dir), file.path(output_dir, "arguments.txt"))
result <- cross_validate(total_data, ngroup = 5, fitting_method = record_fold,
                         cv_seed = 0, parameter_colnames = parameter_names)
baseline <- cross_validate_average(total_data, ngroup = 5, parameter_colnames = parameter_names,
                                   x_names = names(summaries), cv_seed = 0)
metrics <- data.frame(parameter = parameter_names, method, size, seed,
                       rmse = result$errors, baseline_rmse = baseline$errors,
                       performance = 1 - result$errors / baseline$errors,
                       coverage = result$contained, interval_width = result$interval_size)
stopifnot(all(is.finite(as.matrix(metrics[, c("rmse", "performance", "coverage", "interval_width")]))))
write.csv(metrics, file.path(output_dir, "metrics.csv"), row.names = FALSE)
saveRDS(result, file.path(output_dir, "complete.rds"))
print(metrics)
