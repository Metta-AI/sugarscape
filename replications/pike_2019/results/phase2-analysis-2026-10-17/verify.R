args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==2L)
x <- read.csv(file.path(args[1], 'survivors.csv'))
a <- jsonlite::fromJSON(file.path(args[1], 'analysis.json'), simplifyVector=FALSE)
errors <- numeric()
for (label in names(a$survivors)) {
 v <- x$survivors[x$condition==label]
 stopifnot(length(v)==100, identical(sort(x$seed[x$condition==label]),0:99))
 expected <- a$survivors[[label]]
 ci <- t.test(v)$conf.int
 errors <- c(errors, abs(mean(v)-expected$mean),abs(sd(v)-expected$sample_sd),abs(ci[1]-expected$low),abs(ci[2]-expected$high))
}
for (comparison in a$paired_differences) {
 l <- x[x$condition==comparison$left,];r <- x[x$condition==comparison$right,]
 l <- l[order(l$seed),];r <- r[order(r$seed),]
 ci <- t.test(l$survivors,r$survivors,paired=TRUE)$conf.int
 errors <- c(errors,abs(mean(l$survivors-r$survivors)-comparison$mean),abs(ci[1]-comparison$low),abs(ci[2]-comparison$high))
}
b <- x$survivors[x$condition=='phase1-standard']
for (comparison in a$independent_baseline_differences) {
 v <- x$survivors[x$condition==comparison$condition]
 fit <- t.test(v,b)
 errors <- c(errors,abs(mean(v)-mean(b)-comparison$mean_difference),abs(fit$conf.int[1]-comparison$low),abs(fit$conf.int[2]-comparison$high),abs(unname(fit$parameter)-comparison$welch_degrees_of_freedom))
}
stopifnot(max(errors)<1e-9)
report <- list(survivor_intervals=6,paired_intervals=15,independent_baseline_intervals=6,scalar_comparisons=length(errors),maximum_absolute_difference=max(errors),scope='Independent R t.test arithmetic from exported per-run outcomes; validates survivor statistics, not source fidelity or equivalence.')
writeLines(jsonlite::toJSON(report,auto_unbox=TRUE,pretty=TRUE,digits=17),args[2])
print(report)
