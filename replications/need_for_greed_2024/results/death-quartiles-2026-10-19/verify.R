args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2L, !file.exists(args[[2]]))
report <- jsonlite::fromJSON(file.path(args[[1]], "comparison.json"))
vectors <- jsonlite::fromJSON(file.path(args[[1]], "vectors.json"))
rows <- report$comparisons
errors <- numeric(nrow(rows))
distance_errors <- numeric(nrow(rows))
curves <- report
box <- curves$axes_pdf_rectangle
for (i in seq_len(nrow(rows))) {
  row <- rows[i, ]
  probability <- c(first_quartile = .25, median = .5, third_quartile = .75)[[row$quantile]]
  value <- unname(quantile(vectors[[row$series]], probability, type = row$quantile_type))
  errors[[i]] <- abs(value - row$value)
  points <- do.call(rbind, curves$curves[[row$quantile]]$records$pdf_xy)
  x <- box[[1]] + .37 * (box[[3]] - box[[1]])
  y <- box[[4]] - value * (box[[4]] - box[[2]]) / 30
  distances <- numeric(nrow(points) - 1L)
  for (j in seq_len(length(distances))) {
    dx <- points[j + 1L, 1L] - points[j, 1L]
    dy <- points[j + 1L, 2L] - points[j, 2L]
    t <- min(1, max(0, ((x - points[j, 1L]) * dx + (y - points[j, 2L]) * dy) / (dx^2 + dy^2)))
    distances[[j]] <- sqrt((x - points[j, 1L] - t * dx)^2 + (y - points[j, 2L] - t * dy)^2)
  }
  distance_errors[[i]] <- abs(min(distances) - row$distance_points)
}
stopifnot(nrow(rows) == 486L, max(errors) < 1e-10, max(distance_errors) < 1e-10)
result <- list(comparisons = nrow(rows), maximum_quantile_error = max(errors), maximum_distance_error_points = max(distance_errors), quantile_types = 1:9, scope = "Independent R quantiles and scalar segment-distance arithmetic on hash-pinned native-derived vectors; not an independent simulation.")
jsonlite::write_json(result, args[[2]], auto_unbox = TRUE, pretty = TRUE, digits = 17)
print(result)
