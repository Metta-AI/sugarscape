library(jsonlite)
args <- commandArgs(trailingOnly=TRUE)
a <- fromJSON(file.path(args[1], 'analysis.json'))
d <- read.csv(file.path(args[1], 'run-measurements.csv'))
errors <- numeric()
checked <- 0L
check <- function(values, row) {
  values <- values[!is.na(values)]
  stopifnot(length(values) == row$n, length(values) > 1)
  half <- qt(.975, length(values)-1)*sd(values)/sqrt(length(values))
  actual <- c(mean(values), mean(values)-half, mean(values)+half)
  expected <- c(row$mean, row$low, row$high)
  errors <<- c(errors, abs(actual-expected))
  checked <<- checked+1L
  stopifnot(max(abs(actual-expected)) < 1e-10)
}
for(i in seq_len(nrow(a$estimates))) {
  row <- a$estimates[i,]
  check(d$mean[d$condition == row$condition & d$window == row$window & d$metric == row$metric], row)
}
for(i in seq_len(nrow(a$paired_late_minus_early))) {
  row <- a$paired_late_minus_early[i,]
  part <- d[d$condition == row$condition & d$metric == row$metric,]
  pairs <- merge(part[part$window=='late',],part[part$window=='early',],by='seed')
  stopifnot(nrow(pairs)==100)
  check(pairs$mean.x-pairs$mean.y, row)
}
for(i in seq_len(nrow(a$paired_late_policy_minus_none))) {
  row <- a$paired_late_policy_minus_none[i,]
  part <- d[d$metric == row$metric & d$window=='late',]
  pairs <- merge(part[part$condition==row$left,],part[part$condition==row$right,],by='seed')
  stopifnot(nrow(pairs)==100)
  check(pairs$mean.x-pairs$mean.y, row)
}
stopifnot(checked==150,nrow(d)==8400,length(errors)==450)
result <- list(intervals=checked, scalars=length(errors), max_error=max(errors), run_measurements=nrow(d), scope='Independent base-R means, t quantiles, standard errors and paired joins; validates all150 reported intervals from exported per-run measurements, not raw trajectory reconstruction.')
write_json(result,args[2],auto_unbox=TRUE,pretty=TRUE,digits=16)
print(result)
