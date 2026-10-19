args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==3L)
cells <- 0L
for (fold in 1:5) {
  original <- readRDS(file.path(args[[1]],paste0('fold-',fold,'.rds')))
  repeated <- readRDS(file.path(args[[2]],paste0('fold-',fold,'.rds')))
  stopifnot(identical(original$training,repeated$training), identical(original$testing,repeated$testing))
  cells <- cells + length(as.matrix(original$training)) + length(as.matrix(original$testing))
}
jsonlite::write_json(list(folds=5L, exact_input_cells=cells, primary=args[[1]], run=args[[2]]),args[[3]],auto_unbox=TRUE,pretty=TRUE)
