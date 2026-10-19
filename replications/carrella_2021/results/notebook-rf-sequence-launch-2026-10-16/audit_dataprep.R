root <- "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001"
source <- "/Users/relh/Code/workspace/sugarscape-nofreelunch-reference"
checkpoint <- readRDS(file.path(root, "dataprep.rds"))
parameters <- read.csv(file.path(source, "data/sugarscape/params_sugarscape.csv"), check.names=FALSE)
parameters[["random-seed"]] <- NULL
summaries <- read.csv(file.path(source, "data/sugarscape/sugarscape.csv"), check.names=FALSE)
constant <- names(summaries)[vapply(summaries, var, numeric(1)) == 0]
summaries <- summaries[vapply(summaries, var, numeric(1)) > 0]
names(parameters) <- make.names(names(parameters), unique=TRUE, allow_=FALSE)
names(summaries) <- make.names(names(summaries), unique=TRUE, allow_=FALSE)
expected <- cbind(parameters, summaries)
actual <- checkpoint$objects$total_data
stopifnot(identical(dim(actual), c(5000L,151L)), identical(names(actual), names(expected)))
error <- max(abs(as.matrix(actual)-as.matrix(expected)))
stopifnot(error < 1e-10, identical(checkpoint$objects$param_names,names(parameters)),
          identical(checkpoint$objects$x_names,names(summaries)))
# Compare actual saved fold inputs from the already-completed isolated workflow.
fold <- readRDS("/Users/relh/Code/workspace/sugarscape-carrella/replications/carrella_2021/results/rf-5000-2026-10-15/fold-1.rds")
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(0)
permutation <- sample(seq_len(nrow(actual)))
held_out <- sort(permutation[1:1000])
stopifnot(isTRUE(all.equal(as.matrix(fold$testing),as.matrix(actual[held_out,]),check.attributes=FALSE,tolerance=1e-10)))
report <- list(rows=nrow(actual), columns=ncol(actual), numeric_cells=length(as.matrix(actual)),
               maximum_parser_difference=error, removed_constant_columns=constant,
               original_parameter_order=names(parameters),
               first_fold_matches_isolated_run=TRUE,
               scope="Actual notebook data checkpoint agrees with independent base-R parsing and first saved isolated fold. Later random streams and estimator outcomes remain untested.")
writeLines(jsonlite::toJSON(report,auto_unbox=TRUE,pretty=TRUE,digits=17),file.path(root,"dataprep-audit.json"))
print(report)
