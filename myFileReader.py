# file reader
# import csv, os, pyreadr

#def readTPSasList(path, file):
#  file = os.path.join(path,file)
#  tps_list = []
#  with open(file, newline='') as csvfile:
#    reader = csv.DictReader(csvfile)
#    for row in reader:
#      tps = row['tps']
#      if len(tps)<1: continue
#      if tps not in tps_list:
#        tps_list.append(tps)
#  return tps_list
  
def readRData(df):
  tpss_pd_series = df['Metric_Desc']
  #print(tpss_pd_series)
  return tpss_pd_series
  
def readDocFreq(df):
  doc_freq_dic = dict(zip(df['lexicons'], df['n']))
  return doc_freq_dic
     
