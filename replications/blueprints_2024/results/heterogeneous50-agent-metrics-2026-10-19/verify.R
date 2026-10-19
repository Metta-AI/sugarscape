library(jsonlite)
r <- commandArgs(trailingOnly=TRUE)[[1]]
d <- fromJSON(file.path(r,'per-run.json'),simplifyVector=FALSE)
s <- fromJSON(file.path(r,'summary.json'),simplifyVector=FALSE)
ratio <- function(values) vapply(strsplit(values,'/',fixed=TRUE),function(parts) prod(as.numeric(parts)^c(1,-1)[seq_along(parts)]),numeric(1))
observations <- vapply(d,function(x)x$observations,numeric(1)); errors <- c(); medians <- list()
for(metric in names(s$metrics)) {
 total <- ratio(vapply(d,function(x)x$measurements[[metric]]$sum,character(1)))
 initial <- ratio(vapply(d,function(x)x$measurements[[metric]]$initial,character(1)))
 for(name in names(s$metrics[[metric]]$conventions)) {
  exclude <- endsWith(name,'excluding_initial'); fixed <- startsWith(name,'zero_extended')
  values <- (total-initial*exclude)/((if(fixed) 5001 else observations)-exclude)
  observed <- median(values);expected <- s$metrics[[metric]]$conventions[[name]]$median
  medians[[paste(metric,name,sep='/')]] <- observed;errors <- c(errors,abs(observed-expected))
 }
}
stopifnot(length(d)==500,length(errors)==12,max(errors)<1e-10)
write_json(list(inputs=500,median_checks=12,maximum_absolute_error=max(errors),medians=medians,r_version=as.character(getRversion()),scope='Independent R arithmetic from retained exact per-run sums; not an independent simulator.'),file.path(r,'r-verification.json'),pretty=TRUE,auto_unbox=TRUE,digits=16)
