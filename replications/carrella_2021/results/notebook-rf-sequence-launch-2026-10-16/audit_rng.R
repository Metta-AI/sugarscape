root <- "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001"
setup <- readRDS(file.path(root,"setup.rds"))
data <- readRDS(file.path(root,"dataprep.rds"))
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(0)
seed_zero <- .Random.seed
report <- list(setup_equals_seed_zero=identical(setup$random_state,seed_zero),
               dataprep_equals_setup=identical(data$random_state,setup$random_state),
               dataprep_equals_seed_zero=identical(data$random_state,seed_zero),
               state_lengths=c(length(setup$random_state),length(data$random_state)),
               scope="Actual saved notebook setup/dataprep states compared in separate process. No live random state modified; no estimator verdict.")
writeLines(jsonlite::toJSON(report,auto_unbox=TRUE,pretty=TRUE),file.path(root,"rng-audit.json"))
print(report)
