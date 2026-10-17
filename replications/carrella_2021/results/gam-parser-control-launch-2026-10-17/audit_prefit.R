root <- '/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-gam-parser-control-001'
source_dir <- '/Users/relh/Code/workspace/sugarscape-replication-evidence/carrella-2021-source-001'
states <- list();inputs <- list()
for (name in c('original-run_estimator.R','run_estimator.R')) {
  e <- new.env()
  e$args <- c(source_dir,'loess','1250','0',file.path(root,paste0('prefit-',name)))
  expressions <- parse(file.path(root,name))
  stopifnot(as.character(expressions[[1]][[2]])=='args')
  for (expression in expressions[-1]) {
    if (is.call(expression) && identical(expression[[1]],as.name('<-')) && identical(expression[[2]],as.name('result'))) break
    eval(expression,e)
  }
  states[[name]] <- .Random.seed
  inputs[[name]] <- e$total_data
}
stopifnot(identical(states[[1]],states[[2]]),identical(dim(inputs[[1]]),dim(inputs[[2]])))
delta<-as.matrix(inputs[[2]])-as.matrix(inputs[[1]])
stopifnot(all(is.finite(delta)))
report<-list(same_pre_fit_random_state=TRUE,random_state_integers=length(states[[1]]),rows=nrow(delta),columns=ncol(delta),changed_cells=sum(delta!=0),maximum_absolute_delta=max(abs(delta)),columns_with_changes=colnames(delta)[colSums(delta!=0)>0])
saveRDS(states,file.path(root,'prefit-random-states.rds'))
writeLines(jsonlite::toJSON(report,pretty=TRUE,auto_unbox=TRUE,digits=17),file.path(root,'prefit-audit.json'))
print(report)
