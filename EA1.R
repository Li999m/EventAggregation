

keep_first_day <- function(df, tStamp_) {
  save(df, file="df.RData")
  df[[tStamp_]] <- tryCatch(as_datetime(as.numeric(df[[tStamp_]])), 
                            warning = function(e){
                              as_datetime(df[[tStamp_]])
                              })
  df <- df %>%
    group_by(vis_id) %>%
    mutate(day = day(.data[[tStamp_]])) %>%
    filter(day == first(day))
  return(df)
}

remove_dup <- function(df, vis_id, role, workstation_ID, Metric_Desc, tStamp_) {
  while(TRUE){
    df <- df %>%
      arrange(.data[[tStamp_]]) %>%
      group_by(.data[[vis_id]], .data[[role]], .data[[workstation_ID]]) %>% # don't include workstation, may influence how i judge the sequence
      mutate(Metric_Desc_lag = dplyr::lag(.data[[Metric_Desc]]), tStamp_lag=dplyr::lag(.data[[tStamp_]])) %>%
      mutate(Metric_Desc_lag = ifelse(is.na(Metric_Desc_lag), '_', Metric_Desc_lag))%>%
      mutate(tStamp_lag = ifelse(is.na(tStamp_lag), .data[[tStamp_]], tStamp_lag))
    print(nrow(df))
    View(df)
    #save(df, file="df.RData")
    
    ######## test if need to remove duplicates. 
    #if(class(df[[tStamp_]]) == 'character') {
    #  df[[tStamp_]] <- as.numeric(df[[tStamp_]])
    #}
    #if(class(df$tStamp_lag) == 'character'){
    #  class$tStamp_lag <- as.numeric(class$tStamp_lag)
    #}
    x <- df%>% 
      arrange(.data[[tStamp_]]) %>%
      group_by(.data[[vis_id]], .data[[role]], .data[[workstation_ID]]) %>%
      filter(
        (.data[[Metric_Desc]]==Metric_Desc_lag & as.numeric(difftime(as_datetime(.data[[tStamp_]]) ,as_datetime(tStamp_lag)))<=60) 
      )
    n = nrow(x)
    print(n)
    if(n==0){break}
    
    ###### remove 
    df <- df %>%
      arrange(.data[[tStamp_]]) %>%
      group_by(.data[[vis_id]], .data[[role]], .data[[workstation_ID]]) %>%
      #mutate(dff = as.numeric(difftime(as_datetime(.data[[tStamp]]) ,as_datetime(tStamp_lag)))) %>%
      filter(
        (!.data[[Metric_Desc]]==Metric_Desc_lag) | 
          (.data[[Metric_Desc]]==Metric_Desc_lag & as.numeric(difftime(as_datetime(.data[[tStamp_]]) ,as_datetime(tStamp_lag)))>60)
      )
    #View(df)
    print(nrow(df))
  }
  return(df)
}

ea_1 <- function(df, vis_id, role, workstation_ID, Metric_Desc, tStamp_){
  #View(df)
  df_test <- df %>%
    arrange(.data[[tStamp_]]) %>%
    group_by(.data[[vis_id]], .data[[role]], .data[[workstation_ID]]) %>%
    #mutate(gap = as.numeric(difftime(as_datetime(.data[[tStamp_]]), as_datetime(tStamp_lag))))
    mutate(gap = ifelse(as.numeric(difftime(as_datetime(.data[[tStamp_]]) ,
                                            as_datetime(tStamp_lag)))>60, 1, 0), 
           gap_lag = dplyr::lag(gap)) %>%
    mutate(gap_lag = ifelse(is.na(gap_lag), 0, gap_lag), tps_indicator = cumsum(gap_lag))
  View(df_test)
  df1 <- df_test %>% # tps: 108359 rows -> 37275 unique rows (tps) # ort:23824 -> 11887
    group_by(.data[[as.name(vis_id)]], .data[[role]], .data[[workstation_ID]], tps_indicator) %>%
    summarise(start_time = min(.data[[tStamp_]]), 
              Metric_Desc = paste0(.data[[Metric_Desc]], collapse = '|'), 
              vis_id = unique(.data[[vis_id]])
              #wday = unique(wday),
              #week = unique(week)
    ) %>%
    arrange(vis_id, start_time)
  return(df1)
}

# ------------------------- main function -----------------------------

EA1 <- function(df, vis_id, role, workstation_ID, filter_thresholds, Metric_Desc, tStamp_) {
  save(df, file="df.RData")
  df <- keep_first_day(df, tStamp_)
  View(df)
  l <- filter_thresholds
  # threshold: Monday to Friday
  df$wday <- wday(as.Date(df[[tStamp_]]), week_start = 1)
  df <- df%>%
    filter(wday>=l$days_thres[1] & wday<=l$days_thres[2])
  
  # threshold: 8am-5pm
  df$hour = hour(df[[tStamp_]])
  df <- df %>%
    filter(hour>=l$hours_thres[1] & hour<=l$hours_thres[2])
  
  df <- remove_dup(df, vis_id, role, workstation_ID, Metric_Desc, tStamp_)
  if(l$Mostfreq_by_rank_thres==0 & l$Leastfreq_by_seqFreq_thres==0){ # 22554
    return(
      list(
        'lexicons_freq' = Null, 
        'ea1_result' = ea_1(df, vis_id, role, workstation_ID, Metric_Desc, tStamp_))
      )
  }else{
    df1 <- ea_1(df, vis_id, role, workstation_ID, Metric_Desc, tStamp_)
    View(df1)
    df_x <- df1 %>% 
      rowwise() %>%
      mutate(tps = paste0(unique(unlist(strsplit(.data[[Metric_Desc]], "[|]"))) , collapse = ' ' )) %>%
      mutate(n_distinct = n_distinct(unlist(strsplit(.data[[Metric_Desc]], "[|]"))) ) %>%
      mutate(n = length(unlist(strsplit(.data[[Metric_Desc]], "[|]"))) )
    
    # get lexicons list to be removed 
    df_x2 <- data.frame(lexicons = unlist(strsplit(df_x$tps, " ")))
    lexicons_doc_freq <- df_x2 %>% #document frequency of each action
      group_by(lexicons)%>%
      summarise(n=n()) %>%
      arrange(desc(n))
    mostfreq <- head(lexicons_doc_freq,l$Mostfreq_by_rank_thres)
    temp <- lexicons_doc_freq %>%
      filter(n<=l$Leastfreq_by_seqFreq_thres)
    leastfreq <- temp$lexicons 
    df <- df %>%
      mutate(notFreq = !.data[[Metric_Desc]] %in% mostfreq & !.data[[Metric_Desc]] %in% leastfreq)
    df <- df[df$notFreq == 'TRUE', ] 
    return(
      list(
        'lexicons_freq' = lexicons_doc_freq, 
        'ea1_result' = ea_1(df, vis_id, role, workstation_ID, Metric_Desc, tStamp_))
      )
  } # 22429
  #return(df)
}
