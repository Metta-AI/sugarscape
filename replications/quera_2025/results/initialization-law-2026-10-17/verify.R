args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==1L)
a <- jsonlite::fromJSON(file.path(args[1], 'analysis.json'),simplifyVector=FALSE)
rows <- read.csv(file.path(args[1],'cdfs.csv'))
errors <- numeric()
for (name in names(a$parameters)) {
 r <- a$parameters[[name]];alpha <- r$alpha;beta <- r$beta
 mean_native <- integrate(function(u)(1-u^(1/beta))^(1/alpha),0,1,rel.tol=1e-12,abs.tol=1e-12,subdivisions=1000)$value
 second_native <- integrate(function(u)(1-u^(1/beta))^(2/alpha),0,1,rel.tol=1e-12,abs.tol=1e-12,subdivisions=1000)$value
 mean_beta <- integrate(function(x)x*dbeta(x,alpha,beta),0,1,rel.tol=1e-12)$value
 second_beta <- integrate(function(x)x*x*dbeta(x,alpha,beta),0,1,rel.tol=1e-12)$value
 errors <- c(errors,abs(mean_native-r$native_unit_mean),abs(mean_beta-r$beta_unit_mean),abs(r$offset+r$scale*mean_native-r$native_scaled_mean),abs(r$offset+r$scale*mean_beta-r$beta_scaled_mean),abs(r$scale^2*(second_native-mean_native^2)-r$native_scaled_variance),abs(r$scale^2*(second_beta-mean_beta^2)-r$beta_scaled_variance))
 selected <- rows[rows$parameter==name,]
 errors <- c(errors,abs(pbeta(selected$unit_value,alpha,beta)-selected$beta_cdf))
}
stopifnot(max(errors)<1e-9)
result <- list(scalar_checks=length(errors),maximum_absolute_difference=max(errors),scope='Independent numerical integration of the native inverse-uniform sampler and Beta density; R pbeta checks all2002 referenceCDF entries. No parameter fitting or paper verdict.')
writeLines(jsonlite::toJSON(result,auto_unbox=TRUE,pretty=TRUE,digits=17),file.path(args[1],'independent-audit.json')); print(result)
