args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==2L)
x <- read.csv(file.path(args[1], 'run-measurements.csv'))
a <- jsonlite::fromJSON(file.path(args[1], 'analysis.json'), simplifyVector=FALSE)
errors <- numeric()
checked <- 0L
undefined <- 0L
for (e in a$estimates) {
 z <- x[x$condition==e$condition & x$metric==e$metric,]
 stopifnot(nrow(z)==100L,identical(sort(z$seed),0:99))
 v <- z$value[!is.na(z$value)]
 stopifnot(length(v)==e$defined_runs)
 if(length(v)<2L) { stopifnot(is.null(e$interval)); undefined <- undefined+1L; next }
 # Zero variance is a valid degenerate descriptive interval, not a t-test.
 ci <- if(sd(v)==0) rep(mean(v),2) else t.test(v)$conf.int
 errors <- c(errors,abs(mean(v)-e$interval$mean),abs(ci[1]-e$interval$low),abs(ci[2]-e$interval$high))
 stopifnot(length(v)==e$interval$n)
 checked <- checked+1L
}
for (e in a$paired_differences) {
 l <- x[x$condition==e$left & x$metric==e$metric,];r <- x[x$condition==e$right & x$metric==e$metric,]
 l <- l[order(l$seed),];r <- r[order(r$seed),]
 stopifnot(identical(l$seed,r$seed))
 keep <- !is.na(l$value) & !is.na(r$value)
 v <- l$value[keep]-r$value[keep]
 stopifnot(length(v)==e$defined_pairs)
 if(length(v)<2L) { stopifnot(is.null(e$interval)); undefined <- undefined+1L; next }
 ci <- if(sd(v)==0) rep(mean(v),2) else t.test(l$value[keep],r$value[keep],paired=TRUE)$conf.int
 errors <- c(errors,abs(mean(v)-e$interval$mean),abs(ci[1]-e$interval$low),abs(ci[2]-e$interval$high))
 stopifnot(length(v)==e$interval$n)
 checked <- checked+1L
}
stopifnot(max(errors)<1e-8)
report <- list(checked_intervals=checked,undefined_intervals=undefined,scalar_comparisons=length(errors),maximum_absolute_difference=max(errors),scope='Independent R statistics over all exported complete-grid run measurements; source fidelity is not established.')
writeLines(jsonlite::toJSON(report,auto_unbox=TRUE,pretty=TRUE,digits=17),args[2]);print(report)
