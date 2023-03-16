library(shiny)
library(shinyjs)
library(shinydashboard) #Ref: https://rstudio.github.io/shinydashboard/structure.html

fileTypes <- c("text/csv", "text/comma-separated-values,text/plain", ".csv", ".xes", '.rdata')

# Basic UI with a tabset for Routine Resilience Simulator

ui <- dashboardPage(
  dashboardHeader(title = HTML("Event Aggregator <sup>
               <span style='font-size:12px;'>Beta</span></sup>")),
  #dashboardSidebar(disable = TRUE),
  dashboardSidebar(
    sidebarMenu(
      # free icon reference: https://fontawesome.com/search?p=4&o=r&m=free
      menuItem("Event Aggregation", tabName = "ea", icon = icon("wand-magic-sparkles"),
               badgeLabel = 'beta', badgeColor = 'green'),
      menuItem("Acknowledgements", icon = icon("medal"), tabName = "ac")
    )
  ),
  dashboardBody(
    useShinyjs(),
    tags$style(
      ".ea1 {
      margin-bottom: 20px;
    }",
      ".goButton {
      margin-bottom: 20px;
    }",
    HTML('#first_stage_EA_test{background-color:#0077B6; 
         font-weight:bold;
         color:white;
         border-radius: 15px;}'),
    HTML('.content-wrapper {
          overflow-x: auto;
          overflow-y: hidden;
        }')
    ),
    #tags$h2(align = 'center', 
    #        HTML("Event Aggregator <sup>
    #           <span style='font-size:12px;'>Beta</span></sup>")),
    
    tabItems(
      tabItem(tabName = "ea",
              h2(HTML("Event Aggregator <sup><span style='font-size:16px;'>Beta</span></sup>")),
              box(title = "Stage 1 Event Aggregation (touchpoints generating)", 
                  status = "primary", solidHeader = TRUE, width = 12,
                  tags$div(
                    fileInput("inputFile", "Please import a .csv, .xes, or .rdata file", accept = fileTypes)
                  ),
                  fluidRow(
                    box(
                      title = 'step1. choose contexutal attributes that define touchpoints',
                      solidHeader = TRUE, status = 'primary', width=4,
                      div(
                        id = 'context_',
                        #tags$span(style = "font-weight: bold;color: #0077B6; font-size: 16px;", 
                        #          "step1. choose contexutal attributes that define touchpoints:"),
                        selectInput("contextCaseID", 
                                    label = tags$span(style = "font-size: 12px;",
                                                      "Case ID (choose the column indicating case ID):"),
                                    choices=NULL,selected='vis_id',
                                    multiple=FALSE, selectize=TRUE
                        ),
                        selectInput("contextRole", 
                                    label = tags$span(style = "font-size: 12px;",
                                                      "Role (choose the column indicating roles):"),
                                    choices=NULL,selected='newrole',
                                    multiple=FALSE, selectize=TRUE
                        ),
                        selectInput("contextWorkstation", 
                                    label = tags$span(style = "font-size: 12px;",
                                                      "Workstation ID (choose the column indicating workstation ID or type):"),
                                    choices=NULL,selected='Workstation_ID',
                                    multiple=FALSE, selectize=TRUE
                        )
                      )), 
                    box(
                      title = 'step2. tell us more about your data!',
                      solidHeader = TRUE, status = 'primary', width=4,
                      div(id = "panel1",
                          #tags$span(style = "font-weight:bold; color: #0077B6; font-size: 16px;", 
                          #           "step2. tell us more about your data!"),
                          #actionButton("toggle_btn_info", "We need know more about your data!"),
                          selectInput("event", 
                                      label = tags$span(style = "font-size: 12px;","Event column:"), 
                                      choices = NULL, selected = 'Metric_Desc'),
                          selectInput("t", 
                                      label = tags$span(style = "font-size: 12px;","Time column:"), 
                                      choices = NULL, selected = 'Access_Time'),
                      )),
                    box(
                      class = 'ea1',
                      title = 'step3. how you want us to filter your data!',
                      solidHeader = TRUE, status = 'primary', width=4,
                      div(id = "panel2",
                          #tags$span(style = "font-weight:bold; color: #0077B6; font-size: 16px;", 
                          #           "step3. how you want us to filter your data!"),
                          selectInput("threshold_days", 
                                      label = tags$span(style = "font-size: 12px;","Working days:"), 
                                      choices = c("Include weekends", "Weekdays only"), 
                                      selected = "Weekdays only"),
                          sliderInput("threshold_hours", 
                                      label = tags$span(style = "font-size: 12px;","Working hours:"), 
                                      0, 24, c(8,17), step = 1, ticks = FALSE),
                          # for frequency threshold
                          checkboxGroupInput("mostFreq", 
                                             label = tags$span(style = "font-size: 12px;", "Remove frequent events:"), 
                                             choices = list("Remove most frequent events" = "yes"), 
                                             selected=character(0)),
                          div(id = 'freq1', 
                              conditionalPanel(condition = "input.mostFreq=='yes'", 
                                               selectInput("mostFreq_", "Select n to remove the top n frequent actions:",
                                                           choices = c(0:100), selected=3))),
                          checkboxGroupInput("leastFreq", "",
                                             choices = list("Remove least frequent events" = "yes"), 
                                             selected=character(0)),
                          div(id = 'freq2', 
                              conditionalPanel(condition = "input.leastFreq=='yes'",
                                               selectInput("leastFreq_", "Select n to remove actions with document frequency <=n:",
                                                           choices = c(0:100), selected=24)))
                      )),
                    div(
                      class = 'goButton',
                      align = 'center',
                      actionButton("first_stage_EA","Go! First-Stage Event Aggregation"),
                      style = "border-color:red;"
                    ),
                    
                    
                    div(
                      class = 'ea1',
                      align = 'center',
                      downloadButton("download", "Download EA1 File", class = "btn-success", 
                                     style = "display:none; color: white; border-radius: 5px;")
                    ),
                    
                    div(
                      class = 'ea1',
                      align = 'center',
                      downloadButton("download_lexicon_freq", "Download the file with lexicon frequency!", class = "btn-success", 
                                     style = "display:none; color: white; border-radius: 5px;")
                    ),
                    
                  )
              ),
              box(title = HTML("Stage 2 Event Aggregation <sup>Beta</sup> (LSH bucketing)"), 
                  status = "primary", solidHeader = TRUE, width = 12,
                  tags$div(
                    fileInput("inputFile_ea2_1", "Select touchpoints file from stage 1", accept = fileTypes),
                    #textOutput("fpath1")
                  ),
                  tags$div(
                    fileInput("inputFile_ea2_2", "Select lexicons frequency file from stage 1", accept = fileTypes)
                  ),
                  fluidRow(
                    box(
                      title = 'step1. choose parameters for LSH',
                      solidHeader = TRUE, status = 'primary', width=6,
                      div(
                        id = 'LSH_parameters',
                        #tags$span(style = "font-weight: bold;color: #0077B6; font-size: 16px;", 
                        #          "step1. choose parameters for LSH"),
                        selectInput("LSH_r", 
                                    label = tags$span(style = "font-size: 12px;",
                                                      "r (size of signature):"),
                                    choices=sapply(0:4, function(x) as.character(2^x)),selected=2,
                                    multiple=FALSE, selectize=TRUE
                        ),
                        selectInput("LSH_l", 
                                    label = tags$span(style = "font-size: 12px;",
                                                      "l (number of iterations):"),
                                    choices=sapply(0:6, function(x) as.character(2^x)),
                                    selected=1,
                                    multiple=FALSE, selectize=TRUE
                        ),
                      )), 
                    box(
                      title = 'step2. touchpoint representation',
                      solidHeader = TRUE, status = 'primary', width=6,
                      div(
                        id = 'representation_',
                        checkboxInput("kgram", 
                                      label = tags$span(style = "font-size: 12px;","Bag of Events"),
                                      value = TRUE),
                        
                      ))
                  ),
                  div(
                    class = 'goButton',
                    align = 'center',
                    actionButton("second_stage_EA","Go! Second-Stage Event Aggregation"),
                    style = "border-color:red;"
                  ),
                  div(
                    align = 'center',
                    tableOutput('evaluate_result')
                  )
              ),
              div(
                id = "logo",
                align = 'center',
                class = "logo",
                tags$img(src = "http://clipart-library.com/images_k/michigan-state-logo-transparent/michigan-state-logo-transparent-13.png", height = 50)
              ),
              div(id = 'copyright',
                  align = 'center',
                  p('Copyright © 2023 Michigan State University')
              )
      ),
      
      tabItem(tabName = "ac",
              h2("Acknowledgements"),
              tags$h4("PI"),
              tags$p("Brian Pentland, Michigan State University"),
              
              tags$h4("Contact"),
              tags$a(href = "mailto:zhan2070@msu.edu", "zhan2070@msu.edu"),
              
              tags$h4("Financial Support"),
              tags$a(href = "https://www.nsf.gov/awardsearch/showAward?AWD_ID=1734237", "NSF SES-1734237", target = "_blank"),
              tags$p("Antecedents of Complexity in Healthcare Routines"),
              
              tags$h4("Code Gurus"),
              tags$p("Christian Hovestadt, Li Zhang, Omar Syed"),
              
              tags$h4("Collaborators"),
              tags$p(" Ken Frank, Inkyu Kim, Waldemar Kremser,  Alice Pentland, Jan Recker,  Julie Ryan Wolf"),
              
              tags$h4("Documentation and Related Publications"),
              tags$a(href = "http://routines.broad.msu.edu/resources/", "http://routines.broad.msu.edu/resources/", target = "_blank"),
              
              tags$h4("Official Song"),
              tags$a(href = "https://www.youtube.com/watch?v=tSnoHWBYA8U", "Doctor Decade: Tell Us a Story", target = "_blank"),
              
              div(
                id = "logo",
                align = 'center',
                class = "logo",
                tags$img(src = "http://clipart-library.com/images_k/michigan-state-logo-transparent/michigan-state-logo-transparent-13.png", height = 50)
              ),
              div(id = 'copyright',
                  align = 'center',
                  p('Copyright © 2023 Michigan State University')
              )
      )
    )
  )
)

 


