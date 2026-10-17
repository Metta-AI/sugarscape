RNGkind("Mersenne-Twister", "Inversion", "Rejection")
setwd("/Users/relh/Code/workspace/sugarscape-nofreelunch-reference")
source("./setup.R")
checkpoint <- readRDS("/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001/lm.rds")
list2env(checkpoint$objects, envir=.GlobalEnv)
.Random.seed <- checkpoint$random_state
stopifnot(identical(.Random.seed, checkpoint$random_state),
          identical(mget(names(checkpoint$objects), envir=.GlobalEnv), checkpoint$objects),
          nrow(total_data)==5000, length(param_names)==5, length(x_names)==146)
parameters <- read.csv("data/sugarscape/params_sugarscape.csv",check.names=FALSE)
parameters[["random-seed"]] <- NULL
summaries <- read.csv("data/sugarscape/sugarscape.csv",check.names=FALSE)
summaries <- summaries[vapply(summaries,var,numeric(1))>0]
names(parameters) <- make.names(names(parameters),unique=TRUE,allow_=FALSE)
names(summaries) <- make.names(names(summaries),unique=TRUE,allow_=FALSE)
control_data <- cbind(parameters,summaries)
stopifnot(identical(names(control_data),names(total_data)), identical(dim(control_data),dim(total_data)))
maximum_parser_difference <- max(abs(as.matrix(control_data)-as.matrix(total_data)))
stopifnot(maximum_parser_difference<1e-10)
# Compare every held-out/training input against the retained isolated run.
RNGkind("Mersenne-Twister","Inversion","Rejection")
set.seed(0)
permutation <- sample(seq_len(5000))
for (fold in seq_len(5)) {
  ids <- sort(permutation[((fold-1)*1000+1):(fold*1000)])
  prior <- readRDS(file.path("/Users/relh/Code/workspace/sugarscape-carrella/replications/carrella_2021/results/rf-5000-2026-10-15",paste0("fold-",fold,".rds")))
  a <- control_data[ids,]; b <- control_data[-ids,]
  rownames(a) <- NULL; rownames(b) <- NULL
  stopifnot(identical(a,prior$testing),identical(b,prior$training))
}
total_data <- control_data
.Random.seed <- checkpoint$random_state
stopifnot(identical(.Random.seed,checkpoint$random_state))
writeLines(jsonlite::toJSON(list(input_cells=length(as.matrix(total_data)),maximum_parser_difference=maximum_parser_difference,
  all_five_folds_match_isolated_inputs=TRUE,exact_sequential_rng_restored=TRUE),auto_unbox=TRUE,digits=17),
  "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-parser-control-001/restoration.json")
rm(checkpoint)
writeLines(capture.output(sessionInfo()), "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-parser-control-001/session.txt")
rf_cross<-
  cross_validate_rf(total_data,ngroup=5,
                    parameter_colnames = param_names,x_names=x_names)
print_table(rf_cross)


saveRDS(list(random_state=.Random.seed, objects=mget(ls(envir=.GlobalEnv), envir=.GlobalEnv)), "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-parser-control-001/rf.rds")
cat("CHECKPOINT rf\n"); flush.console()
