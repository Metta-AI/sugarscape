library(jsonlite)
r <- commandArgs(trailingOnly=TRUE)[[1]];d <- read.csv(file.path(r,'per-timestep.csv'),check.names=FALSE);s <- fromJSON(file.path(r,'summary.json'))
stopifnot(nrow(d)==5001,all(d$timestep==0:5000),all(d$population>0))
rates <- 100*(d$agentStarvationDeaths+d$agentCombatDeaths+d$agentAgingDeaths)/d$population
error <- max(abs(rates-d$author_meanDeaths_percent))
values <- c(mean(rates),mean(rates[-1]),median(rates),median(rates[-1]));expected <- unlist(s$death_rate_percent)
stopifnot(error<1e-12,max(abs(values-expected))<1e-12)
write_json(list(per_timestep_checks=5001,maximum_absolute_error=error,summary_checks=4,maximum_summary_error=max(abs(values-expected)),scope='Independent R recomputation from summed integer death counts and populations, including all per-timestep rates.'),file.path(r,'r-verification.json'),pretty=TRUE,auto_unbox=TRUE,digits=16)
