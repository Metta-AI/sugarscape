library(jsonlite)
library(digest)
args <- commandArgs(TRUE)
stopifnot(length(args) == 1L)
r <- args[[1]]
report <- fromJSON(file.path(r, "summary.json"), simplifyVector = FALSE)
for (path in names(report$source_sha256)) {
  stopifnot(identical(digest(file = path, algo = "sha256"), report$source_sha256[[path]]))
}
source <- names(report$source_sha256)[endsWith(names(report$source_sha256), "/per-run.json")]
rows <- fromJSON(source, simplifyVector = FALSE)
stopifnot(length(rows) == 500L)
errors <- numeric()
for (key in names(rows[[1]]$definitions)) {
  excluded <- as.integer(grepl("/exclude_initial", key, fixed = TRUE))
  sums <- vapply(rows, function(x) x$definitions[[key]]$sum_step_ratios, numeric(1))
  positive <- vapply(rows, function(x) x$definitions[[key]]$positive_rows, numeric(1))
  observed <- vapply(rows, function(x) x$observations, numeric(1)) - excluded
  choices <- list(positive_population_only = positive, observed_zero_assigned = observed,
                  fixed_horizon_zero_extended = rep(5001 - excluded, 500))
  for (name in names(choices)) {
    value <- median(100 * (sums / choices[[name]]))
    expected <- report$definitions[[paste(key, name, sep = "/")]]$median_percent
    errors <- c(errors, abs(value - expected))
  }
}
stopifnot(length(errors) == 12L, max(errors) < 1e-12)
future_rows <- sum(vapply(rows, function(x) 5001 - x$observations, numeric(1)))
zero_rows <- sum(vapply(rows, function(x) x$definitions[["all_reported_causes/include_initial"]]$zero_population_rows, numeric(1)))
zero_deaths <- sum(vapply(rows, function(x) x$definitions[["all_reported_causes/include_initial"]]$deaths_at_zero_population, numeric(1)))
stopifnot(future_rows == report$future_zero_rows, zero_rows == report$terminal_zero_population_rows,
          zero_rows == report$native_extinctions, zero_deaths == report$all_cause_deaths_at_zero_population)
write_json(list(inputs = 500L, median_checks = 12L, maximum_absolute_error = max(errors),
                future_zero_rows = future_rows, terminal_zero_population_rows = zero_rows,
                all_cause_deaths_at_zero_population = zero_deaths,
                scope = "Independent R aggregation from the same previously native-audited accumulators; not a second native trajectory recomputation."),
           file.path(r, "r-verification.json"), auto_unbox = TRUE, pretty = TRUE, digits = 16)
