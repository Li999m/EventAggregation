library(reticulate) # for using python function
use_python("/Users/xinyun/Library/r-miniconda-arm64/envs/r-reticulate/bin/python")

EA2 <- function(l, r, df, freq_df){
  py_run_file("lsh.py")
  test <- py$LSH(l, r, df, freq_df)
  return(test)
}

