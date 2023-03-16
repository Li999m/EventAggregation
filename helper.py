###########################################
# * define a series of helper funcitons * #
###########################################
import numpy as np, pandas as pd
import os, csv, gensim
from itertools import groupby
from evaluate import jaccardSimilarity
from gensim.models import KeyedVectors
from gensim.matutils import unitvec

def isPrime(n):
  if n%2==0:
    return False
  else:
    for i in range(3,n-1):
      if n%i==0: return False
  return True

def nextPrime(n):
  while(not isPrime(n) or n==11):
    n+=1
  return n

# tf_i: frequency of touchpoint that action i present.
def tf(path, file):
  file = os.path.join(path, file)
  dic_action_freq = {}
  with open(file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      tps = row['tps']
      if len(tps) == 0: continue
      seen = set()
      actions = tps.split(' ')
      for action in actions:
        if action not in seen:
          if action not in dic_action_freq:
            dic_action_freq[action] = 1
          else:
            dic_action_freq[action] += 1
          seen.add(action)
  sorted_tuples = sorted(dic_action_freq.items(), key = lambda item: item[1], reverse=True)
  print(sorted_tuples)
  print('number of actions: %s ' % len(sorted_tuples))
  dic_action_freq = {k:v for k,v in sorted_tuples}
  return dic_action_freq

def tf_from_raw(raw_tps_list):
  dic_action_freq = {}
  for tps in raw_tps_list:
    if isinstance(tps, float): continue
    if len(tps) == 0: continue
    seen = set()
    actions = tps.split(' ')
    for action in actions:
      if action not in seen:
        if action not in dic_action_freq:
          dic_action_freq[action] = 1
        else:
          dic_action_freq[action] += 1
        seen.add(action)
  sorted_tuples = sorted(dic_action_freq.items(), key = lambda item: item[1], reverse=True)
  #print(sorted_tuples)
  print('number of actions: %s ' % len(sorted_tuples))
  dic_action_freq = {k:v for k,v in sorted_tuples}
  return dic_action_freq

def tf_from_raw_shingle(raw_tps_list, k):
  dic_shingle_freq = {}
  for tps in raw_tps_list:
    if len(tps) == 0: continue
    seen = set()
    actions = tps.split(' ')
    if k==2:
      actions = [' ']+actions+[' ']
    elif k==3:
      actions = [' ', ' ']+actions+[' ',' ']
    for i in range(0, len(actions)-k+1):
      shingle = ' '.join(actions[i:i+k])
      if shingle not in seen:
        if shingle not in dic_shingle_freq:
          dic_shingle_freq[shingle] = 1
        else:
          dic_shingle_freq[shingle] += 1
        seen.add(shingle)
  print('number of distinct shingles: %s' % len(dic_shingle_freq.keys()))
  return dic_shingle_freq


def tf_test(path, file, f, f_least):
  file = os.path.join(path, file)
  dic_action_freq = {}
  with open(file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      tps = row['tps']
      if len(tps) == 0: continue
      seen = set()
      actions = tps.split(' ')
      for action in actions:
        if action not in seen:
          if action not in dic_action_freq:
            dic_action_freq[action] = 1
          else:
            dic_action_freq[action] += 1
          seen.add(action)
  sorted_tuples = sorted(dic_action_freq.items(), key = lambda item: item[1], reverse=True)
  #print(sorted_tuples)
  print('number of actions: %s ' % len(sorted_tuples))
  dic_action_freq = {k:v for k,v in sorted_tuples}
  rmv = round(len(sorted_tuples)*f)
  rmv_least = round(len(sorted_tuples)*f_least)
  most_freq_list = [k for k,v in sorted_tuples[0:rmv]]
  
  least_freq_list = [k for k,v in sorted_tuples[len(sorted_tuples)-rmv_least:]]
  freq_list = most_freq_list + least_freq_list
  return freq_list, least_freq_list, most_freq_list

# get length of longest tps
def getLongest(tps_list):
  longest = 0
  shortest = 100
  for tps in tps_list:
    actions = tps.split(' ')
    this_len = len(actions)
    longest = max(longest, this_len)
    shortest = min(shortest, this_len)
  print(longest, shortest)
  return longest

def initialMatrix(x, y):
  initMatrix = np.zeros((x,y))
  return initMatrix

def fillSimilarityMatrix(similarity_matrix, overlapping_buckets, bandIdx):
  for idx, bucket_str in enumerate(overlapping_buckets):
    if idx % 50 == 0:
      completed = (idx/len(overlapping_buckets))*100
      print('Filling similarity matrix: ... band %s .... %s percent ....' % (bandIdx, completed))
    bucket = bucket_str.split(',')
    for i in range(0, len(bucket)):
      for j in range(i+1, len(bucket)):
        similarity_matrix[int(bucket[i])] [int(bucket[j])] = 1
        similarity_matrix[int(bucket[j])] [int(bucket[i])] = 1
  return similarity_matrix

def getSimilarityPairs(similarity_pairs, overlapping_buckets, bandIdx):
  for idx, bucket_str in enumerate(overlapping_buckets):
    if idx % 50 == 0:
      completed = (idx/len(overlapping_buckets))*100
      print('Getting similarity pairs: ... band %s .... %s percent ....' % (bandIdx, completed))
    bucket = bucket_str.split(',')
    for i in range(0, len(bucket)):
      for j in range(i+1, len(bucket)):
        temp = (int(bucket[i]), int(bucket[j]))
        temp1 = (int(bucket[j]), int(bucket[i]))
        if temp not in similarity_pairs:
          similarity_pairs.append(temp)
        if temp1 not in similarity_pairs:
          similarity_pairs.append(temp1)
  return similarity_pairs
  
def write_to_csv(tps_list):
  tps_df = pd.DataFrame(tps_list)
  tps_df.columns=['tps']
  tps_df.to_csv('tps_list.csv')

def denoise_by_role(temp_path, raw_tps_list, freq_list):
  wname = os.path.join(temp_path, role+'_denoised.csv')
  tps_list = []
  for tps in raw_tps_list:
    actions = tps.split(' ')
    actions_updated = [action for action in actions if action not in freq_list]
    actions_updated = [action[0] for action in groupby(actions_updated)]
    actions_updated_str = ' '.join(actions_updated)
    if actions_updated_str not in tps_list:
      tps_list.append(actions_updated_str)
  

def normalize(path, file, freq_list):
  file = os.path.join(path,file)
  name = file.split('.')[0]
  wname = name+'_normalized_1.csv'
  wfile = os.path.join(path, wname)
  raw_tps_list = [] # a list of normalized tps
  new_tps_list = [] # a set of normalized tps
  with open(file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    header = reader.fieldnames+['normalized_tps']
    header_size = len(header)
    with open(wfile, 'a', newline = '') as wcsvfile:
      writer = csv.DictWriter(wcsvfile, fieldnames=header)
      writer.writeheader()
      for row in reader:
        tps = row['tps']
        actions = tps.split(' ')
        actions_updated = [action for action in actions if action not in freq_list]
        actions_updated = [action[0] for action in groupby(actions_updated)]
        actions_updated_str = ' '.join(actions_updated)
        row['normalized_tps'] = actions_updated_str
        writer.writerow(row)
        if len(actions_updated)<1: continue
        raw_tps_list.append(actions_updated_str)
        if actions_updated_str not in new_tps_list:
          new_tps_list.append(actions_updated_str)
  return raw_tps_list, new_tps_list, wname

def tagFile(file, rpath, wpath, dic_tagging_Ktps_VclassID, centers):
  rfile = os.path.join(rpath, file)
  name = file.split('.')[0]
  wname = name+'_tagged_1.csv'
  wfile = os.path.join(wpath, wname)
  with open(rfile, newline = '') as csvfile:
    reader = csv.DictReader(csvfile)
    header = reader.fieldnames
    header = header+['Bucket ID']+['Is Bucketed']+['Is Center']
    with open(wfile, 'a', newline = '') as wcsvfile:
      writer = csv.DictWriter(wcsvfile, fieldnames=header)
      writer.writeheader()
      for row in reader:
        tps = row['tps']
        if len(tps)==0:
          row['Bucket ID'] = 0
          row['Is Bucketed'] = ''
          row['Is Center'] = ''
          writer.writerow(row)
          continue
        try:
          bucketID = dic_tagging_Ktps_VclassID[tps]
          row['Bucket ID'] = bucketID
          row['Is Bucketed'] = 'Y'
          if tps in centers:
            row['Is Center'] = 'Y'
        except:
          bucketID = ''
          row['Bucket ID'] = bucketID
          row['Is Bucketed'] = ''
          row['Is Center'] = ''
        writer.writerow(row)
  return wname

def addTypicalTPS(file, rpath, wpath, typical_tps_by_bucket):
  rfile = os.path.join(rpath, file)
  name = file.split('.')[0]
  wname = name+'_tagged_2.csv'
  wfile = os.path.join(wpath, wname)
  with open(rfile, newline = '') as csvfile:
    reader = csv.DictReader(csvfile)
    header = reader.fieldnames
    header = header+['typical tps']
    with open(wfile, 'a', newline = '') as wcsvfile:
      writer = csv.DictWriter(wcsvfile, fieldnames=header)
      writer.writeheader()
      for row in reader:
        bid = row['Bucket ID']
        if len(bid)==0:
          row['typical tps'] = row['tps']
          writer.writerow(row)
          continue
        try:
          typical_tps = typical_tps_by_bucket[bid]
          #print(bid, typical_tps)
          row['typical tps'] = typical_tps
        except:
          typical_tps = ''
          row['typical tps'] = typical_tps
        writer.writerow(row)
  return wname

def computeMean(tpsID_list, raw_tps_list):
  return

def getSimilarity_simple(result_dic, id_tps_dic):
  return

def calculate_centroid(word_vectors):
    # Convert the list of word vectors to a matrix
    word_matrix = np.array(word_vectors)
    # Calculate the centroid by taking the row-wise mean
    centroid = np.mean(word_matrix, axis=0)
    # Normalize the centroid to unit length
    centroid = unitvec(centroid)
    return centroid
  
def evaluate_word2vec(buckets, id_tps_dic):
  n = len(buckets.keys())
  if n == 0: return 0, 0, 0
  denom = 0
  TP = 0
  accum_avg_sim = 0
  bucketed_n = 0
  n=0
  loaded_model = KeyedVectors.load_word2vec_format('/Users/xinyun/Desktop/Event Aggregation/evaluation/my_model_derm3.bin', binary=True)
  lsh_centroid_dic = {}
  lsh_intrasim_dic = {}
  lsh_intrapre_dic = {}
  for lsh, id_list in buckets.items():
    nid = len(id_list)
    if nid<=1:
      continue
    n+=1
    bucketed_n += nid
    accum_sim = 0
    tps_cluster = [id_tps_dic[id] for id in id_list]
    tps_vectors = [loaded_model[action] for tps in tps_cluster for action in tps.split(' ') if action in loaded_model]
    centroid = calculate_centroid(tps_vectors)
    # print('size:', np.size(centroid))
    lsh_centroid_dic[lsh] = centroid
    # intra-cluster
    avg_sim = 0
    n=0
    tp = 0
    fp = 0
    for tps in tps_cluster:
      tps_vector = [loaded_model[action] for action in tps.split(' ') if action in loaded_model]
      tps_centroid = np.mean(tps_vector, axis=0)
      # print("size:", np.size(tps_centroid))
      tps_centroid = unitvec(tps_centroid)
      # cluster centroid and tps centroid
      similarity = loaded_model.cosine_similarities(centroid, tps_centroid.reshape(1,-1))
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
        similarity = loaded_model.cosine_similarities(a, b.reshape(1,-1))
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
  print(avg_sil, avg_inter, avg_intra, avg_intra_pre/n)
  return

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
    #print(nid, [id_tps_dic[id] for id in id_list])
    for i in range(0, nid):
      accum_sim_this_tps = 0
      for j in range(0, nid):
        tps_a = id_tps_dic[id_list[i]].split('|')
        tps_b = id_tps_dic[id_list[j]].split('|')
        similarity = jaccardSimilarity(tps_a, tps_b)
        accum_sim += similarity
        accum_sim_this_tps += similarity
      avg_sim_this_tps = float("{: .2f}".format(accum_sim_this_tps/nid))
      #print(avg_sim_this_tps)
      if avg_sim_this_tps>=0.6: TP+=1
      denom+=1
    avg_sim_this_bucket = float("{: .2f}".format(accum_sim/(nid*(nid))))
    accum_avg_sim += avg_sim_this_bucket
  avg_sim = float("{: .2f}".format(accum_avg_sim/n))
  precision = float("{: .2f}".format(TP/denom))
  return avg_sim, precision, bucketed_n, n

def tagFile_updated(file, rpath, wpath, dic_tagging_Ktps_VclassID):
  rfile = os.path.join(rpath, file)
  name = file.split('.')[0]
  wname = name+'_tagged_1.csv'
  wfile = os.path.join(wpath, wname)
  with open(rfile, newline = '') as csvfile:
    reader = csv.DictReader(csvfile)
    header = reader.fieldnames
    header = header+['updated Bucket ID']+['updated Is Bucketed']
    with open(wfile, 'a', newline = '') as wcsvfile:
      writer = csv.DictWriter(wcsvfile, fieldnames=header)
      writer.writeheader()
      for row in reader:
        tps = row['typical tps']
        role = row['newROLE']
        if len(tps)==0:
          row['updated Bucket ID'] = 0
          row['updated Is Bucketed'] = ''
          writer.writerow(row)
          continue
        try:
          bucketID = dic_tagging_Ktps_VclassID[role][tps]
          row['updated Bucket ID'] = bucketID
          row['updated Is Bucketed'] = 'Y'
        except:
          bucketID = ''
          row['updated Bucket ID'] = bucketID
          row['Is Bucketed'] = ''
        writer.writerow(row)
  return wname

def tagFile_by_role(file, rpath, wpath, dic_tagging_Ktps_VclassID, centers):
  rfile = os.path.join(rpath, file)
  name = file.split('.')[0]
  wname = name+'_tagged_1.csv'
  wfile = os.path.join(wpath, wname)
  with open(rfile, newline = '') as csvfile:
    reader = csv.DictReader(csvfile)
    header = reader.fieldnames
    header = header+['Bucket ID']+['Is Bucketed']+['Is Center']
    with open(wfile, 'a', newline = '') as wcsvfile:
      writer = csv.DictWriter(wcsvfile, fieldnames=header)
      writer.writeheader()
      for row in reader:
        role = row['newROLE']
        tps = row['tps']
        if len(tps)==0:
          row['Bucket ID'] = 0
          row['Is Bucketed'] = ''
          row['Is Center'] = ''
          writer.writerow(row)
          continue
        if role not in set(['Physician', 'Resident', 'Licensed Nurse']):
          row['Bucket ID'] = 'other'
          row['Is Bucketed'] = ''
          row['Is Center'] = ''
        else:
          try:
            bucketID = dic_tagging_Ktps_VclassID[role][tps]
            row['Bucket ID'] = bucketID
            row['Is Bucketed'] = 'Y'
            if tps in centers:
              row['Is Center'] = 'Y'
          except:
            bucketID = ''
            row['Bucket ID'] = bucketID
            row['Is Bucketed'] = ''
            row['Is Center'] = ''
        writer.writerow(row)
  return wname

def denoise_by_role(raw_tps_list, tps_list, freq_list):
  file = os.path.join(path,file)
  name = file.split('.')[0]
  wname = name+'_normalized_1.csv'
  wfile = os.path.join(path, wname)
  raw_tps_list = [] # a list of normalized tps
  new_tps_list = [] # a set of normalized tps
  with open(file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    header = reader.fieldnames+['normalized_tps']
    header_size = len(header)
    with open(wfile, 'a', newline = '') as wcsvfile:
      writer = csv.DictWriter(wcsvfile, fieldnames=header)
      writer.writeheader()
      for row in reader:
        tps = row['tps']
        actions = tps.split(' ')
        actions_updated = [action for action in actions if action not in freq_list]
        actions_updated = [action[0] for action in groupby(actions_updated)]
        actions_updated_str = ' '.join(actions_updated)
        row['normalized_tps'] = actions_updated_str
        writer.writerow(row)
        if len(actions_updated)<1: continue
        raw_tps_list.append(actions_updated_str)
        if actions_updated_str not in new_tps_list:
          new_tps_list.append(actions_updated_str)
  return raw_tps_list, new_tps_list, wname
  
"""
def x():
  c=0
  cnt=0
  cc=0
tps_set = set()
visit_set = set()
rowID = 0
with open(file, newline='') as csvfile:
   reader = csv.DictReader(csvfile)
   for row in reader:
     rowID+=1
     tps = row['normalized_tps']
     if 'BEGIN' in tps:
       cc+=1
       #print(rowID, row['vis_id'], tps)
     b = row['Is Bucketed']
     if('RIS_BEGIN_EXAM' in tps or 'RIS_END_EXAM' in tps):
       #print(tps)
     if('ADD' in tps):
       print(tps)
     if('MR_EXTERNAL_VIDEOCONFERENCE_CONNECTED' in tps):
       cnt+=1
       visit_set.add(row['vis_id'])
     #print(b != 'Y', len(tps.split(' ')), tps not in tps_set)
     if b!='Y' and len(tps.split(' '))==1 and tps not in tps_set:
       c+=1
       #print(tps)
     tps_set.add(tps)



action_begin_set = set()
action_end_set = set()
visit_set = set()
rowID = 0
action_other_set = set()
with open(file, newline='') as csvfile:
   reader = csv.DictReader(csvfile)
   #print(reader.fieldnames)
   for row in reader:
     action = row['Metric_Desc']
     rowID+=1
     if 'BEGIN' in action:
       action_begin_set.add(action)
     if 'END' in action:
       action_end_set.add(action)
     if 'ADD' in action:
       action_other_set.add(action)
"""
