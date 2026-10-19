args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==3L, !file.exists(args[[3]]))
rows <- list()
for (seed in 7:8) {
  for (fold in 1:5) {
    baseline <- readRDS(file.path(args[[1]], paste0('fold-',fold,'.rds')))
    current <- readRDS(file.path(args[[2]], sprintf('seed-%02d',seed),'run',paste0('fold-',fold,'.rds')))
    for (quantity in c('predictions','lows','highs')) {
      a <- as.matrix(baseline[[quantity]])
      b <- as.matrix(current[[quantity]])
      stopifnot(identical(dim(a),c(250L,5L)),identical(dim(a),dim(b)),identical(colnames(a),colnames(b)),all(is.finite(a)),all(is.finite(b)))
      rows[[length(rows)+1L]] <- data.frame(seed,fold,quantity,values=length(a),changed=sum(a!=b),identical_values=identical(as.numeric(a),as.numeric(b)),max_absolute_change=max(abs(a-b)),rng_state_identical=identical(baseline$random_state,current$random_state))
    }
  }
}
result <- do.call(rbind,rows)
jsonlite::write_json(list(comparisons=result,scope='Exact matrix comparisons against completed historical seed0. Seeds7 and8 only; no final sensitivity range or historical author RNG identification.'),args[[3]],pretty=TRUE,auto_unbox=TRUE,digits=17)
print(aggregate(cbind(values,changed)~seed+quantity,result,sum))
