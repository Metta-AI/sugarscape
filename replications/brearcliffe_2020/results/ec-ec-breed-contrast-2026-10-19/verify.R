library(jsonlite)
args <- commandArgs(trailingOnly=TRUE)
root <- args[[1]]
d <- read.csv(file.path(root,'paired-endpoints.csv'),check.names=FALSE)
x <- as.matrix(d[,-1]); stopifnot(all(dim(x)==c(50,14)))
con <- gzfile(file.path(dirname(root),'brearcliffe-ec-ec-snapshot-001/cohort/bootstrap-indices.u8.gz'),'rb')
i <- matrix(as.integer(readBin(con,'raw',n=1000000)),nrow=20000,byrow=TRUE)+1L
close(con)
r <- fromJSON(file.path(root,'contrasts.json'),simplifyVector=FALSE)
errors <- c()
for (j in 1:7) {
 v <- x[,2*j-1]-x[,2*j]
 means <- rowMeans(matrix(v[i],nrow=20000))
 interval <- quantile(means,c(.025,.975),type=7,names=FALSE)
 observed <- c(mean(v),sd(v),interval,sum(v>0),sum(v==0),sum(v<0),mean((x[,2*j-1]+x[,2*j])/2))
 a <- r$records[[j]]
 expected <- c(a$A_minus_B_mean,a$paired_sample_sd,unlist(a$pointwise_bootstrap_interval_95),a$A_greater_runs,a$equal_runs,a$A_less_runs,a$pooled_breed_mean)
 errors <- c(errors,abs(observed-expected)/pmax(1,abs(expected)))
}
stopifnot(max(errors)<1e-12)
write_json(list(metrics=7,values_checked=length(errors),max_scaled_error=max(errors),scope='Independent R arithmetic on retained endpoint matrix and shared bootstrap draws.'),file.path(root,'r-verification.json'),pretty=TRUE,auto_unbox=TRUE)
