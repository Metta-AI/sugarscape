# Independently reconstruct overlap categories from the pinned source intervals.
library(jsonlite)
library(digest)
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 3L, !file.exists(args[3]))
report <- fromJSON(args[2], simplifyVector = FALSE)
summaries <- list()
comparisons <- list()
for (name in names(report$source_sha256)) {
  path <- file.path(args[1], name)
  stopifnot(digest(file = path, algo = "sha256") == report$source_sha256[[name]])
  if (endsWith(name, "cohort-summary.json")) {
    s <- fromJSON(path, simplifyVector = FALSE)
    key <- paste(s$group_A, s$group_B, s$interpretation, sep = "/")
    stopifnot(!key %in% names(summaries))
    summaries[[key]] <- s
  }
  if (endsWith(name, "curve-comparison.json.gz")) {
    connection <- gzfile(path, "rt")
    c <- fromJSON(paste(readLines(connection), collapse = "\n"), simplifyVector = FALSE)
    close(connection)
    key <- paste(c$group_A, c$group_B, c$interpretation, sep = "/")
    stopifnot(!key %in% names(comparisons))
    comparisons[[key]] <- c
  }
}
stopifnot(length(summaries) == 20L, length(comparisons) == 20L)
categories <- c("both_overlap", "released_only", "paper_only", "neither_overlap", "unresolved")
totals <- setNames(integer(5), categories)
curves_checked <- endpoints_checked <- 0L
for (pair in report$pairings) {
  prefix <- paste(pair$group_A, pair$group_B, sep = "/")
  left <- comparisons[[paste(prefix, "released-code", sep = "/")]]$records
  right <- comparisons[[paste(prefix, "paper-table", sep = "/")]]$records
  stopifnot(length(left) == 3876L, length(right) == 3876L)
  counts <- endpoint_counts <- setNames(integer(5), categories)
  endpoint_columns <- tapply(vapply(left, function(r) r$column, numeric(1)),
                             vapply(left, function(r) r$metric, character(1)), max)
  for (i in seq_along(left)) {
    a <- left[[i]]
    b <- right[[i]]
    stopifnot(identical(a$metric, b$metric), identical(a$column, b$column),
              identical(a$status, b$status))
    if (a$status == "visible-raster-interval-not-statistical-confidence") {
      stopifnot(identical(a$metric_interval, b$metric_interval))
      target <- unlist(a$metric_interval)
      la <- unlist(a$cohort_mean_range_over_tick_interval)
      lb <- unlist(b$cohort_mean_range_over_tick_interval)
      oa <- max(target[1], la[1]) <= min(target[2], la[2])
      ob <- max(target[1], lb[1]) <= min(target[2], lb[2])
      category <- if (oa && ob) "both_overlap" else if (oa) "released_only" else if (ob) "paper_only" else "neither_overlap"
    } else {
      category <- "unresolved"
    }
    counts[category] <- counts[category] + 1L
    if (a$column == endpoint_columns[[a$metric]]) {
      endpoint_counts[category] <- endpoint_counts[category] + 1L
      claimed <- Filter(function(r) r$metric == a$metric, pair$endpoints)[[1]]
      stopifnot(claimed$category == category)
      sa <- Filter(function(r) r$metric == a$metric,
                   summaries[[paste(prefix, "released-code", sep = "/")]]$endpoint_statistics)[[1]]
      sb <- Filter(function(r) r$metric == a$metric,
                   summaries[[paste(prefix, "paper-table", sep = "/")]]$endpoint_statistics)[[1]]
      stopifnot(claimed$released_mean == sa$mean, claimed$paper_mean == sb$mean,
                abs(claimed$paper_minus_released_mean - (sb$mean - sa$mean)) <= 1e-12 * max(1, abs(sa$mean), abs(sb$mean)))
      endpoints_checked <- endpoints_checked + 1L
    }
    curves_checked <- curves_checked + 1L
  }
  stopifnot(sum(counts) == 3876L, sum(endpoint_counts) == 14L,
            all(counts[names(pair$curve_counts)] == unlist(pair$curve_counts)),
            sum(unlist(pair$curve_counts)) == 3876L,
            all(endpoint_counts[names(pair$endpoint_counts)] == unlist(pair$endpoint_counts)),
            sum(unlist(pair$endpoint_counts)) == 14L)
  totals <- totals + endpoint_counts
}
stopifnot(curves_checked == 38760L, endpoints_checked == 140L)
write_json(list(curve_pairs_checked = curves_checked, endpoint_pairs_checked = endpoints_checked,
                endpoint_categories = as.list(totals),
                report_sha256 = digest(file = args[2], algo = "sha256"),
                scope = "Independent interval-intersection and source-mean arithmetic; no new trajectory audit or historical parameter identification."),
           args[3], auto_unbox = TRUE, pretty = TRUE)
