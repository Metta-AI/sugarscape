library(jsonlite)
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3L, !file.exists(args[3]))
root <- args[1]
report <- fromJSON(args[2], simplifyVector = FALSE)
observation <- as.matrix(read.csv(file.path(root, "observation.csv"), header = FALSE))
stopifnot(identical(dim(observation), c(2L, 50L)))
errors <- numeric()
checked <- 0L
verify <- function(actual, expected) {
  expected <- as.numeric(unlist(expected))
  stopifnot(length(actual) == length(expected), all(is.finite(actual)))
  error <- max(abs(actual - expected) / pmax(1, abs(expected)))
  stopifnot(error <= 1e-10)
  errors <<- c(errors, error)
  checked <<- checked + length(actual)
}
for (distribution in c("prior", "pathwise", "vargrad", "truth")) {
  target <- report$distributions[[distribution]]
  parameters <- read.csv(file.path(root, paste0(distribution, "-parameters.csv")))
  trajectories <- read.csv(file.path(root, paste0(distribution, "-trajectories.csv")))
  stopifnot(nrow(parameters) == 1000L, nrow(trajectories) == 50000L)
  stopifnot(identical(parameters$sample, 1:1000))
  stopifnot(identical(trajectories$sample, rep(1:1000, each = 50)))
  stopifnot(identical(trajectories$seed, rep(10000:10999, each = 50)))
  stopifnot(identical(trajectories$time, rep(0:49, 1000)))
  for (name in c("p1", "p6", "m_alpha", "m_beta", "w_alpha", "w_beta")) {
    values <- parameters[[name]]
    expected <- target$parameters[[name]]
    quantiles <- quantile(values, c(0.025, 0.5, 0.975), type = 7, names = FALSE)
    verify(c(mean(values), quantiles),
           c(expected$mean, expected$q025, expected$median, expected$q975))
    stopifnot(identical(
      quantiles[1] <= expected$truth && expected$truth <= quantiles[3],
      expected$truth_inside_pointwise_interval
    ))
  }
  for (index in 1:2) {
    name <- c("mean_wealth", "alive_fraction")[index]
    values <- matrix(trajectories[[name]], nrow = 1000, ncol = 50, byrow = TRUE)
    expected <- target$channels[[name]]
    means <- colMeans(values)
    quantiles <- apply(values, 2, quantile, probs = c(0.025, 0.5, 0.975),
                       type = 7, names = FALSE)
    verify(means, expected$mean)
    verify(quantiles[1, ], expected$q025)
    verify(quantiles[2, ], expected$median)
    verify(quantiles[3, ], expected$q975)
    coverage <- sum(observation[index, ] >= quantiles[1, ] &
                    observation[index, ] <= quantiles[3, ])
    verify(coverage, expected$observed_states_inside_interval)
    rmse <- sqrt(mean((means - observation[index, ])^2))
    verify(rmse, expected$predictive_mean_rmse_against_observation)
  }
}
write_json(list(
  distributions = 4,
  trajectories = 4000,
  stored_states = 200000,
  arithmetic_values_verified = checked,
  maximum_scaled_error = max(errors),
  r_version = as.character(getRversion()),
  scope = paste(
    "Independent R summaries from all native raw exports.",
    "No model-state replay, simultaneous interval coverage,",
    "historical posterior identity or paper verdict is inferred."
  )
), args[3], auto_unbox = TRUE, pretty = TRUE)
cat("PREDICTIVE_R_ARITHMETIC_VERIFIED\n")
