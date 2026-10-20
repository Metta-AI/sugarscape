library(jsonlite)
library(digest)
args <- commandArgs(trailingOnly=TRUE)
root <- args[[1]]
sources <- fromJSON(file.path(root, 'sources.json'))
expected <- as.matrix(read.csv(file.path(root, 'input-matrix.csv'), header=FALSE))
ticks <- scan(file.path(root, 'ticks.csv'), quiet=TRUE)
x <- matrix(NA_real_, 50, 286)
for (i in seq_len(50)) {
  path <- sources$trajectories$path[[i]]
  stopifnot(digest(file=path, algo='sha256') == sources$trajectories$sha256[[i]])
  frame <- read.csv(path, check.names=FALSE)
  stopifnot(nrow(frame)==20001, all(frame$tick==0:20000))
  x[i,] <- approx(frame$tick, frame[['mean [vision] of group-B']], xout=ticks)$y
}
input_error <- max(abs(x-expected))
stopifnot(input_error < 1e-12)
con <- gzfile(sources$bootstrap,'rb')
bytes <- readBin(con,what='raw',n=1000001)
close(con)
stopifnot(length(bytes)==1000000, digest(bytes,algo='sha256',serialize=FALSE)==sources$bootstrap_uncompressed_sha256)
indices <- matrix(as.integer(bytes)+1L,nrow=20000,byrow=TRUE)
counts <- t(apply(indices,1,tabulate,nbins=50))
mean <- colMeans(x)
se <- sqrt(colSums(sweep(x,2,mean)^2)/49)/sqrt(50)
boot <- counts %*% x / 50
maxima <- apply(abs(sweep(sweep(boot,2,mean),2,se,FUN='/')),1,max)
critical <- unname(quantile(maxima,.95,type=7))
ref <- fromJSON(file.path(root,'summary.json'))
bands <- read.csv(file.path(root,'bands.csv'))
maximum_error <- max(abs(maxima-scan(file.path(root,'bootstrap-maxima.csv'),quiet=TRUE)))
mean_error <- max(abs(mean-bands$mean))
se_error <- max(abs(se-bands$standard_error))
lower <- mean-critical*se
upper <- mean+critical*se
band_error <- max(abs(lower-bands$lower),abs(upper-bands$upper))
overlap <- upper>=bands$paper_lower & lower<=bands$paper_upper
stopifnot(maximum_error<1e-10,mean_error<1e-12,se_error<1e-12,band_error<1e-10,abs(critical-ref$critical)<1e-10,all(as.integer(overlap)==bands$overlap))
write_json(list(runs=50,columns=286,resamples=20000,native_trajectory_values_checked=1000050,input_interpolation_max_abs_error=input_error,bootstrap_maxima_max_abs_error=maximum_error,mean_max_abs_error=mean_error,se_max_abs_error=se_error,band_max_abs_error=band_error,critical=critical,overlaps=sum(overlap),r_version=as.character(getRversion()),scope='Independent R native CSV interpolation and full resampling arithmetic; no independent RNG or inferential validity claim.'),file.path(root,'r-validation.json'),pretty=TRUE,auto_unbox=TRUE,digits=16)
print(critical)
