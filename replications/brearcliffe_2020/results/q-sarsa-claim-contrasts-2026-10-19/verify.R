library(jsonlite)
root <- commandArgs(trailingOnly=TRUE)[[1]]
repo <- '/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020'
report <- fromJSON(file.path(root, 'contrasts.json'), simplifyVector=FALSE)
endpoints <- read.csv(file.path(root, 'paired-endpoints.csv'), check.names=FALSE)
audit <- fromJSON(file.path(dirname(root), 'brearcliffe-sarsa-q-snapshot-002/union-audit/audit.json'))
field <- function(metric, breed) {
  stopifnot(metric == 'sugar')
  sprintf('mean [sugar] of group-%s', breed)
}
errors <- c()
raw_errors <- c()
ranges <- list()
for (pair in c(11,14)) {
  selected <- Filter(function(x) x$pair_index == pair, report$records)
  stopifnot(length(selected) == 1)
  folder <- file.path(repo, 'results', paste0(selected[[1]]$pairing, '-complete-cohort-2026-10-19'))
  summary <- fromJSON(file.path(folder, 'cohort-summary.json'))
  side <- if (summary$group_A == 'Q-Learning') 'A' else 'B'
  other <- if (side == 'A') 'B' else 'A'
  d <- endpoints[endpoints$pair_index == pair, ]
  stopifnot(nrow(d) == 50, all(d$run_id == sprintf('released-code-pair-%02d-repeat-%02d', pair, 0:49)))
  for (k in 1:50) {
    row <- audit$completed[audit$completed$run_id == d$run_id[[k]], ]
    stopifnot(nrow(row) == 1)
    lines <- readLines(file.path(row$directory, 'trajectory.csv'))
    stopifnot(length(lines) == 20002)
    last <- read.csv(text=paste(lines[[1]], lines[[20002]], sep='\n'), check.names=FALSE)
    stopifnot(last$tick == 20000)
    for (metric in c('sugar')) {
      actual <- c(last[[field(metric,side)]], last[[field(metric,other)]])
      expected <- c(d[[paste0(metric,'_q')]][[k]], d[[paste0(metric,'_opponent')]][[k]])
      raw_errors <- c(raw_errors, abs(actual-expected)/pmax(1,abs(expected)))
    }
  }
  con <- gzfile(file.path(folder, 'bootstrap-indices.u8.gz'), 'rb')
  indices <- matrix(as.integer(readBin(con, 'raw', n=1000000)), nrow=20000, byrow=TRUE)+1L
  close(con)
  stopifnot(all(dim(indices)==c(20000,50)), min(indices)>=1, max(indices)<=50)
  means <- read.csv(gzfile(file.path(folder,'means.csv.gz')), check.names=FALSE)
  stopifnot(all(means$tick == 0:20000))
  for (record in selected) {
    metric <- record$metric
    values <- d[[paste0(metric,'_q')]] - d[[paste0(metric,'_opponent')]]
    draws <- rowMeans(matrix(values[indices], nrow=20000))
    interval <- quantile(draws,c(.025,.975),type=7,names=FALSE)
    curve <- means[[field(metric,side)]] - means[[field(metric,other)]]
    ticks <- means$tick[-1]
    after <- curve[-1]
    actual <- c(mean(d[[paste0(metric,'_q')]]),mean(d[[paste0(metric,'_opponent')]]),mean(values),sd(values),interval,sum(values>0),sum(values==0),sum(values<0),curve[[1]],sum(after>0),sum(after==0),sum(after<0),min(after),max(after))
    expected <- c(record$q_endpoint_mean,record$opponent_endpoint_mean,record$paired_endpoint_mean,record$paired_endpoint_sample_sd,unlist(record$pointwise_bootstrap_interval_95),record$endpoint_positive_runs,record$endpoint_equal_runs,record$endpoint_negative_runs,record$initial_mean_difference,record$post_initial_positive_ticks,record$post_initial_equal_ticks,record$post_initial_negative_ticks,record$minimum_post_initial_difference,record$maximum_post_initial_difference)
    errors <- c(errors,abs(actual-expected)/pmax(1,abs(expected)))
    negative <- ticks[after<0]
    ranges[[length(ranges)+1]] <- list(pair_index=pair,metric=metric,negative_ticks=length(negative),first_negative_tick=if(length(negative)) min(negative) else NULL,last_negative_tick=if(length(negative)) max(negative) else NULL)
  }
}
stopifnot(length(raw_errors)==200, length(errors)==30, max(raw_errors)<1e-12, max(errors)<1e-12)
write_json(list(contrasts=2,raw_endpoint_values_checked=length(raw_errors),raw_endpoint_max_scaled_error=max(raw_errors),summary_values_checked=length(errors),summary_max_scaled_error=max(errors),negative_tick_ranges=ranges,scope='Independent R reopens all 100 raw trajectories to validate breed/metric mapping and endpoints, then recomputes paired bootstrap intervals and complete-curve sign counts. No simultaneous coverage or full-paper verdict.'),file.path(root,'r-verification.json'),pretty=TRUE,auto_unbox=TRUE,null='null')
