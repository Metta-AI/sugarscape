library(jsonlite)
root <- commandArgs(trailingOnly=TRUE)[[1]]
protocol <- fromJSON(file.path(root, "native/protocol.json"), simplifyVector=FALSE)
results <- list()
for (variant in protocol$variants) {
  name <- variant$variant
  cells <- read.csv(file.path(root, "native/runs", name, "initial-cells.csv"))
  lines <- readLines(file.path(root, "native", paste0(name, "-native.log")))
  peaks <- read.csv(text=paste(grep("^HOTSPOT,", lines, value=TRUE), collapse="\n"), header=FALSE)
  stopifnot(nrow(cells)==65536, nrow(peaks)==54)
  total <- integer(nrow(cells))
  for (i in seq_len(nrow(peaks))) {
    dx <- abs(cells$x-peaks$V2[[i]])
    dy <- abs(cells$y-peaks$V3[[i]])
    if (variant$wrapped_cell_distances) {
      dx <- pmin(dx,256-dx)
      dy <- pmin(dy,256-dy)
    }
    squared <- dx*dx+dy*dy
    total <- total+(squared<25)+(squared<100)+(squared<225)+(squared<400)
  }
  expected <- pmin(variant$capacity_maximum,total)
  stopifnot(all(cells$cell_capacity==expected),all(cells$cell_sugar==expected))
  active <- cells[cells$status==1,]
  stopifnot(all(active$metabolism>=1),all(active$metabolism<=variant$metabolism_maximum))
  results[[name]] <- list(cells=nrow(cells), total_initial_sugar=sum(expected),
                         maximum_initial_capacity=max(expected), occupied=nrow(active))
}
write_json(list(variants=results, exact_cells_checked=9*65536,
                scope="Independent R landscape arithmetic on all nine native initial worlds; no independent GPU conflict-winner or random-stream reconstruction."),
           file.path(root,"r-initializer-verification.json"),pretty=TRUE,auto_unbox=TRUE)
