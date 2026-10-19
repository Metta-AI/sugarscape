library(jsonlite)
args <- commandArgs(TRUE)
stopifnot(length(args) == 2L)
reference <- read.csv(args[[1]])
root <- args[[2]]
actual <- read.csv(file.path(root, "current/metrics.csv"))
stopifnot(nrow(actual) == 5L, setequal(actual$parameter, reference$parameter))
actual <- actual[match(reference$parameter, actual$parameter), ]
columns <- c("rmse", "baseline_rmse", "performance", "coverage", "interval_width")
expected <- as.matrix(reference[columns])
differences <- abs(expected - as.matrix(actual[columns]))
scaled <- differences / pmax(1, abs(expected))
stopifnot(all(is.finite(differences)), max(scaled) < 1e-12)
report <- list(aggregate_values = length(differences), maximum_absolute_error = max(differences),
               maximum_scaled_error = max(scaled), tolerance = 1e-12,
               scope = "All five aggregate metrics for all five parameters; CSV serialization precision, with complete raw predictions and bounds separately checked exactly.")
write_json(report, file.path(root, "metric-validation.json"), auto_unbox = TRUE, pretty = TRUE, digits = 16)
print(report)
