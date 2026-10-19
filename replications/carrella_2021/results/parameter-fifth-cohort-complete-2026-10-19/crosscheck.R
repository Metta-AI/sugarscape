d <- read.csv('replications/carrella_2021/results/parameter-fifth-cohort-complete-2026-10-19/runs.csv')
stopifnot(nrow(d)==128, all(table(d$variant)==64))
a <- d[d$variant=='native',]; b <- d[d$variant=='independent',]
metrics <- c('last_population','minimum_population','price_at475','last_price','maximum_price','mean_price')
result <- data.frame(metric=metrics, difference=sapply(metrics,function(m) { points <- sort(unique(c(a[[m]],b[[m]]))); max(abs(ecdf(a[[m]])(points)-ecdf(b[[m]])(points))) }))
write.csv(result,'/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-parameter-fifth-r-ecdf.csv',row.names=FALSE)
events <- cbind(persistent_late_price=d$price_at475>=10 & d$last_price>=10,low_final_population=d$last_population<50)
rare <- lapply(seq_len(ncol(events)),function(i) { v <- events[,i]; x <- sum(v[d$variant=='native']); y <- sum(v[d$variant=='independent']); data.frame(event=colnames(events)[i],native=x,independent=y,p=fisher.test(matrix(c(x,64-x,y,64-y),nrow=2,byrow=TRUE))$p.value) })
write.csv(do.call(rbind,rare),'/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-parameter-fifth-r-rare.csv',row.names=FALSE)
