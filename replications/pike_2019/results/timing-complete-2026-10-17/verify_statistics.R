# Independently recompute each seed-paired interval from audited timing measurements.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2, !file.exists(args[[2]]))
x <- jsonlite::fromJSON(args[[1]])
maximum_difference <- 0
for (i in seq_len(nrow(x$comparisons))) {
  r <- x$comparisons[i, ]
  a <- x$measurements[x$measurements$condition == r$numerator, ]
  b <- x$measurements[x$measurements$condition == r$denominator, ]
  a <- a[order(a$seed), ]
  b <- b[order(b$seed), ]
  stopifnot(identical(a$seed, 0:99), identical(b$seed, 0:99))
  values <- if (r$statistic == "paired_ratio") a[[r$metric]] / b[[r$metric]] else a[[r$metric]] - b[[r$metric]]
  result <- t.test(values)
  difference <- max(abs(c(unname(result$estimate) - r$mean, result$conf.int - as.numeric(unlist(r$pointwise_ci95)))))
  stopifnot(difference < 1e-10)
  maximum_difference <- max(maximum_difference, difference)
}
writeLines(jsonlite::toJSON(list(comparisons = nrow(x$comparisons), maximum_absolute_difference = maximum_difference, independent_implementation = "R stats::t.test on all 100 paired seeds"), auto_unbox = TRUE, pretty = TRUE, digits = 17), args[[2]])
