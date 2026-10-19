# Independent base-R reconstruction from the original individual simulation rows.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2, !file.exists(args[2]))
stream <- gzfile(args[1], "rt")
header <- strsplit(readLines(stream, n = 1), ",", fixed = TRUE)[[1]]
close(stream)
header <- gsub('"', '', header, fixed = TRUE)
keys <- c("id", "population", "minSugar", "maxSugar")
metrics <- c("gini", "mwgini")
classes <- ifelse(header %in% c(keys, metrics), "numeric", "NULL")
raw <- read.csv(gzfile(args[1]), colClasses = classes, check.names = FALSE)
stopifnot(nrow(raw) == 2727994, all(is.finite(as.matrix(raw))))
group <- do.call(paste, c(raw[keys], sep = ":"))
indices <- split(seq_len(nrow(raw)), group)
stopifnot(length(indices) == 54560)
result <- do.call(rbind, lapply(indices, function(i) {
  values <- unlist(lapply(metrics, function(metric) {
    x <- raw[[metric]][i]
    stopifnot(length(x) > 1, sd(x) > 0)
    c(mean(x), sd(x), mean(x) / sd(x))
  }))
  c(unlist(raw[i[1], keys]), n = length(i), values)
}))
colnames(result) <- c(keys, "n", "gini_mean", "gini_sd", "gini_sharpe",
                     "mwgini_mean", "mwgini_sd", "mwgini_sharpe")
write.csv(result, args[2], row.names = FALSE)
print(summary(result[, "gini_sharpe"]))
print(summary(result[, "mwgini_sharpe"]))
