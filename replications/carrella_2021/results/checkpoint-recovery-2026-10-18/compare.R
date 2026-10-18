args <- commandArgs(TRUE)
original <- args[[1]]
resumed <- args[[2]]
for (fold in 1:5) {
  a <- readRDS(file.path(original, paste0("fold-", fold, ".rds")))
  b <- readRDS(file.path(resumed, paste0("fold-", fold, ".rds")))
  stopifnot(identical(a, b))
}
stopifnot(identical(readRDS(file.path(original,"complete.rds")),readRDS(file.path(resumed,"complete.rds"))))
stopifnot(identical(readLines(file.path(original,"metrics.csv")),readLines(file.path(resumed,"metrics.csv"))))
cat("All five full fold objects, predictions, intervals, RNG states and aggregate metrics are identical.\n")
