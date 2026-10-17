args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==3L)
a <- readRDS(args[[1]])
b <- readRDS(args[[2]])
stopifnot(identical(a$objects$param_names,b$objects$param_names))
parameters <- a$objects$param_names
metrics <- list()
for (p in parameters) {
  x <- unlist(lapply(a$objects$rf_cross$results,function(fold)fold$predictions[[p]]))
  y <- unlist(lapply(b$objects$rf_cross$results,function(fold)fold$predictions[[p]]))
  stopifnot(length(x)==5000,length(y)==5000,all(is.finite(c(x,y))))
  metrics[[p]] <- list(predictions=5000,exactly_equal=sum(x==y),maximum_absolute_difference=max(abs(x-y)),mean_absolute_difference=mean(abs(x-y)))
}
columns <- names(a$objects$total_data)
input_differences <- lapply(columns,function(name)list(column=name,different_cells=sum(a$objects$total_data[[name]]!=b$objects$total_data[[name]]),maximum_absolute_difference=max(abs(a$objects$total_data[[name]]-b$objects$total_data[[name]]))))
input_differences <- Filter(function(x)x$different_cells>0,input_differences)
report <- list(comparison="Sequential original notebook versus fixed-sequential-RNG base-R parser control",input_differences=input_differences,predictions=metrics,final_rng_identical=identical(a$random_state,b$random_state),aggregate_errors_difference=unname(b$objects$rf_cross$errors-a$objects$rf_cross$errors),scope="Both workflows use the same pre-forest random state, source, five-fold partitions and runtime. This control isolates changed parsed total_data; no paper-level negative verdict.")
writeLines(jsonlite::toJSON(report,pretty=TRUE,auto_unbox=TRUE,digits=17),args[[3]])
print(report)
