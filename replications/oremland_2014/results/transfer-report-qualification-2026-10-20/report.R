# Recompute held-out objectives in R and display every evaluated final policy.
library(jsonlite)
library(digest)
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3L, !dir.exists(args[3]))
run <- args[1]
audit <- fromJSON(args[2], simplifyVector = FALSE)
report <- fromJSON(file.path(run, "complete.json"), simplifyVector = FALSE)
plan <- fromJSON(file.path(run, "plan.json"), simplifyVector = FALSE)
for (name in names(audit$sha256)) stopifnot(digest(file = file.path(run, name), algo = "sha256") == audit$sha256[[name]])
stopifnot(report$native_runs == audit$native_runs, length(report$policies) == audit$policies)
rows <- list()
checked <- 0L
for (group in plan$groups) {
  native <- lapply(readLines(file.path(run, group$name, "results.jsonl")), fromJSON)
  requests <- lapply(readLines(file.path(run, group$name, "requests.jsonl")), fromJSON)
  points <- Filter(function(p) p$group == group$name, report$policies)
  count <- length(plan$held_out_seeds)
  stopifnot(count == 200L)
  stopifnot(length(native) == length(requests), length(native) == length(points) * count)
  for (i in seq_along(points)) {
    point <- points[[i]]
    indices <- (i - 1L) * count + seq_len(count)
    observed <- native[indices]
    expected <- requests[indices]
    stopifnot(point$samples == count)
    for (j in seq_len(count)) {
      stopifnot(observed[[j]]$id == expected[[j]]$id,
                observed[[j]]$seed == plan$held_out_seeds[[j]],
                observed[[j]]$steps == 50L)
    }
    for (metric in c("population", "total_tax")) {
      values <- vapply(observed, function(r) r[[metric]], numeric(1))
      stopifnot(all(is.finite(values)), sum(values) == point[[metric]]$sum,
                abs(mean(values) - point[[metric]]$mean) < 1e-10,
                abs(sd(values) / sqrt(count) - point[[metric]]$standard_error) < 1e-10)
      checked <- checked + length(values)
    }
    rows[[length(rows) + 1L]] <- data.frame(
      group = group$name, identity = point$identity, width = point$width,
      optimizer_seed = point$optimizer_seed, samples = count,
      mean_revenue = point$total_tax$mean, revenue_se = point$total_tax$standard_error,
      mean_mortality_fraction = 1 - point$population$mean / 200,
      mortality_se = point$population$standard_error / 200,
      dominated_by_full_search = point$dominated_by_full_search)
  }
}
points <- do.call(rbind, rows)
stopifnot(nrow(points) == audit$policies, checked == 2L * audit$native_runs)
for (i in seq_len(nrow(points))) {
  reference <- points[points$width == 50 & points$optimizer_seed == points$optimizer_seed[i], ]
  stopifnot(nrow(reference) > 0)
  dominated <- any((reference$mean_revenue > points$mean_revenue[i] & reference$mean_mortality_fraction <= points$mean_mortality_fraction[i]) |
                   (reference$mean_revenue >= points$mean_revenue[i] & reference$mean_mortality_fraction < points$mean_mortality_fraction[i]))
  stopifnot(dominated == points$dominated_by_full_search[i])
}
dir.create(args[3])
write.csv(points, file.path(args[3], "held-out-policies.csv"), row.names = FALSE)
colors <- c("50" = "#000000", "40" = "#0072B2", "30" = "#E69F00", "20" = "#009E73", "10" = "#CC79A7", "5" = "#D55E00")
seeds <- unique(points$optimizer_seed)
xrange <- range(points$mean_revenue - points$revenue_se, points$mean_revenue + points$revenue_se)
yrange <- range(points$mean_mortality_fraction - points$mortality_se, points$mean_mortality_fraction + points$mortality_se)
pdf(file.path(args[3], "held-out-transfer.pdf"), width = max(8, 5 * length(seeds)), height = 6.5)
par(mfrow = c(1, length(seeds)), mar = c(4.3, 4.3, 5.5, 1), oma = c(5, 0, 1, 0))
for (seed in seeds) {
  subset <- points[points$optimizer_seed == seed, ]
  plot(xrange, yrange, type = "n", xlab = "Mean full-model revenue", ylab = "Mean full-model mortality fraction",
       main = "")
  title(main = paste("Optimizer seed", seed), line = 4)
  for (i in seq_len(nrow(subset))) {
    row <- subset[i, ]
    color <- colors[as.character(row$width)]
    segments(row$mean_revenue - row$revenue_se, row$mean_mortality_fraction,
             row$mean_revenue + row$revenue_se, row$mean_mortality_fraction, col = color)
    segments(row$mean_revenue, row$mean_mortality_fraction - row$mortality_se,
             row$mean_revenue, row$mean_mortality_fraction + row$mortality_se, col = color)
    points(row$mean_revenue, row$mean_mortality_fraction, col = color,
           pch = if (row$dominated_by_full_search) 1 else 16)
  }
  widths <- sort(unique(subset$width), decreasing = TRUE)
  legend("top", paste("Source width", widths), col = colors[as.character(widths)], pch = 16, bty = "n", cex = 0.8,
         inset = c(0, -0.22), xpd = NA, ncol = 3)
}
mtext("All final policies; bars = one standard error across 200 held-out seeds.", side = 1, outer = TRUE, line = 0, cex = 0.8)
mtext("Open symbols: empirical full-search dominance.", side = 1, outer = TRUE, line = 1.1, cex = 0.8)
mtext("Reconstructed controls and optimizer budgets; no global-optimality", side = 1, outer = TRUE, line = 2.5, cex = 0.8)
mtext("or historical frontier identity claim.", side = 1, outer = TRUE, line = 3.6, cex = 0.8)
dev.off()
write_json(list(native_values_checked = checked, policies = nrow(points), native_runs = audit$native_runs,
                optimizer_seeds = seeds, source_widths = sort(unique(points$width)),
                empirical_dominance_decisions_checked = nrow(points),
                native_audit_sha256 = digest(file = args[2], algo = "sha256"),
                report_sha256 = digest(file = file.path(run, "complete.json"), algo = "sha256"),
                visual_review_complete = FALSE,
                scope = "Independent R arithmetic from every held-out native record. Pointwise standard errors and empirical dominance do not establish global optimization or statistical superiority."),
           file.path(args[3], "verification.json"), auto_unbox = TRUE, pretty = TRUE)
