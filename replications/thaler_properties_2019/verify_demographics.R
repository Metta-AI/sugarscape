# Independently calculate all paired inheritance mean intervals from audited seeds.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args) == 2L, !file.exists(args[2]))
observations <- read.csv(args[1], stringsAsFactors=FALSE)
rows <- list()
for (metric in unique(observations$metric)) {
  data <- observations[observations$metric == metric, ]
  stopifnot(nrow(data) == 100L, identical(data$index, 0:99))
  stopifnot(all(is.finite(data$without)), all(is.finite(data$with)))
  samples <- list(mating=data$without, inheritance=data$with,
                  paired_change=data$with-data$without)
  for (label in names(samples)) {
    result <- t.test(samples[[label]], conf.level=0.95)
    rows[[length(rows)+1L]] <- data.frame(metric=metric, label=label,
      mean=unname(result$estimate), lower=result$conf.int[1], upper=result$conf.int[2])
  }
}
write.csv(do.call(rbind, rows), args[2], row.names=FALSE)
