args <- commandArgs(trailingOnly=TRUE)
p <- args[[1]]
x <- read.csv(file.path(p, "survivors.csv"))
stopifnot(nrow(x) == 300, all(table(x$file) == 100))
result <- do.call(rbind, lapply(split(x, x$file), function(d) {
 stopifnot(identical(d$run, 0:99))
 data.frame(file=d$file[[1]], n=nrow(d), mean=mean(d$survivors), sample_sd=sd(d$survivors), minimum=min(d$survivors), maximum=max(d$survivors))
}))
row.names(result) <- NULL
write.csv(result, file.path(p, "independent-r.csv"), row.names=FALSE)
print(result, digits=17)
