library(shinyjs) # for UI
library(igraph)
library(shiny)
library(lubridate) #for dealing with time
library(dplyr) #for preparing data
library(ggplot2) #for plotting
library(ngram)
library(stringr)
library(reticulate) # for using python function
use_python("/Users/xinyun/Library/r-miniconda-arm64/envs/r-reticulate/bin/python")

source("Thread2Network.R")
source("EA1.R")
source("EA2.R")

server <- shinyServer(function(input, output, session) {

  # increase max file size to 40MB
  options(shiny.maxRequestSize = 40 * 1024^2)


  # Server: Read Data functions
  ##############################
  # Local Variable Definitions #
  ##############################

  # limit what files to accept on input
  fileTypes <- c("text/csv", "text/comma-separated-values,text/plain", ".csv", ".xes", '.RData')

  ##########################
  # Tab Output Definitions #
  ##########################
  output$evaluate_result <- renderTable({
    if (is.null(test_ea2())) {
      return(NULL)
    } else {
      rlist <- list('silhouette' = test_ea2()[1], 
           'max_inter_cluster' = test_ea2()[2], 
           'avg_intra_cluster' = test_ea2()[3], 
           'avg_intra_precision' = test_ea2()[4], 
           'avg_similarity' = test_ea2()[5], 
           'number_of_buckets' = test_ea2()[6],
           'clustered_percentage' = test_ea2()[7])
      ea2_result <- data.frame(name=names(rlist), value=unlist(rlist))
      return(ea2_result)
    }
  })

  output$download <- downloadHandler(
    filename = function() {
      paste(tools::file_path_sans_ext(input$inputFile$name), 'stage1', ".Rdata", sep = "_")
    },
    content = function(file) {
      #print(file)
      #View(test()$ea1_result)
      ea1_df <- test()$ea1_result
      save(ea1_df, file = file)
    }
  )
  
  output$download_lexicon_freq <- downloadHandler(
    filename = function() {
      paste(tools::file_path_sans_ext(input$inputFile$name), 'LexiconsFreq', ".Rdata", sep = "_")
      #print(input$inputFile$name)
    },
    content = function(file) {
      #print(file)
      lexicons_freq <- test()$lexicons_freq
      save(lexicons_freq, file = file)
    }
  )


  ###########################
  ### read data functions ###
  ###########################

  # dataframe for occurrences that are read in from file1
  occ <<- eventReactive(input$inputFile, parseInputData(input$inputFile))
  
  tps <<- eventReactive(input$inputFile_ea2_1, load_(input$inputFile_ea2_1, 'ea1_df'))
  
  freq <<- eventReactive(input$inputFile_ea2_2, load_(input$inputFile_ea2_2, 'lexicons_freq'))

  
  ###########################
  ### first stage EA beta ###
  ###########################
  #test <- data.frame() 
  #df_in <<- eventReactive(input$ea1_input_file, parseInputData(input$ea1_input_file))
  
  observe({
    updateSelectInput(session, "event", choices = names(occ())[-1], selected = 'Metric_Desc')
  })
  
  observe({
    updateSelectInput(session, "t", choices = names(occ())[-1], selected = 'Access_Time')
  })
  
  observe({
    updateSelectInput(session, "contextCaseID", choices = names(occ())[-1], selected = 'vis_id')
  })
  
  observe({
    updateSelectInput(session, "contextRole", choices = names(occ())[-1], selected = 'newrole')
  })
  
  observe({
    updateSelectInput(session, "contextWorkstation", choices = names(occ())[-1], selected = 'Workstation_ID')
  })
  
  get_threshold <- reactive({
    days_thres = NULL
    if (input$threshold_days == "Weekdays only"){
      days_thres = c(1,5)
    }else{
      days_thres = c(1,7)
    }
    return(list('days_thres' = days_thres, 
                'hours_thres' = input$threshold_hours, 
                'Mostfreq_by_rank_thres' = as.numeric(input$mostFreq_), 
                'Leastfreq_by_seqFreq_thres' = as.numeric(input$leastFreq_)
                )
           )
  })
  
  test <<- eventReactive(input$first_stage_EA, 
                         EA1(occ(), 
                             input$contextCaseID, input$contextRole, input$contextWorkstation,
                             get_threshold(),
                             input$event,
                             input$t
                             )
                         )
  test_ea2 <<- eventReactive(input$second_stage_EA, 
                         EA2(as.numeric(input$LSH_l),
                             as.numeric(input$LSH_r),
                             tps(),
                             freq()
                             )
                         )
  observe({
    print(input$LSH_l)
    print(input$LSH_r)
    #print(path_tps)
    #View(test()$ea1_result)
    #View(test()$lexicons_freq)
    #print(is.null(test()))
  })
  observeEvent(test(), {
    if (!is.null(test()$ea1_result)) {
      #print(!is.null(test()$ea1_result))
      shinyjs::show("download")
    }
  })
  observeEvent(test(), {
    if (!is.null(test()$lexicons_freq)) {
      #print(!is.null(test()$lexicons_freq))
      shinyjs::show("download_lexicon_freq")
    }
  })
  
  observeEvent(test_ea2(), {
    if (!is.null(test_ea2())) {
      print(test_ea2())
    }
  })
  
  observeEvent(freq(), {
    if (!is.null(freq())) {
      #View(freq())
    }
  })
  
  observeEvent(tps(), {
    if (!is.null(tps())) {
      #View(tps())
    }
  })
  
  
  #observeEvent(input$toggle_btn, {
  #  print('toggleeeee')
  #  shinyjs::toggle("panel")
  #})
  observeEvent(input$mostFreq, {
    if(input$mostFreq == '') {
      updateCheckboxGroupInput(session, 'mostFreq', selected = character(0))
    }
  })

  observeEvent(input$leastFreq, {
    if(input$leastFreq == '') {
      updateCheckboxGroupInput(session, 'leastFreq', selected = character(0))
    }
  })
  
  
  #
  
  ####################
  # Helper Functions #
  ####################
  
  load_ <- function(inputFile, subname) {
    #print(inputFile$datapath)
    load(inputFile$datapath)
    fileRows <- get(grep(subname, ls(), value = TRUE))
    #View(fileRows)
    return(fileRows)
  }

  # read in user supplied file
  # return dataframe of occurences
  parseInputData <- function(inputFile) {

    withProgress(message = "Reading and cleaning Data", value = 0, {

      # Check if this is an xes file
      fileType <- tools::file_ext(inputFile$datapath)
      if (fileType == 'xes')
      {
        # read in the table of occurrences
        fileRows <- as.data.frame(read_xes(inputFile$datapath))

        if (any(match(colnames(fileRows), "timestamp"))) {

          # rename column as tStamp
          colnames(fileRows)[colnames(fileRows) == "timestamp"] <- "tStamp"

          # move tStamp to the first column
          fileRows <- fileRows[c('tStamp', setdiff(names(fileRows), 'tStamp'))]
        }else if (any(match(colnames(fileRows), "start_time"))) {
          
          # rename column as tStamp
          colnames(fileRows)[colnames(fileRows) == "start_time"] <- "tStamp"
          
          # move tStamp to the first column
          fileRows <- fileRows[c('tStamp', setdiff(names(fileRows), 'tStamp'))]
          
        }
        else { return(NULL) }
      }
      else if (fileType == 'csv')
      { # read in the table of occurrences
        fileRows <- read.csv(inputFile$datapath) }
      else if (fileType == 'RData' | tolower(fileType) == 'rdata') {
        load(inputFile$datapath)
        fileRows <- get(ls()[1])
        # move tStamp to the first column
        fileRows <- fileRows[c('tStamp', setdiff(names(fileRows), 'tStamp'))]
        #View(fileRows)
      }

      incProgress(1 / 3)

      # validate expected columns (first col must be "tStamp" or "sequence")
      firstCol <- names(fileRows)[1]

      # if first col is tStamp, no changes, else
      # if first col is sequence, add a default timestamp, else
      # supply a default dataset

      if (firstCol != "tStamp") {
        if (firstCol != "sequence") {
          print("First column needs to be tStamp or sequence")
        } else {
          fileRows <- add_relative_timestamps(fileRows)
        }
      }
      incProgress(2 / 3)
      # clean the data
      cleanData <- cleanOcc(fileRows)
      #View(cleanData)
      incProgress(3 / 3)

    })


    # shinyjs::show(selector = "#navbar li a[data-value=choosePOV]")
    # shinyjs::hide(selector = "#navbar li a[data-value=visualize]")
    # shinyjs::hide(selector = "#navbar li a[data-value=subsets]")
    # shinyjs::hide(selector = "#navbar li a[data-value=comparisons]")
    # shinyjs::hide(selector = "#navbar li a[data-value=movingWindow]")
    # shinyjs::hide(selector = "#navbar li a[data-value=parameterSettings]")
    # 


    # return a valid dataframe of occurences
    return(cleanData)
  }

  # add initial "tStamp" column if missing in original input data
  # Start time for all threads is the same: "2017-01-01 00:00:00"  Happy New Year!
  add_relative_timestamps <- function(fileRows) {

    startTime <- as.POSIXct("2017-01-01 00:00:00")

    # add the column at the beginning
    fileRows <- cbind(startTime + 60 * as.numeric(as.character(fileRows[["sequence"]])), fileRows)

    # set the column name
    names(fileRows)[1] <- "tStamp"

    return(fileRows)

  }

  # clean up the raw occurrence data
  # Remove blanks for n-gram functionality
  cleanOcc <- function(fileRows) {

    # extract tStamp
    tStamp <- fileRows$tStamp

    # confirm all spaces are converted to underscores in non tStamp columns; set as factors
    cleanedCF <- data.frame(lapply(fileRows[2:ncol(fileRows)], function(x) { gsub(" ", "_", x) }))

    # bind tStamp back to cleaned data
    complete <- cbind(tStamp, cleanedCF)

    # force tStamp into a "YMD_HMS" format
    complete$tStamp <- as.character(complete$tStamp)
    complete$tStamp <- parse_date_time(complete$tStamp, c("dmy HMS", "dmY HMS", "ymd HMS", "dmy HM", "dmY HM", "ymd HM"))

    # add weekday and month
    complete$weekday <- as.factor(weekdays(as.Date(complete$tStamp)))
    complete$month <- as.factor(months(as.Date(complete$tStamp)))

    return(complete)
  }
  
})


