args <- commandArgs(trailingOnly=TRUE)
p <- args[[1]]
s <- read.csv(file.path(p, "survivors-opcode-decoded.csv"))
h <- read.csv(file.path(p, "histogram.csv"))
x <- read.csv(gzfile(file.path(p, "price-steps.csv.gz")))
stopifnot(nrow(s) == 100, nrow(x) == 100000, sum(s$survivors) == 9283)
valid <- x$sample_sd_log_price[!is.na(x$sample_sd_log_price)]
counts <- hist(valid, breaks=c(h$low, tail(h$high, 1)), right=FALSE, include.lowest=TRUE, plot=FALSE)$counts
stopifnot(identical(as.integer(counts), as.integer(h$count)), length(valid) == 26632)
stopifnot(sum(x$trades) == 884283, all(table(x$run) == 1000))
out <- data.frame(metric=c("survivor_mean", "survivor_sample_sd", "histogram_cells", "defined_dispersion_steps", "trade_records"), value=c(mean(s$survivors), sd(s$survivors), length(counts), length(valid), sum(x$trades)))
write.csv(out, file.path(p, "independent-r.csv"), row.names=FALSE)
print(out, digits=17)
