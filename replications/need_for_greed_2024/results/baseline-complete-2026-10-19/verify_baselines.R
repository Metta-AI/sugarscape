args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==4L, !file.exists(args[[4]]))
original <- unzip(args[[1]], list=TRUE)$Name
inventory <- jsonlite::fromJSON(args[[2]])
report <- jsonlite::fromJSON(args[[3]], simplifyVector=FALSE)
stopifnot(!anyDuplicated(inventory$runs$entry))
prefixes <- c("altruisticHalfLookaheadBinary", "egoisticHalfLookaheadBinary", "benthamHalfLookaheadBinary")
labels <- c("table_I", "table_II", "table_III")
published <- list(c(67,2,31), c(62,2,36), c(0,0,100))
results <- vector("list", 3L)
seen <- character()
for (i in seq_along(prefixes)) {
  expected <- sort(original[grepl(paste0("^",prefixes[[i]],"[0-9]+\\.config$"), original)])
  stopifnot(length(expected)==100L, !anyDuplicated(expected), !any(expected %in% seen))
  seen <- c(seen, expected)
  rows <- inventory$runs[inventory$runs$entry %in% expected, ]
  stopifnot(nrow(rows)==100L, identical(sort(rows$entry), expected))
  population <- rows$final_population
  stopifnot(all(is.finite(population)), all(population>=0), all(population==floor(population)))
  counts <- c(sum(population==0), sum(population>0 & population<=250), sum(population>250))
  released <- c(sum(population==0), sum(population>0 & population<250), sum(population>=250))
  stopifnot(sum(counts)==100L, sum(released)==100L)
  target <- Filter(function(x) x$label==labels[[i]], report$rows)
  stopifnot(length(target)==1L)
  target <- target[[1]]
  stopifnot(isTRUE(target$complete), target$required_inputs==100L, target$audited_inputs==100L,
            length(target$missing_entries)==0L, target$equal_initial_population==sum(population==250))
  stopifnot(all(unlist(target$paper_counts[c("extinct","worse","better")])==counts),
            all(unlist(target$released_plot_counts[c("extinct","worse","better")])==released),
            all(unlist(target$published_percentages)==published[[i]]),
            all(unlist(target$complete_percentages)==counts),
            all(unlist(target$complete_percentage_point_differences)==counts-published[[i]]))
  results[[i]] <- list(label=labels[[i]], original_inputs=100L, audited_inputs=100L,
                      observations=sum(rows$observations), paper_counts=counts,
                      released_plot_counts=released, percentages=counts,
                      published_percentages=published[[i]],
                      percentage_point_differences=counts-published[[i]],
                      equal_initial_population=sum(population==250))
}
stopifnot(length(seen)==300L, report$complete_rows==3L, report$audited_table_inputs==300L)
result <- list(original_inputs=300L, rows=results,
               scope="Independent R census selected directly from original ZIP filenames. Verifies Tables I-III arithmetic on audited endpoints, not an independent simulation, raw trajectory audit, or whole-paper verdict.")
jsonlite::write_json(result,args[[4]],auto_unbox=TRUE,pretty=TRUE,digits=17)
print(result)
