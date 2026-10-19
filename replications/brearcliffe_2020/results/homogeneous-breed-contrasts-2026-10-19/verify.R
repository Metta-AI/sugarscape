library(jsonlite)
root <- commandArgs(trailingOnly=TRUE)[[1]]
repo <- '/Users/relh/Code/workspace/sugarscape-brearcliffe/replications/brearcliffe_2020'
report <- fromJSON(file.path(root, 'contrasts.json'), simplifyVector=FALSE)
endpoints <- read.csv(file.path(root, 'paired-endpoints.csv'), check.names=FALSE)
audit <- fromJSON('/Users/relh/Code/workspace/sugarscape-replication-evidence/brearcliffe-released-recovery-audited-001/union-audit/audit.json')
field <- function(metric, breed) {
  if (metric == 'combat') return(sprintf('combat-agent-%s-die', tolower(breed)))
  if (metric == 'starvation') return(sprintf('starve-agent-%s-die', tolower(breed)))
  if (metric == 'max_age') return(sprintf('max [age] of group-%s', breed))
  sprintf('mean [%s] of group-%s', metric, breed)
}
errors <- c()
raw_errors <- c()
for (pair in c(0,5,10,15)) {
  selected <- Filter(function(x) x$pair_index == pair, report$records)
  stopifnot(length(selected) == 7)
  folder <- file.path(repo, 'results', paste0(selected[[1]]$pairing, '-complete-cohort-2026-10-19'))
  summary <- fromJSON(file.path(folder, 'cohort-summary.json'))
  side <- 'A'
  other <- 'B'
  d <- endpoints[endpoints$pair_index == pair, ]
  stopifnot(nrow(d) == 50, all(d$run_id == sprintf('released-code-pair-%02d-repeat-%02d', pair, 0:49)))
  for (k in 1:50) {
    row <- audit$completed[audit$completed$run_id == d$run_id[[k]], ]
    stopifnot(nrow(row) == 1)
    lines <- readLines(file.path(row$directory, 'trajectory.csv'))
    stopifnot(length(lines) == 20002)
    last <- read.csv(text=paste(lines[[1]], lines[[20002]], sep='\n'), check.names=FALSE)
    stopifnot(last$tick == 20000)
    for (metric in c('sugar','vision','metabolism','combat','starvation','age','max_age')) {
      actual <- c(last[[field(metric,side)]], last[[field(metric,other)]])
      expected <- c(d[[paste0(metric,'_A')]][[k]], d[[paste0(metric,'_B')]][[k]])
      raw_errors <- c(raw_errors, abs(actual-expected)/pmax(1,abs(expected)))
    }
  }
  con <- gzfile(file.path(folder, 'bootstrap-indices.u8.gz'), 'rb')
  indices <- matrix(as.integer(readBin(con, 'raw', n=1000000)), nrow=20000, byrow=TRUE)+1L
  close(con)
  stopifnot(all(dim(indices)==c(20000,50)), min(indices)>=1, max(indices)<=50)
  for (record in selected) {
    metric <- record$metric
    values <- d[[paste0(metric,'_A')]] - d[[paste0(metric,'_B')]]
    draws <- rowMeans(matrix(values[indices], nrow=20000))
    interval <- quantile(draws,c(.025,.975),type=7,names=FALSE)
    actual <- c(mean(d[[paste0(metric,'_A')]]),mean(d[[paste0(metric,'_B')]]),mean(values),sd(values),interval,sum(values>0),sum(values==0),sum(values<0))
    expected <- c(record$A_endpoint_mean,record$B_endpoint_mean,record$paired_endpoint_mean,record$paired_endpoint_sample_sd,unlist(record$pointwise_bootstrap_interval_95),record$endpoint_positive_runs,record$endpoint_equal_runs,record$endpoint_negative_runs)
    errors <- c(errors,abs(actual-expected)/pmax(1,abs(expected)))

  }
}
stopifnot(length(raw_errors)==2800, length(errors)==252, max(raw_errors)<1e-12, max(errors)<1e-12)
write_json(list(contrasts=28,raw_endpoint_values_checked=length(raw_errors),raw_endpoint_max_scaled_error=max(raw_errors),summary_values_checked=length(errors),summary_max_scaled_error=max(errors),scope='Independent R reopens all 200 raw trajectories to validate breed/metric mapping and endpoints, then recomputes paired bootstrap intervals from the frozen whole-run draws. No simultaneous coverage or full-paper verdict.'),file.path(root,'r-verification.json'),pretty=TRUE,auto_unbox=TRUE,null='null',digits=17)
