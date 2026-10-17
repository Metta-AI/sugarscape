# Audit the complete original-notebook forest against retained isolated results.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==4L)
checkpoint_path <- args[[1]]
predecessor_path <- args[[2]]
prior <- args[[3]]
output <- args[[4]]
stopifnot(!dir.exists(output))
dir.create(output,recursive=TRUE)
x <- readRDS(checkpoint_path)
data <- x$objects$total_data
parameters <- x$objects$param_names
result <- x$objects$rf_cross
stopifnot(nrow(data)==5000, length(parameters)==5, length(result$results)==5, !anyDuplicated(data))
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(0)
permutation <- sample(seq_len(5000))
errors <- coverage <- width <- baseline <- matrix(NA_real_,5,5)
max_prediction_difference <- 0
previous <- read.csv(file.path(prior,"validation/predictions.csv"))
exports <- list()
stopifnot(nrow(previous)==25000)
for (fold in seq_len(5)) {
  ids <- sort(permutation[((fold-1)*1000+1):(fold*1000)])
  truth <- as.matrix(data[ids,parameters])
  train <- as.matrix(data[-ids,parameters])
  saved <- result$results[[fold]]
  pred <- as.matrix(saved$predictions)
  low <- as.matrix(saved$lows)
  high <- as.matrix(saved$highs)
  stopifnot(identical(dim(pred),dim(truth)),all(is.finite(pred)),all(low<=high))
  errors[fold,] <- sqrt(colMeans((pred-truth)^2))
  coverage[fold,] <- colMeans(truth>=low & truth<=high)
  width[fold,] <- colMeans(high-low)
  baseline[fold,] <- sqrt(colMeans(sweep(truth,2,colMeans(train),"-")^2))
  stopifnot(max(abs(errors[fold,]-saved$errors))<1e-10,
            max(abs(coverage[fold,]-saved$contained))<1e-10,
            max(abs(width[fold,]-saved$interval_size))<1e-10)
  exports[[fold]] <- data.frame(fold=fold,row=rep(ids,5),parameter=rep(parameters,each=1000),truth=as.vector(truth),prediction=as.vector(pred),low=as.vector(low),high=as.vector(high))
  for (column in seq_along(parameters)) {
    prior_rows <- previous[previous$fold==fold & previous$parameter==parameters[column],]
    prior_rows <- prior_rows[order(prior_rows$test_row),]
    stopifnot(identical(prior_rows$test_row,seq_len(1000)),max(abs(prior_rows$truth-truth[,column]))<1e-10)
    max_prediction_difference <- max(max_prediction_difference,abs(pred[,column]-prior_rows$prediction))
  }
}
stopifnot(max(abs(colMeans(errors)-result$errors))<1e-10,
          max(abs(colMeans(coverage)-result$contained))<1e-10,
          max(abs(colMeans(width)-result$interval_size))<1e-10)
performance <- 1-colMeans(errors)/colMeans(baseline)
published <- c(.475,.536,.446,.463,.790)
comparison <- data.frame(parameter=parameters,rmse=colMeans(errors),baseline_rmse=colMeans(baseline),performance=performance,published=published,matches_printed_precision=round(performance,3)==published,coverage=colMeans(coverage),interval_width=colMeans(width))
report <- list(held_out_rows=5000,predictions_audited=25000,folds=5,comparison=comparison,
  maximum_prediction_difference_from_isolated_run=max_prediction_difference,
  rng_state_unchanged_since_lm=identical(x$random_state,readRDS(predecessor_path)$random_state),
  scope="Saved quantile random forest checkpoint; independent arithmetic uses saved predictions and reconstructed original folds. Attribution requires separate data and random-state controls.")
writeLines(jsonlite::toJSON(report,auto_unbox=TRUE,pretty=TRUE,digits=17),file.path(output,"audit.json"))
print(report)

write.csv(do.call(rbind,exports),file.path(output,"predictions.csv"),row.names=FALSE)
writeLines(capture.output(sessionInfo()),file.path(output,"session.txt"))
