args <- commandArgs(trailingOnly=TRUE)
root <- args[[1]]
expected <- list('common-one'=c(86143,58278,76,83), 'common-multi'=c(89027,61041,76,86))
for (variant in names(expected)) {
  x <- read.csv(file.path(root,variant,'health.csv'))
  failed <- !is.finite(x$Sugar_Level) | !is.finite(x$Spice_Level)
  actual <- c(nrow(x),sum(failed),min(x$Step[failed]),length(unique(x$Agent[x$Step==1000])))
  stopifnot(identical(as.numeric(actual),expected[[variant]]))
  cat(variant,actual,'\n')
}
