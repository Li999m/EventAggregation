# evaluate the results
import pandas as pd

def jaccardSimilarity(list1, list2):
  intersection_size = len(set(list1)&set(list2))
  union_size = len(set(list1)|set(list2))
  similarity = intersection_size/union_size
  similarity = float("{:.2f}".format(similarity))
  return similarity

# evaluate containment: from point center's view
def containment(neighbor, center):
  intersection_size = len(set(neighbor)&set(center))
  neighbor_size = len(set(neighbor))
  containment = intersection_size/neighbor_size
  containment = float("{:.2f}".format(similarity))
  return containment
  
def calculate_representative(tps_cluster):
  x = tps_cluster.str.split('|').to_frame().applymap(set)
  #print(x['tps'])
  y = x['tps'].explode().reset_index(drop=True).to_frame()
  z = y.groupby('tps').size().to_dict() # z is the doc frequency
  n = len(x) #total elements# in this cluster
  representative = set()
  for lexicon in z:
    if z[lexicon]/n>0.5: representative.add(lexicon)
  #print(representative)
  return representative

def evaluate(buckets, id_tps_dic):
  n = len(buckets.keys())
  if n == 0: return 0, 0, 0
  denom = 0
  TP = 0
  accum_avg_sim = 0
  bucketed_n = 0
  n=0
  lsh_centroid_dic = {}
  lsh_intrasim_dic = {}
  lsh_intrapre_dic = {}
  for lsh, id_list in buckets.items():
    nid = len(id_list)
    
    # if a cluster contains only one tps, skip
    if nid<=1:
      continue
      
    n+=1
    bucketed_n += nid
    accum_sim = 0
    
    # one cluster
    
    tps_cluster = [id_tps_dic[id] for id in id_list]
    
    #tps_vectors = [loaded_model[action] for tps in tps_cluster for action in tps.split(' ') if action in loaded_model]
    representative = calculate_representative(pd.Series(tps_cluster, name='tps'))
    # print('size:', np.size(centroid))
    lsh_centroid_dic[lsh] = representative
    # intra-cluster
    avg_sim = 0
    n=0
    tp = 0
    fp = 0
    for tps in tps_cluster:
      tps_array = tps.split('|')
      similarity = jaccardSimilarity(representative, tps_array)
      #print(similarity)
      if similarity>=0.6: tp+=1
      else: fp+=1
      n+=1
      avg_sim += similarity
    avg_sim = avg_sim/n
    lsh_intrasim_dic[lsh] = avg_sim
    lsh_intrapre_dic[lsh] = tp/(tp+fp)
    #print(avg_sim)
  # inter cluster
  lsh_intersim_dic = {}
  for lsh in buckets.keys():
    if lsh not in lsh_centroid_dic: continue
    max_ = -2
    for lsh_ in buckets.keys():
      if lsh_ not in lsh_centroid_dic: continue
      if lsh!=lsh_:
        a=lsh_centroid_dic[lsh]
        #print(a)
        b=lsh_centroid_dic[lsh_]
        similarity = jaccardSimilarity(a,b)
        max_ = max(similarity, max_)
        #print(max_)
    lsh_intersim_dic[lsh] = max_
  # silhouette score
  avg_sil = 0
  n=0
  avg_intra = 0
  avg_inter = 0
  avg_intra_pre = 0
  for lsh in buckets.keys():
    if lsh in lsh_intrasim_dic:
      a = lsh_intrasim_dic[lsh]
      b = lsh_intersim_dic[lsh]
      o = lsh_intrapre_dic[lsh]
      #print(o)
      #print('cluster:', [id_tps_dic[id] for id in buckets[lsh]])
      sil = (b-a)/max(a,b)
      n+=1
      avg_intra += a
      avg_inter += b
      avg_sil+=sil
      avg_intra_pre += o
      #print(sil)
  avg_intra = avg_intra/n
  avg_inter = avg_inter/n
  avg_sil = avg_sil/n
  #print(avg_sil, avg_inter, avg_intra, avg_intra_pre/n)
  return avg_sil, avg_inter, avg_intra, avg_intra_pre/n

def getSimilarity(buckets, id_tps_dic):
  n = len(buckets.keys())
  if n == 0: return 0, 0, 0
  denom = 0
  TP = 0
  accum_avg_sim = 0
  bucketed_n = 0
  n=0
  for lsh, id_list in buckets.items():
    nid = len(id_list)
    if nid<=1:
      continue
    n+=1
    bucketed_n += nid
    accum_sim = 0
    for i in range(0, nid):
      accum_sim_this_tps = 0
      for j in range(0, nid):
        tps_a = id_tps_dic[id_list[i]].split(' ')
        tps_b = id_tps_dic[id_list[j]].split(' ')
        similarity = jaccardSimilarity(tps_a, tps_b)
        accum_sim += similarity
        accum_sim_this_tps += similarity
      avg_sim_this_tps = float("{: .2f}".format(accum_sim_this_tps/nid))
      if avg_sim_this_tps>=0.6: TP+=1
      denom+=1
    avg_sim_this_bucket = float("{: .2f}".format(accum_sim/(nid*(nid))))
    accum_avg_sim += avg_sim_this_bucket
  avg_sim = float("{: .2f}".format(accum_avg_sim/n))
  precision = float("{: .2f}".format(TP/denom))
  return avg_sim, precision, bucketed_n, n
