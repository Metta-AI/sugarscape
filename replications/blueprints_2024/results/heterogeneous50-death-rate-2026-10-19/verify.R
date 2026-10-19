library(jsonlite)
r <- commandArgs(trailingOnly=TRUE)[[1]]
d <- fromJSON(file.path(r,'per-run.json'),simplifyVector=FALSE); s <- fromJSON(file.path(r,'summary.json'),simplifyVector=FALSE);errors <- c()
for(key in names(d[[1]]$definitions)) {
 for(order in c('mean_of_step_ratios','ratio_of_sums')) {
  values <- vapply(d,function(row) {
   z <- row$definitions[[key]]
   100*if(order=='mean_of_step_ratios') z$sum_step_ratios/z$positive_rows else z$deaths_sum_positive/z$population_sum_positive
  },numeric(1))
  expected <- s$definitions[[paste(key,order,sep='/')]]$median_percent
  errors <- c(errors,abs(median(values)-expected))
 }
}
stopifnot(length(d)==500,length(errors)==8,max(errors)<1e-12)
write_json(list(inputs=500,median_checks=8,maximum_absolute_error=max(errors),scope='Independent R aggregation from retained per-run sufficient statistics; per-step ratio sums are shared inputs, not independently recomputed.'),file.path(r,'r-verification.json'),pretty=TRUE,auto_unbox=TRUE,digits=16)
