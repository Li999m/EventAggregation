from bagofactions import oneShingling_tfidf
from myFileReader import readRData, readDocFreq
from hashfunc import getMH
import random, pandas as pd
from helper import getSimilarity
from evaluate import evaluate
import os

def LSH(l, r, df, freq):
  l = int(l)
  r = int(r)
  m = int(l*r)
  print(m)
  # in STANDFORD paper l: number of bands or iteration; nband
  # in STANDFORD paper k: number of rows for each band if viewed as a matrix; r
  ngram = 1 # specify that this is a bag of events representation.
 
  # section 0.1 read tps as panda series
  tps_list = []
  try:
    tps_pd_series = readRData(df)  #todo
  except:
    print('error: read df error!')
  print('number of distinct touchpoints are %s:' % len(tps_pd_series.unique()))
  
  #0.2 read lexicons freqeuncy
  try:
    dic_tf = readDocFreq(freq)
  except:
    print('error: read freq error!')

  
  # 0.3 bag of events 
  #     id_tps_dic: touchpoint by index (int type)
  #     dic_id_bagoftps: "bag of words" representation of touchpoints by index
  #     total_set:
  dic_id_bagoftps, total_set, id_tps_dic = oneShingling_tfidf(1, tps_pd_series.unique().tolist(), len(tps_pd_series.tolist()), dic_tf) if ngram==1 else nshingling_tfidf(tps_list, ngram, dic_tf)
  print('Length of the total set: %s' % len(total_set))
  
  #1.0 scan bags to create m MH-signatures for each tps
  dic_bagId_MH = {}
  # bag: "bag of words" representation of touchpoint
  try:
    for bagId, bag in dic_id_bagoftps.items():
    # create minhashing by index: idea is that min(hashing("action_freq"))
      dic_bagId_MH = getMH(m, bag, bagId, dic_bagId_MH)
  except:
    print('Error: creating MH-signatures!')

  
  #1.1 create LSH-signatures for each tps
  seen = set()
  similarity_pairs = []
  cluster = {}
  result_dic = {}
  for i in range(0,l):
    random_indices = random.sample(range(0,m),r)
    print(random_indices)
    dic_bagId_LSH = {}
    for bagId, MH in dic_bagId_MH.items():
      temp = []
      for indice in random_indices:
        temp.append(str(MH[indice]))
      LSH_signature = ' '.join(temp)
      
      # bagID is the ID for each unique touchpoint
      # LSH_signature is the hash for one touchpoint
      dic_bagId_LSH[str(bagId)] = LSH_signature
      if LSH_signature in result_dic:
        result_dic[LSH_signature].append(bagId)
      else:
        result_dic[LSH_signature] = [bagId]
  avg_silhoutte, avg_inter_cluster, avg_intra_cluster, avg_intra_precision = evaluate(result_dic, id_tps_dic)
  print(avg_silhoutte, avg_inter_cluster, avg_intra_cluster, avg_intra_precision)
  # compute average similarity of clustering results
  avg_similarity, precision, bucketed_n, number_of_buckets = getSimilarity(result_dic, id_tps_dic)
  
  print('average similarity: %s' % avg_similarity)
  print('precision: %s' % precision)
  print('Number of buckets: %s' % number_of_buckets)
  print('Number of bucketed touchpoint: %s' % bucketed_n)
  recall_rate = bucketed_n/len(tps_pd_series.unique().tolist())
  recall_rate = '%.2f' % recall_rate
  print('Recall: %s' % recall_rate)
  return ["{:.2f}".format(avg_silhoutte), "{:.2f}".format(avg_inter_cluster), "{:.2f}".format(avg_intra_cluster), "{:.2f}".format(avg_intra_precision), avg_similarity, number_of_buckets, recall_rate]
