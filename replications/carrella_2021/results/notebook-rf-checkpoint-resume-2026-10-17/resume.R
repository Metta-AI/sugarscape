RNGkind("Mersenne-Twister", "Inversion", "Rejection")
setwd("/Users/relh/Code/workspace/sugarscape-nofreelunch-reference")
source("./setup.R")
checkpoint <- readRDS("/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001/lm.rds")
list2env(checkpoint$objects, envir=.GlobalEnv)
.Random.seed <- checkpoint$random_state
stopifnot(identical(.Random.seed, checkpoint$random_state),
          identical(mget(names(checkpoint$objects), envir=.GlobalEnv), checkpoint$objects),
          nrow(total_data)==5000, length(param_names)==5, length(x_names)==146)
writeLines(jsonlite::toJSON(list(objects_restored=length(checkpoint$objects),
  random_state_integers=length(.Random.seed), exact_object_and_rng_match=TRUE),auto_unbox=TRUE),
  "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-resume-001/restore-verification.json")
rm(checkpoint)
writeLines(capture.output(sessionInfo()), "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-resume-001/session.txt")
rf_cross<-
  cross_validate_rf(total_data,ngroup=5,
                    parameter_colnames = param_names,x_names=x_names)
print_table(rf_cross)


saveRDS(list(random_state=.Random.seed, objects=mget(ls(envir=.GlobalEnv), envir=.GlobalEnv)), "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-resume-001/rf.rds")
cat("CHECKPOINT rf\n"); flush.console()
