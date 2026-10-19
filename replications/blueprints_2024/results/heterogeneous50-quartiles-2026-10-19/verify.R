library(jsonlite)
a <- commandArgs(trailingOnly=TRUE); root <- a[[1]]
d <- read.csv(file.path(dirname(root),'blueprints-heterogeneous50-population-001/per-run.csv'))
report <- fromJSON(file.path(root,'quartiles.json'),simplifyVector=FALSE)
methods <- c('inverted_cdf','averaged_inverted_cdf','closest_observation','interpolated_inverted_cdf','hazen','weibull','linear','median_unbiased','normal_unbiased')
errors <- c()
for (name in names(report$conventions)) {
 exclude <- endsWith(name,'excluding_initial'); fixed <- startsWith(name,'zero_extended')
 x <- (d$population_sum-250*exclude)/((if(fixed) 5001 else d$observations)-exclude)
 for (type in 1:9) {
  observed <- quantile(x,c(.25,.75),type=type,names=FALSE)
  expected <- unlist(report$conventions[[name]]$quantiles_by_method[[methods[[type]]]])
  errors <- c(errors,abs(observed-expected))
 }
}
stopifnot(length(errors)==72,max(errors)<1e-10)
write_json(list(values_checked=72,max_absolute_error=max(errors),r_version=as.character(getRversion()),scope='Independent R quantile arithmetic using the already audited per-run sums; not an independent simulator.'),file.path(root,'r-verification.json'),pretty=TRUE,auto_unbox=TRUE)
