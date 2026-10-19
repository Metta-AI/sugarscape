library(jsonlite)
r <- commandArgs(trailingOnly=TRUE)[[1]]
d <- read.csv(file.path(r,'per-run.csv'),colClasses='character')
s <- fromJSON(file.path(r,'summary.json'),simplifyVector=FALSE)
ratio <- function(values) vapply(strsplit(values,'/',fixed=TRUE),function(parts) prod(as.numeric(parts)^c(1,-1)[seq_along(parts)]),numeric(1))
total <- ratio(d$wealth_sum); initial <- ratio(d$initial_wealth); observations <- as.integer(d$observations)
errors <- c(); medians <- list()
for (name in names(s$conventions)) {
 exclude <- endsWith(name,'excluding_initial'); fixed <- startsWith(name,'zero_extended')
 values <- (total-initial*exclude)/((if(fixed) 5001 else observations)-exclude)
 observed <- median(values); expected <- s$conventions[[name]]$median
 medians[[name]] <- observed; errors <- c(errors,abs(observed-expected))
}
stopifnot(nrow(d)==500,max(errors)<1e-9)
write_json(list(inputs=500,median_checks=4,maximum_absolute_error=max(errors),medians=medians,r_version=as.character(getRversion()),scope='Independent R arithmetic from exact per-run wealth sums; not an independent simulator.'),file.path(r,'r-verification.json'),pretty=TRUE,auto_unbox=TRUE,digits=16)
