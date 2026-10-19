# Check whether the released source-history change changes any Sugarscape GAM formula.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3L, !file.exists(args[[3]]))
inputs <- c(`1250` = args[[1]], `5000` = args[[2]])
rows <- list()
formulas <- list()
for (size in names(inputs)) {
  for (fold_number in 1:5) {
    fold <- readRDS(file.path(inputs[[size]], paste0('fold-', fold_number, '.rds')))
    training <- as.data.frame(fold$training)
    parameters <- names(fold$result$predictions)
    predictors <- setdiff(names(training), parameters)
    stopifnot(length(parameters) == 5L, length(predictors) == 146L)
    counts <- vapply(training, function(x) length(unique(x)), integer(1))
    old_small <- sort(names(counts)[counts < 10L])
    new_small <- sort(predictors[counts[predictors] < 10L])
    stopifnot(identical(old_small, new_small))
    old_valid <- setdiff(predictors, old_small)
    new_valid <- setdiff(predictors, new_small)
    stopifnot(identical(old_valid, new_valid))
    for (parameter in parameters) {
      expressions <- character()
      for (small in list(old_small, new_small)) {
        valid <- setdiff(predictors, small)
        small <- small[counts[small] > 1L]
        expression <- paste(parameter, '~', 's(', paste(valid, collapse = ')+s('), ')')
        if (length(small) > 0L) {
          expression <- paste(expression, '+', paste('s(', small, ',k=', pmin(10L, counts[small]), ')', collapse = '+'))
        }
        expressions <- c(expressions, expression)
      }
      stopifnot(identical(expressions[[1]], expressions[[2]]))
      key <- paste(size, fold_number, parameter, sep = '-')
      formulas[[key]] <- expressions[[1]]
      rows[[key]] <- data.frame(size = as.integer(size), fold = fold_number, parameter,
        response_distinct_values = counts[[parameter]], old_and_new_formula_identical = TRUE,
        candidate_response_predictors = length(intersect(old_small, parameters)))
    }
  }
}
dir.create(args[[3]], recursive = TRUE)
write.csv(do.call(rbind, rows), file.path(args[[3]], 'comparison.csv'), row.names = FALSE)
saveRDS(formulas, file.path(args[[3]], 'formulas.rds'))
writeLines(capture.output(sessionInfo()), file.path(args[[3]], 'session.txt'))
cat('All', length(formulas), 'old/new formulas identical across ten folds\n')
