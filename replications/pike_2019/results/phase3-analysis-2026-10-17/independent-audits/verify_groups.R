args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==2L)
x <- read.csv(file.path(args[1],'run-measurements.csv'))
a <- jsonlite::fromJSON(file.path(args[1],'analysis.json'),simplifyVector=FALSE)
stopifnot(nrow(x)==1800L,a$observations==1800000)
errors <- numeric()
for(e in a$estimates) {
 z <- x[x$condition==e$condition,];stopifnot(nrow(z)==100L,identical(sort(z$seed),0:99))
 v <- z[[e$metric]]
 ci <- if(sd(v)==0) rep(mean(v),2) else t.test(v)$conf.int
 errors <- c(errors,abs(mean(v)-e$mean),abs(ci[1]-e$low),abs(ci[2]-e$high))
}
for(e in a$paired_movement_differences) {
 l <- x[x$condition==e$left,];r <- x[x$condition==e$right,]
 l <- l[order(l$seed),];r <- r[order(r$seed),];stopifnot(identical(l$seed,r$seed))
 v <- l[[e$metric]]-r[[e$metric]]
 ci <- if(sd(v)==0) rep(mean(v),2) else t.test(l[[e$metric]],r[[e$metric]],paired=TRUE)$conf.int
 errors <- c(errors,abs(mean(v)-e$mean),abs(ci[1]-e$low),abs(ci[2]-e$high))
}
stopifnot(length(a$estimates)==36L,length(a$paired_movement_differences)==24L,max(errors)<1e-9)
r <- list(intervals=60,scalar_comparisons=length(errors),maximum_absolute_difference=max(errors),scope='Independent R statistics for all complete-grid ungrouped-agent estimates and movement contrasts; reporter reconstruction validated separately.')
writeLines(jsonlite::toJSON(r,auto_unbox=TRUE,pretty=TRUE,digits=17),args[2]);print(r)
