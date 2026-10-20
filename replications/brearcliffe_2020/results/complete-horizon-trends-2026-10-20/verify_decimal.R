library(jsonlite)
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3, !file.exists(args[3]))
rows <- read.csv(file.path(args[2], 'trends.csv'), check.names = FALSE)
stopifnot(nrow(rows) == 80)
maximum <- 0
parser_sensitive_curves <- 0
Sys.setlocale("LC_COLLATE", "C")
for (name in unique(rows$source_means)) {
  native <- read.csv(gzfile(file.path(args[1], name)), check.names = FALSE)
  decimal_text <- read.csv(gzfile(file.path(args[1], name)), check.names = FALSE, colClasses = 'character')
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
    expected_counts <- as.numeric(row[c('increasing_steps', 'decreasing_steps', 'unchanged_steps')])
    parser_sensitive_curves <- parser_sensitive_curves + as.integer(any(c(sum(increments > 0), sum(increments < 0), sum(increments == 0)) != expected_counts))
    # These means have one positive integer digit and decimal fractional digits.
    # Right-padding with zeros preserves their exact decimal order without parsing.
    text <- decimal_text[[paste0('mean [', row$metric, '] of group-', row$breed)]]
    stopifnot(all(grepl('^[1-9][.][0-9]+$', text)))
    padded <- paste0(text, strrep('0', max(nchar(text)) - nchar(text)))
    before <- head(padded, -1)
    after <- tail(padded, -1)
    stopifnot(sum(after > before) == row$increasing_steps,
              sum(after < before) == row$decreasing_steps,
              sum(after == before) == row$unchanged_steps)
  }
}
write_json(list(cohorts = 32, trends = 80, checked_mean_values = 1600080,
                maximum_scaled_error = maximum, all_step_sign_counts_exact = TRUE,
                step_sign_basis = "Exact decimal text ordering; no tolerance or floating-point subtraction",
                parser_sensitive_curves = parser_sensitive_curves,
                scope = 'Independent R complete-cohort mean trends; no additional simulation or inference.'),
           args[3], auto_unbox = TRUE, pretty = TRUE, digits = 16)
