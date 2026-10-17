RNGkind("Mersenne-Twister", "Inversion", "Rejection")
setwd("/Users/relh/Code/workspace/sugarscape-nofreelunch-reference")
set.seed(0)
knitr::opts_chunk$set(echo = FALSE, warning= FALSE, message=FALSE,
                      cache=TRUE,cache.extra = knitr::rand_seed,
                      dpi = 300, fig.width = 13.3, fig.height = 10)
library(abctools)
source('./setup.R')
library(tidyverse)
FILENAME<-"sugarscape"
bam_loess<-TRUE
FILTER_TO_1250<-FALSE

saveRDS(list(random_state=.Random.seed, objects=mget(ls(envir=.GlobalEnv), envir=.GlobalEnv)), "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001/setup.rds")
cat("CHECKPOINT setup\n"); flush.console()
# I add to add a "row.number" column name to the file to read this correctly
dr_sumstat<-read_csv("./data/sugarscape/sugarscape.csv",
                     col_names=TRUE) 


dr_sumstat<-
  dr_sumstat %>% select_if(function(x){var(x)>0})


colnames(dr_sumstat) <-
  colnames(dr_sumstat) %>% make.names(unique=TRUE,allow_ = FALSE)


# I add to add a "row.number" column name to the file to read this correctly
dr_parameters<-
  read_csv("./data/sugarscape/params_sugarscape.csv",
                     col_names=TRUE) %>%
  dplyr::select(-`random-seed`)

colnames(dr_parameters) <-
  colnames(dr_parameters) %>% make.names(unique=TRUE,allow_ = FALSE)




total_data<-
  cbind(dr_parameters,dr_sumstat) 

if(FILTER_TO_1250){
  total_data<- total_data %>%
  filter(row_number()<=1250)
}



param_names<-colnames(dr_parameters)
x_names<-colnames(dr_sumstat)
saveRDS(list(random_state=.Random.seed, objects=mget(ls(envir=.GlobalEnv), envir=.GlobalEnv)), "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001/dataprep.rds")
cat("CHECKPOINT dataprep\n"); flush.console()
rejection_cross<-
  cross_validate_abc(total_data,ngroup=5,method="rejection",parameter_colnames = param_names)
print_table(rejection_cross)

saveRDS(list(random_state=.Random.seed, objects=mget(ls(envir=.GlobalEnv), envir=.GlobalEnv)), "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001/rejection.rds")
cat("CHECKPOINT rejection\n"); flush.console()
rejection_cross_sabc<-
  cross_validate_abc(total_data,ngroup=5,method="rejection",parameter_colnames = param_names,
                     semiauto = TRUE)
print_table(rejection_cross_sabc)

saveRDS(list(random_state=.Random.seed, objects=mget(ls(envir=.GlobalEnv), envir=.GlobalEnv)), "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001/rejection-sabc.rds")
cat("CHECKPOINT rejection-sabc\n"); flush.console()
lm_cross<-
  cross_validate_lm(total_data,ngroup=5,
                    parameter_colnames = param_names,x_names=x_names,
                     degree=1)
print_table(lm_cross)

saveRDS(list(random_state=.Random.seed, objects=mget(ls(envir=.GlobalEnv), envir=.GlobalEnv)), "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001/lm.rds")
cat("CHECKPOINT lm\n"); flush.console()
rf_cross<-
  cross_validate_rf(total_data,ngroup=5,
                    parameter_colnames = param_names,x_names=x_names)
print_table(rf_cross)

saveRDS(list(random_state=.Random.seed, objects=mget(ls(envir=.GlobalEnv), envir=.GlobalEnv)), "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001/rf.rds")
cat("CHECKPOINT rf\n"); flush.console()
writeLines(capture.output(sessionInfo()), "/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-notebook-rf-sequence-001/session.txt")
