abc_testing<-function(training_set,testing_set,tol=DEFAULT_TOL,parameter_colnames,
                      method="rejection",semiauto=FALSE,
                      #only used in semi-auto
                      satr=list(function(x){outer(x,Y=1:4,"^")}),# this comes from the COAL example; regress up to degree 4
                      ...)
{
  
  #abctools works on matrices, not data.frames so we need to convert
  obsparam = testing_set %>% 
    dplyr::select(parameter_colnames) %>% as.matrix()
  obs<- testing_set %>% dplyr::select(-parameter_colnames) %>%   
    data.matrix()
  progress_bar<- knitrProgressBar::progress_estimated(obs %>%nrow())
  
  
  #store results here
  results<-data.frame(
    matrix(ncol=length(parameter_colnames),nrow=0)
  )
  colnames(results)<-parameter_colnames
  
  #store intervals here
  highs<-data.frame(
    matrix(ncol=length(parameter_colnames),nrow=0)
  )
  lows<-data.frame(
    matrix(ncol=length(parameter_colnames),nrow=0)
  )
  colnames(highs)<-parameter_colnames
  colnames(lows)<-parameter_colnames
  
  # the x and the y of the training set
  param <-
    training_set %>% 
    dplyr::select(parameter_colnames) %>% data.matrix()
  sumstats<-
    training_set %>% dplyr::select(-parameter_colnames) %>%   
    data.matrix()
  for(i in 1:nrow(testing_set))
  {
    checkpoint_path <- file.path(checkpoint_fold, sprintf("row-%04d.rds", i))
    rng_before <- .Random.seed
    if (file.exists(checkpoint_path)) {
      cached <- readRDS(checkpoint_path)
      stopifnot(identical(rng_before, cached$rng_before))
      low <- cached$low
      medians <- cached$medians
      high <- cached$high
      assign(".Random.seed", cached$rng_after, envir = .GlobalEnv)
    } else {
    rezult<-NULL
    
    if(semiauto)
    {
      rezult<-
        semiauto.abc(obs = obs[i,], 
                     param = param ,
                     sumstats = sumstats,
                     method=method,
                     # this comes from the COAL example; regress up to degree 4
                     satr=satr,
                     verbose=FALSE,
                     plot=FALSE,
                     do.err=TRUE,
                     final.dens = TRUE,
                     tol=tol,
                     obspar = obsparam[i,],...)
      low<-rezult$post.sample %>% as.data.frame() %>% summarise_all(quantile,LOW_QUANTILE)
      medians<-rezult$post.sample %>% as.data.frame() %>% summarise_all(median)
      high<-rezult$post.sample %>% as.data.frame() %>% summarise_all(quantile,HIGH_QUANTILE)
      
    }
    else{
      rezult<-abc::abc(target = obs[i,], 
                  param = param,
                  sumstat = sumstats
                  ,tol=tol,method=method,...)
      low<- summary(rezult, print = F)[2, ]
      medians<-summary(rezult, print = F)[3, ] #grabbed from the ABC code (the cv method)
      high<-summary(rezult, print = F)[6,]
    }
    
    names(medians) <- names(low) <- names(high) <-parameter_colnames
    medians<-data.frame(
      as.list(medians)
    )
    # 3 is median; 4 is mean; 5 is mode.
      pending <- paste0(checkpoint_path, ".", Sys.getpid(), ".pending")
      stopifnot(!file.exists(pending), !file.exists(checkpoint_path))
      saveRDS(list(low = low, medians = medians, high = high,
                   rng_before = rng_before, rng_after = .Random.seed), pending)
      stopifnot(file.rename(pending, checkpoint_path))
      checkpoints_written <<- checkpoints_written + 1L
      if (stop_after > 0L && checkpoints_written == stop_after) {
        stop("Requested interruption after durable observation checkpoint")
      }
    }
    results<-bind_rows(results,
                       medians)
    
    highs<-bind_rows(highs,
                     data.frame(as.list(high)))
    lows<-bind_rows(lows,
                    data.frame(as.list(low)))
    
    progress_bar$tick()
    progress_bar$print()
    
  }
  
  #compute prediction errors
  errors<-vector(mode="numeric",length=length(parameter_colnames))
  contained<-vector(mode="numeric",length=length(parameter_colnames))
  interval_size<-vector(mode="numeric",length=length(parameter_colnames))
  
  for(i in 1:length(errors))
  {
    errors[i] <- sqrt(mean((obsparam[,i]-results[,i])^2))
    contained[i] <- sum( obsparam[,i] >= lows[,i] & obsparam[,i] <= highs[,i])/length(obsparam[,i])
    interval_size[i] <- mean(highs[,i]-lows[,i])
  }
  names(errors)<- names(contained) <- names(interval_size) <-parameter_colnames
  
  return(
    list(
      medians= results,
      lows = lows,
      highs = highs,
      errors = errors,
      contained = contained,
      interval_size = interval_size
    )
  )
  
}  



