# Event Aggregator
Event aggregation for Audit Trails in Clinics

This is a web application with mixed programming language R and Python. 

    1. UI and server are programmed in R. 

    2. First-stage event aggregation is programmed in R.

    3. Second-stage event aggregation is programmed in Python. 

To run the app locally, you can use RStudio. One thing to notice is that you need to go to EA2.R to set the python path to your own: 

use_python("~/Library/r-miniconda-arm64/envs/r-reticulate/bin/python")
