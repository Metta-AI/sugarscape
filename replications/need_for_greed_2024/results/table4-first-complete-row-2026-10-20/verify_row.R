args <- commandArgs(trailingOnly=TRUE)
d <- read.csv(args[1])
stopifnot(nrow(d) == 500, length(unique(d$entry)) == 500)
p <- d$final_population
counts <- c(sum(p == 0), sum(p > 0 & p <= 250), sum(p > 250))
stopifnot(identical(counts, c(6L, 0L, 494L)), all(counts / 5 == c(1.2, 0, 98.8)))
cat("500 unique inputs; counts6/0/494; percentages1.2/0/98.8; published row exact\n")
