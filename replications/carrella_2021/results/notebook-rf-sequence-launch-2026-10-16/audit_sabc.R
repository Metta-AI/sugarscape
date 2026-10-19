root <- "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001"
prior <- "/Users/relh/Code/workspace/sugarscape-carrella/replications/carrella_2021/results/sabc4d-5000-clean-2026-10-15"
x <- readRDS(file.path(root,"rejection-sabc.rds"))
data <- x$objects$total_data
parameters <- x$objects$param_names
result <- x$objects$rejection_cross_sabc
stopifnot(nrow(data)==5000, length(parameters)==5, length(result$results)==5, !anyDuplicated(data))
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(0)
permutation <- sample(seq_len(5000))
errors <- coverage <- width <- baseline <- matrix(NA_real_,5,5)
max_prediction_difference <- 0
for (fold in seq_len(5)) {
  ids <- sort(permutation[((fold-1)*1000+1):(fold*1000)])
  truth <- as.matrix(data[ids,parameters])
  train <- as.matrix(data[-ids,parameters])
  saved <- result$results[[fold]]
  pred <- as.matrix(saved$medians)
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
  previous <- readRDS(file.path(prior,paste0("fold-",fold,".rds")))
  stopifnot(max(abs(as.matrix(previous$testing)-as.matrix(data[ids,])))<1e-10)
  max_prediction_difference <- max(max_prediction_difference,abs(pred-as.matrix(previous$result$medians)))
}
stopifnot(max(abs(colMeans(errors)-result$errors))<1e-10,
          max(abs(colMeans(coverage)-result$contained))<1e-10,
          max(abs(colMeans(width)-result$interval_size))<1e-10)
performance <- 1-colMeans(errors)/colMeans(baseline)
published <- c(.509,.449,.458,.476,.624)
comparison <- data.frame(parameter=parameters,rmse=colMeans(errors),baseline_rmse=colMeans(baseline),performance=performance,published=published,matches_printed_precision=round(performance,3)==published,coverage=colMeans(coverage),interval_width=colMeans(width))
report <- list(held_out_rows=5000,predictions_audited=25000,folds=5,comparison=comparison,
  maximum_prediction_difference_from_isolated_run=max_prediction_difference,
  rng_state_unchanged_since_rejection=identical(x$random_state,readRDS(file.path(root,"rejection.rds"))$random_state),
  scope="Sequential original notebook semi-automatic4DABC checkpoint only; later estimators remain running. Independent arithmetic uses saved predictions and reconstructed original folds.")
writeLines(jsonlite::toJSON(report,auto_unbox=TRUE,pretty=TRUE,digits=17),file.path(root,"sabc-audit.json"))
print(report)
