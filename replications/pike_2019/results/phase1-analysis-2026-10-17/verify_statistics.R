args <- commandArgs(trailingOnly=TRUE)
data <- read.csv(file.path(args[1], 'survivors.csv'))
analysis <- jsonlite::fromJSON(file.path(args[1], 'analysis.json'), simplifyVector=FALSE)
errors <- c()
for (variant in names(analysis$survivors)) {
  values <- data$survivors[data$variant == variant]
  expected <- analysis$survivors[[variant]]
  stopifnot(length(values) == 100)
  interval <- mean(values) + c(-1,1)*qt(.975,99)*sd(values)/sqrt(100)
  errors <- c(errors, abs(mean(values)-expected$mean), abs(sd(values)-expected$sample_sd),
              abs(interval-unlist(expected$mean_ci95)))
}
for (comparison in analysis$comparisons) {
  left <- subset(data, variant == comparison$left)
  right <- subset(data, variant == comparison$right)
  stopifnot(identical(left$seed,right$seed))
  result <- t.test(left$survivors,right$survivors,var.equal=TRUE)
  paired <- t.test(left$survivors,right$survivors,paired=TRUE)
  errors <- c(errors, abs(unname(result$statistic)-comparison$equal_variance_t),
              abs(result$p.value-comparison$correct_two_sided_p),
              abs(mean(left$survivors-right$survivors)-comparison$paired_left_minus_right$mean),
              abs(unname(paired$conf.int)-unlist(comparison$paired_left_minus_right$mean_ci95)))
}
stopifnot(all(errors < 1e-10))
jsonlite::write_json(list(validated_numeric_values=length(errors), maximum_absolute_difference=max(errors),
                         independent_runtime=R.version.string, scope='R mean/sd/qt/t.test cross-check of all300native survivors and all3paired comparisons'),
                    file.path(args[1],'statistics-verification.json'), pretty=TRUE, auto_unbox=TRUE, digits=17)
