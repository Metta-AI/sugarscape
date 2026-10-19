# Recompute complete-cohort statistics from pinned trajectories using R arithmetic.
library(jsonlite)
library(digest)

args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 4L, !file.exists(args[4]))
prepared <- args[1]
audit <- fromJSON(args[2])
summary_dir <- args[3]
report <- fromJSON(file.path(summary_dir, "summary.json"), simplifyVector = FALSE)
stopifnot(report$runs == 50L, report$observations == 1000050L)
stopifnot(digest(file = args[2], algo = "sha256") == report$audit_sha256)
manifest_path <- file.path(prepared, "manifest.csv")
stopifnot(digest(file = manifest_path, algo = "sha256") == report$manifest_sha256)
manifest <- read.csv(manifest_path, check.names = FALSE)
selected <- manifest[manifest$interpretation == report$interpretation &
                     manifest$pair_index == report$pair_index, ]
selected <- selected[order(selected$repetition), ]
stopifnot(identical(selected$repetition, 0:49))
stopifnot(identical(names(report$trajectory_sha256), selected$run_id))
stopifnot(!anyDuplicated(audit$completed$run_id))
matched <- match(selected$run_id, audit$completed$run_id)
stopifnot(!anyNA(matched))
means_csv <- read.csv(file.path(summary_dir, "means.csv"), check.names = FALSE)
sd_csv <- read.csv(file.path(summary_dir, "sample-sd.csv"), check.names = FALSE)
stopifnot(identical(means_csv$tick, 0:20000), identical(sd_csv$tick, 0:20000))
stopifnot(identical(names(means_csv), names(sd_csv)), ncol(means_csv) == 17L)
values <- matrix(0, nrow = 20001L * 16L, ncol = 50L)
for (i in seq_len(50L)) {
  trajectory <- file.path(audit$completed$directory[matched[i]], "trajectory.csv")
  stopifnot(digest(file = trajectory, algo = "sha256") == report$trajectory_sha256[[i]])
  observations <- read.csv(trajectory, check.names = FALSE)
  stopifnot(identical(observations$tick, 0:20000))
  stopifnot(identical(names(observations), names(means_csv)))
  values[, i] <- as.vector(as.matrix(observations[, -1]))
}
stopifnot(all(is.finite(values)))
means <- rowMeans(values)
sample_sd <- sqrt(rowSums((values - means)^2) / 49)
mean_error <- max(abs(as.vector(as.matrix(means_csv[, -1])) - means) / (1 + abs(means)))
sd_error <- max(abs(as.vector(as.matrix(sd_csv[, -1])) - sample_sd) / (1 + abs(sample_sd)))
stopifnot(mean_error <= 1e-12, sd_error <= 1e-10)

connection <- gzfile(file.path(summary_dir, "bootstrap-indices.u8.gz"), "rb")
indices <- readBin(connection, what = "raw", n = 1000001L)
close(connection)
stopifnot(length(indices) == 1000000L, all(as.integer(indices) < 50L))
stopifnot(digest(indices, algo = "sha256", serialize = FALSE) == report$bootstrap$indices_sha256)
draws <- matrix(as.integer(indices), nrow = 20000L, ncol = 50L, byrow = TRUE)
endpoints <- t(values[(3:16) * 20001L, ])
endpoint_error <- 0
interval_error <- 0
for (j in seq_len(14L)) {
  item <- report$endpoint_statistics[[j]]
  stopifnot(item$metric == names(means_csv)[j + 3L])
  expected <- c(mean(endpoints[, j]), sd(endpoints[, j]))
  endpoint_error <- max(endpoint_error,
                        abs(c(item$mean, item$sample_sd) - expected) / (1 + abs(expected)))
  samples <- rowMeans(matrix(endpoints[as.vector(draws) + 1L, j], nrow = 20000L, ncol = 50L))
  bounds <- as.numeric(quantile(samples, c(0.025, 0.975), type = 7))
  interval_error <- max(interval_error,
                        abs(unlist(item$pointwise_percentile_interval_95) - bounds) / (1 + abs(bounds)))
}
stopifnot(endpoint_error <= 1e-10, interval_error <= 1e-12)
validation <- list(
  runs = 50L, observations = 1000050L, means_checked = length(means),
  sample_standard_deviations_checked = length(sample_sd), endpoint_metrics = 14L,
  bootstrap_repetitions = 20000L, mean_max_scaled_error = mean_error,
  sample_sd_max_scaled_error = sd_error, endpoint_max_scaled_error = endpoint_error,
  interval_max_scaled_error = interval_error, r_version = as.character(getRversion()),
  summary_sha256 = digest(file = file.path(summary_dir, "summary.json"), algo = "sha256"),
  scope = paste("Independent R arithmetic with the recorded whole-run resampling indices.",
                "This does not independently validate the random-number generator,",
                "establish simultaneous interval coverage, or judge paper agreement.")
)
write_json(validation, args[4], pretty = TRUE, auto_unbox = TRUE, digits = NA)
cat(toJSON(validation, auto_unbox = TRUE, digits = NA), "\n")
