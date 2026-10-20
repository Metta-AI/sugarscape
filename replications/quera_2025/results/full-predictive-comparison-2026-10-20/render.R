# Render retained, audited samples without fitting curves to paper images.
library(jsonlite)
library(digest)
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2L, !dir.exists(args[2]))
root <- args[1]
output <- args[2]
terminal <- fromJSON(file.path(root, "predictive-terminal.json"))
stopifnot(terminal$exit_code == 0, terminal$native_trajectories == 4000,
          terminal$python_audit_passed, terminal$independent_r_arithmetic_passed)
summary <- fromJSON(file.path(root, "predictive-summary.json"), simplifyVector = FALSE)
stopifnot(digest(file = file.path(root, "protocol.json"), algo = "sha256") == summary$protocol_sha256)
observation_path <- file.path(root, "predictive/observation.csv")
stopifnot(digest(file = observation_path, algo = "sha256") == summary$observation_sha256)
observation <- as.matrix(read.csv(observation_path, header = FALSE))
stopifnot(identical(dim(observation), c(2L, 50L)))
methods <- c("prior", "pathwise", "vargrad")
colors <- c(prior = "#707070", pathwise = "#0072B2", vargrad = "#D55E00", truth = "#009E73")
parameters <- list()
inputs <- list()
for (method in c(methods, "truth")) {
  record <- summary$distributions[[method]]
  stopifnot(record$draws == 1000, record$stored_states == 50000)
  for (name in names(record$sha256)) {
    path <- file.path(root, "predictive", name)
    stopifnot(digest(file = path, algo = "sha256") == record$sha256[[name]])
    inputs[[paste0("predictive/", name)]] <- record$sha256[[name]]
  }
  parameters[[method]] <- read.csv(file.path(root, "predictive", paste0(method, "-parameters.csv")))
  stopifnot(nrow(parameters[[method]]) == 1000)
}
dir.create(output)
pdf(file.path(output, "predictive.pdf"), width = 11, height = 5)
par(mfrow = c(1, 2), mar = c(4, 4, 3, 1), oma = c(2, 0, 1, 0))
channels <- c("mean_wealth", "alive_fraction")
for (i in seq_along(channels)) {
  channel <- channels[i]
  records <- lapply(summary$distributions, function(d) d$channels[[channel]])
  limits <- range(observation[i, ], unlist(lapply(records, function(r) c(r$q025, r$q975))))
  plot(0:49, observation[i, ], type = "n", ylim = limits, xlab = "Stored time (initial state = 0)",
       ylab = if (i == 1) "Mean holdings per initial agent" else "Alive fraction", main = "Reconstructed calibration")
  for (method in methods) {
    record <- records[[method]]
    polygon(c(0:49, 49:0), c(unlist(record$q025), rev(unlist(record$q975))),
            col = adjustcolor(colors[method], alpha.f = 0.13), border = NA)
    lines(0:49, unlist(record$mean), col = colors[method], lwd = 2)
  }
  lines(0:49, unlist(records$truth$mean), col = colors["truth"], lty = 3, lwd = 2)
  lines(0:49, observation[i, ], col = "black", lty = 2, lwd = 2)
  legend("topleft", c(methods, "true-parameter mean", "observed calibration data"),
         col = c(colors[methods], colors["truth"], "black"), lty = c(1, 1, 1, 3, 2), bty = "n", cex = 0.7)
}
mtext("Bands: pointwise empirical 2.5%-97.5% quantiles from 1,000 draws; reconstructed prior and validation settings.", outer = TRUE, side = 1, cex = 0.8)
dev.off()

# The five independent coordinates omit p6 = 1-p1; retain all 1,000 samples.
axes <- c("p1", "m_alpha", "m_beta", "w_alpha", "w_beta")
truth <- c(0.2, 2, 5, 5, 2)
bounds <- list(c(0, 1), c(0.1, 10), c(0.1, 10), c(0.1, 10), c(0.1, 10))
pdf(file.path(output, "posterior-pairs.pdf"), width = 11, height = 11)
par(mfrow = c(5, 5), mar = c(2.8, 2.8, 1, 0.4), oma = c(3, 0, 3, 0),
    mgp = c(1.5, 0.4, 0), cex.lab = 0.8, cex.axis = 0.75)
for (row in seq_along(axes)) {
  for (column in seq_along(axes)) {
    if (row < column) {
      plot.new()
    } else if (row == column) {
      plot(bounds[[column]], c(0, 1), type = "n", xlab = axes[column], ylab = "Empirical CDF")
      for (method in methods) plot(ecdf(parameters[[method]][[axes[column]]]), add = TRUE,
                                  col = colors[method], verticals = TRUE, do.points = FALSE)
      abline(v = truth[column], lty = 2)
    } else {
      plot(bounds[[column]], bounds[[row]], type = "n", xlab = axes[column], ylab = axes[row])
      for (method in methods) points(parameters[[method]][[axes[column]]], parameters[[method]][[axes[row]]],
                                    pch = 16, cex = 0.18, col = adjustcolor(colors[method], alpha.f = 0.2))
      points(truth[column], truth[row], pch = 4, cex = 1.5, lwd = 2)
    }
  }
}
mtext("Prior (grey), pathwise (blue), VarGrad (orange); true parameters dashed / cross", outer = TRUE, side = 3)
mtext("1,000 retained draws each; no density smoothing. Five independent coordinates; p6 = 1-p1.", outer = TRUE, side = 1)
dev.off()

histories <- list()
for (method in c("pathwise", "vargrad")) {
  path <- file.path(root, method, "epochs.csv")
  audit <- fromJSON(file.path(root, paste0(method, "-audit.json")), simplifyVector = FALSE)
  digest_value <- digest(file = path, algo = "sha256")
  stopifnot(digest_value == audit$sha256[["epochs.csv"]])
  inputs[[paste0(method, "/epochs.csv")]] <- digest_value
  histories[[method]] <- read.csv(path)
  stopifnot(nrow(histories[[method]]) == 5000, identical(histories[[method]]$epoch, 1:5000))
}
pdf(file.path(output, "training.pdf"), width = 11, height = 5)
par(mfrow = c(1, 2), mar = c(4, 4, 3, 1), oma = c(2, 0, 0, 0))
for (field in c("training_elbo", "validation_loss")) {
  limits <- range(unlist(lapply(histories, function(h) h[[field]])))
  plot(c(1, 5000), limits, type = "n", xlab = "Epoch", ylab = field,
       main = if (field == "training_elbo") "Recorded training ELBO" else "Validation negative log likelihood")
  for (method in names(histories)) lines(histories[[method]]$epoch, histories[[method]][[field]], col = colors[method])
  legend("topright", names(histories), col = colors[names(histories)], lty = 1, bty = "n")
}
mtext("All 5,000 epochs; unsmoothed. Objectives differ; these panels are not numerical reproductions of Figure 19.", outer = TRUE, side = 1, cex = 0.8)
dev.off()
write_json(list(input_sha256 = inputs, summary_sha256 = digest(file = file.path(root, "predictive-summary.json"), algo = "sha256"),
                rendered = c("predictive.pdf", "posterior-pairs.pdf", "training.pdf"), visual_review_complete = FALSE,
                scope = "Reconstructed experiment; no historical posterior identity, density agreement, or paper completion inferred."),
           file.path(output, "render.json"), auto_unbox = TRUE, pretty = TRUE)
