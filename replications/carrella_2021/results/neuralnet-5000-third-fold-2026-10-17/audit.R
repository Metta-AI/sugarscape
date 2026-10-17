args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==3)
source <- args[[1]]
output <- args[[2]]
x <- readRDS(args[[3]])
parameters <- read.csv(file.path(source,"data/sugarscape/params_sugarscape.csv"),check.names=FALSE)
parameters[["random-seed"]] <- NULL
summaries <- read.csv(file.path(source,"data/sugarscape/sugarscape.csv"),check.names=FALSE)
summaries <- summaries[vapply(summaries,var,numeric(1))>0]
names(parameters)<-make.names(names(parameters),unique=TRUE,allow_=FALSE)
names(summaries)<-make.names(names(summaries),unique=TRUE,allow_=FALSE)
data <- cbind(parameters,summaries)
RNGkind("Mersenne-Twister","Inversion","Rejection")
set.seed(0)
ids <- sort(sample(seq_len(5000))[2001:3000])
expected_test <- data[ids,]
expected_train <- data[-ids,]
rownames(expected_test) <- NULL
rownames(expected_train) <- NULL
stopifnot(identical(x$testing,expected_test),identical(x$training,expected_train),ncol(data)==151)
pred <- as.matrix(x$result$medians)
truth <- as.matrix(x$testing[names(parameters)])
low <- as.matrix(x$result$lows)
high <- as.matrix(x$result$highs)
stopifnot(identical(dim(pred),c(1000L,5L)),identical(dim(low),dim(pred)),identical(dim(high),dim(pred)),all(is.finite(c(pred,truth,low,high))),all(low<=high))
rmse <- sqrt(colMeans((pred-truth)^2))
coverage <- colMeans(truth>=low & truth<=high)
width <- colMeans(high-low)
baseline <- sqrt(colMeans(sweep(truth,2,colMeans(as.matrix(x$training[names(parameters)])),"-")^2))
stopifnot(max(abs(rmse-x$result$errors))<1e-10,max(abs(coverage-x$result$contained))<1e-10,max(abs(width-x$result$interval_size))<1e-10)
report <- list(fold=3,training_rows=4000,held_out_rows=1000,predictions=5000,input_cells_checked=755000,exact_original_fold_alignment=TRUE,
  statistics=data.frame(parameter=names(parameters),rmse=rmse,baseline_rmse=baseline,fold_performance=1-rmse/baseline,coverage=coverage,interval_width=width),
  scope="One completed fold of the original five-fold neural-network workflow. No aggregate Table8 score or new completed target is claimed.")
writeLines(jsonlite::toJSON(report,pretty=TRUE,auto_unbox=TRUE,digits=17),file.path(output,"audit.json"))
write.csv(data.frame(row=rep(ids,5),parameter=rep(names(parameters),each=1000),truth=as.vector(truth),prediction=as.vector(pred),low=as.vector(low),high=as.vector(high)),file.path(output,"predictions.csv"),row.names=FALSE)
print(report)
