library(jsonlite)
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3, !file.exists(args[3]))
rows <- read.csv(file.path(args[2], 'trends.csv'), check.names = FALSE)
stopifnot(nrow(rows) == 80)
maximum <- 0
for (name in unique(rows$source_means)) {
  native <- read.csv(gzfile(file.path(args[1], name)), check.names = FALSE)
  stopifnot(nrow(native) == 20001, identical(native$tick, 0:20000))
  selected <- rows[rows$source_means == name, ]
  for (i in seq_len(nrow(selected))) {
    row <- selected[i, ]
    values <- native[[paste0('mean [', row$metric, '] of group-', row$breed)]]
    expected <- c(values[1], tail(values, 1), tail(values, 1) - values[1])
    observed <- as.numeric(row[c('initial_mean', 'final_mean', 'final_minus_initial')])
    error <- max(abs(expected - observed) / pmax(1, abs(expected)))
    stopifnot(error < 1e-12)
    maximum <- max(maximum, error)
    increments <- diff(values)
    stopifnot(sum(increments > 0) == row$increasing_steps,
              sum(increments < 0) == row$decreasing_steps,
              sum(increments == 0) == row$unchanged_steps)
  }
}
write_json(list(cohorts = 32, trends = 80, checked_mean_values = 1600080,
                maximum_scaled_error = maximum, all_step_sign_counts_exact = TRUE,
                scope = 'Independent R complete-cohort mean trends; no additional simulation or inference.'),
           args[3], auto_unbox = TRUE, pretty = TRUE, digits = 16)
