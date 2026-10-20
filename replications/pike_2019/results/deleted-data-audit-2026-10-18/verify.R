args <- commandArgs(trailingOnly=TRUE)
p <- args[[1]]
results <- list()
for (name in c("network-10", "network-10-policy", "explicit-10-policy")) {
 x <- read.csv(gzfile(file.path(p, paste0(name, ".csv.gz"))))
 r <- read.csv(file.path(p, paste0(name, "-runs.csv")))
 h <- read.csv(file.path(p, paste0(name, "-histogram.csv")))
 stopifnot(nrow(x) == 100000, nrow(r) == 100, all(table(x$run) == 1000))
 valid <- x$sample_sd_log_price[!is.na(x$sample_sd_log_price)]
 bins <- hist(valid, breaks=c(h$low, tail(h$high, 1)), right=FALSE, include.lowest=TRUE, plot=FALSE)$counts
 stopifnot(identical(as.integer(bins), as.integer(h$count)))
 for (i in 0:99) {
  rows <- x[x$run == i, ]
  stopifnot(identical(rows$step, 1:1000))
  stopifnot(sum(rows$trades) == r$trade_records[i+1], sum(rows$invalid_prices) == r$invalid_prices[i+1])
  stopifnot(tail(rows$independents + rows$group_member_records, 1) == r$survivors[i+1])
 }
 results[[name]] <- data.frame(dataset=name, runs=nrow(r), observations=nrow(x), trades=sum(x$trades), invalid_prices=sum(x$invalid_prices), defined_dispersion=length(valid), histogram_bins=length(bins), survivor_mean=mean(r$survivors), mean_seconds=mean(r$native_seconds))
}
result <- do.call(rbind, results)
row.names(result) <- NULL
write.csv(result, file.path(p, "independent-r.csv"), row.names=FALSE)
print(result, digits=17)
