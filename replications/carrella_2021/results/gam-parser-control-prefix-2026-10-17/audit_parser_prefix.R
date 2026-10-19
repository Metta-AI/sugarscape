args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==4L,!file.exists(args[[4]]))
source_dir<-args[[1]];run<-args[[2]];primary<-args[[3]]
params<-as.data.frame(readr::read_csv(file.path(source_dir,'data/sugarscape/params_sugarscape.csv'),show_col_types=FALSE))
params[['random-seed']]<-NULL
stats<-as.data.frame(readr::read_csv(file.path(source_dir,'data/sugarscape/sugarscape.csv'),show_col_types=FALSE))
stats<-stats[vapply(stats,var,numeric(1))>0]
names(params)<-make.names(names(params),unique=TRUE,allow_=FALSE)
names(stats)<-make.names(names(stats),unique=TRUE,allow_=FALSE)
data<-cbind(params,stats)[1:1250,]
RNGkind('Mersenne-Twister','Inversion','Rejection');set.seed(0)
permutation<-sample(seq_len(1250))
errors<-coverage<-width<-baseline<-matrix(NA_real_,5,5)
input_delta<-numeric(5);prediction_delta<-numeric(5)
for(fold in 1:2){
 x<-readRDS(file.path(run,paste0('fold-',fold,'.rds')))
 old<-readRDS(file.path(primary,paste0('fold-',fold,'.rds')))
 ids<-sort(permutation[((fold-1)*250+1):(fold*250)])
 testing<-data[ids,];training<-data[-ids,]
 rownames(testing)<-rownames(training)<-NULL
 stopifnot(identical(x$testing,testing),identical(x$training,training))
 stopifnot(identical(dim(old$training),dim(training)),identical(dim(old$testing),dim(testing)),identical(names(old$testing),names(testing)))
 input_delta[fold]<-max(abs(as.matrix(old$training)-as.matrix(training)),abs(as.matrix(old$testing)-as.matrix(testing)))
 prediction<-as.matrix(x$result$predictions);truth<-as.matrix(testing[names(params)])
 low<-as.matrix(x$result$lows);high<-as.matrix(x$result$highs)
 stopifnot(identical(dim(prediction),c(250L,5L)),identical(dim(low),dim(prediction)),identical(dim(high),dim(prediction)),all(is.finite(c(prediction,truth,low,high))),all(low<=high))
 errors[fold,]<-sqrt(colMeans((prediction-truth)^2))
 coverage[fold,]<-colMeans(truth>=low & truth<=high)
 width[fold,]<-colMeans(high-low)
 baseline[fold,]<-sqrt(colMeans(sweep(truth,2,colMeans(as.matrix(training[names(params)])),'-')^2))
 prediction_delta[fold]<-max(abs(prediction-as.matrix(old$result$predictions)))
 stopifnot(max(abs(errors[fold,]-x$result$errors))<1e-10,max(abs(coverage[fold,]-x$result$contained))<1e-10,max(abs(width[fold,]-x$result$interval_size))<1e-10)
}

x<-readRDS(file.path(run,'fold-2.rds'));old<-readRDS(file.path(primary,'fold-2.rds'))
ids<-sort(permutation[251:500]);stopifnot(ids[131]==676L,x$testing$wealth.reproduction[131]==92)
report<-list(completed_folds_audited=2,predictions_audited=2500,input_cells_checked=377500,maximum_input_delta=max(input_delta[1:2]),maximum_prediction_delta=max(prediction_delta[1:2]),maximum_prediction_delta_by_fold=prediction_delta[1:2],original_outlier=list(source_input_zero_based=675,test_row_one_based=131,truth=92,primary_prediction=old$result$predictions[131,'wealth.reproduction'],parser_control_prediction=x$result$predictions[131,'wealth.reproduction']),scope='Two complete saved folds only; no aggregate cross-validation result or paper verdict.')
writeLines(jsonlite::toJSON(report,pretty=TRUE,auto_unbox=TRUE,digits=17),args[[4]])
print(report)
