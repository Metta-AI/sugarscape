library(jsonlite)
root <- commandArgs(trailingOnly=TRUE)[[1]]
report <- fromJSON(file.path(root,"analysis.json"),simplifyVector=FALSE)
checked <- 0
for (record in report$records) {
  cells <- read.csv(gzfile(file.path(root,paste0(record$world,"-cells.csv.gz"))))
  peaks <- read.csv(file.path(dirname(root),record$source_folder,record$hotspots_file),header=FALSE)
  stopifnot(nrow(cells)==65536,nrow(peaks)==54)
  dx <- abs(outer(peaks$V2,peaks$V2,"-"));dy <- abs(outer(peaks$V3,peaks$V3,"-"))
  squared <- pmin(dx,256-dx)^2+pmin(dy,256-dy)^2
  minimum <- min(squared[upper.tri(squared)])
  stopifnot(minimum>=400,minimum==record$minimum_wrapped_peak_squared_distance)
  sums <- list()
  for (geometry in c("direct","wrapped")) {
    total <- integer(65536)
    for (i in 1:nrow(peaks)) {
      dx <- abs(cells$x-peaks$V2[[i]]);dy <- abs(cells$y-peaks$V3[[i]])
      if (geometry=="wrapped") {dx<-pmin(dx,256-dx);dy<-pmin(dy,256-dy)}
      squared <- dx*dx+dy*dy
      total <- total + (squared<25) + (squared<100) + (squared<225) + (squared<400)
    }
    sums[[paste0(geometry,"_sum")]] <- total
    for (cap in c(4,7)) sums[[paste0(geometry,"_cap",cap)]] <- pmin(cap,total)
  }
  source <- read.csv(gzfile(file.path(dirname(root),record$source_folder,record$states_file)))
  stopifnot(all(source$cell_capacity==sums$direct_cap4))
  for (name in names(sums)) {
    v <- sums[[name]];stopifnot(all(cells[[name]]==v))
    actual <- c(sum(v),max(v),sum(v>4),sum(v!=source$cell_capacity),sum(v-source$cell_capacity))
    expected <- unlist(record$metrics[[name]],use.names=FALSE)
    stopifnot(all(actual==expected));checked<-checked+length(v)
  }
}
write_json(list(exact_cell_values_checked=checked,worlds=2,method="Independent integer squared-distance band thresholds; all six surfaces and summary quantities checked against original complete host worlds.",scope="Initial landscape only; no GPU simulation or paper-completion verdict."),file.path(root,"r-verification.json"),pretty=TRUE,auto_unbox=TRUE)
