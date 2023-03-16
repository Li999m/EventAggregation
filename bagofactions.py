import math

# bag representation of each tps
def oneShingling(tps_list):
  id = 0
  total_set = set()
  # id - tps as a string
  id_tps_dic = {}
  # id - tps as a set of 'action freq'
  id_bagoftps_dic = {}
  for tps in tps_list:
    this_set = set()
    id_tps_dic[id] = tps
    this_bag = {}
    actions = tps.split(' ')
    for action in actions:
      if action not in this_bag:
        this_bag[action] = 1
      else:
        this_bag[action] = this_bag[action]+1
    for action, freq in this_bag.items():
      for i in range(1, freq+1):
        this_set.add(action+' '+str(i))
        total_set.add(action+' '+str(i))
    id_bagoftps_dic[id] = this_set
    id+=1
  return id_bagoftps_dic, total_set

# refer STANFORD paper for frequency updates.
# *n: number of distinct tps
# *dic_tf: for action i, how many tps this action present in
def oneShingling_tfidf(id, tps_list, n, dic_tf):
  total_set = set()
  # id - tps as a string
  id_tps_dic = {}
  # id - tps as a set of 'action freq'
  id_bagoftps_dic = {}
  for tps in tps_list:
    this_set = set()
    id_tps_dic[id] = tps
    this_bag = {}
    actions = tps.split('|')
    # frequency by action
    for action in actions:
      if action not in this_bag:
        this_bag[action] = 1
      else:
        this_bag[action] = this_bag[action]+1
    normalize_factor = 0
    updated_bag_tfidf = {}
    for action, freq in this_bag.items():
      if action == '': continue
      # n: number of tps instances: will be changing
      # doc frequency by action (with duplications; instances): will be changing
      # log term meaning: if an action appear in fewer tps, it has higher weight, and vice versa.
      tfidf_freq = (freq**0.5)*math.log(n/dic_tf[action])
      normalize_factor += tfidf_freq
      updated_bag_tfidf[action] = tfidf_freq
      #print(action, dic_tf[action], freq, tfidf_freq)
    updated_bag_tfidf_normalize = {}
    for action, freq in updated_bag_tfidf.items():
      # why 100? I follow the choice of paper. For example in clinic RADONC 1 (test run), the size of tps range from (1,84), so I think 100 is appropriate for our case
      normalized_freq = round((freq/normalize_factor)*100)
      updated_bag_tfidf_normalize[action] = normalized_freq
      #print(action, normalized_freq)
    #print('\n ')
    for action, freq in updated_bag_tfidf_normalize.items():
      #print(action, freq)
      for i in range(1, freq+1):
        this_set.add(action+' '+str(i))
        total_set.add(action+' '+str(i))
    id_bagoftps_dic[id] = this_set
    id+=1
  return id_bagoftps_dic, total_set, id_tps_dic

# a n-gram shingling funciton for 2-gram shingles and 3-gram shingles.
#       k: k=2 or 3
def nshingling(tps_list, k):
  id = 0
  id_bagoftps_dic = {}
  id_tps_dic = {}
  total_set = set()
  for tps in tps_list:
    id_tps_dic[id] = tps
    shingle_set = set()
    actions = tps.split(' ')
    # my heuristic way of treating the case when a touchpoint has only one action.
    if k==2:
      actions = [' ']+actions+[' ']
    elif k==3:
      actions = [' ', ' ']+actions+[' ',' ']
    for i in range(0, len(actions)-k+1):
      shingle = ' '.join(actions[i:i+k])
      shingle_set.add(shingle)
      total_set.add(shingle)
    id_bagoftps_dic[id] = shingle_set
    id+=1
  return id_bagoftps_dic, total_set, id_tps_dic
 
def nshingling_tfidf(tps_list, k, dic_tf):
  n = len(tps_list)
  id = 0
  id_bagoftps_dic = {}
  id_tps_dic = {}
  total_set = set()
  for tps in tps_list:
    this_set = set()
    id_tps_dic[id] = tps
    shingle_set = set()
    actions = tps.split(' ')
    # my heuristic way of treating the case when a touchpoint has only one action.
    if k==2:
      actions = [' ']+actions+[' ']
    elif k==3:
      actions = [' ', ' ']+actions+[' ',' ']
    # bag representation of each tps
    this_bag = {}
    for i in range(0, len(actions)-k+1):
      shingle = ' '.join(actions[i:i+k])
      this_bag[shingle] = 1 if shingle not in this_bag else this_bag[shingle]+1
    normalize_factor=0
    updated_bag_tfidf = {}
    # update the freq as tfidf
    for shingle, freq in this_bag.items():
      if shingle == '': continue
      tfidf_freq = (freq**0.5)*math.log(n/dic_tf[shingle])
      normalize_factor += tfidf_freq
      updated_bag_tfidf[shingle] = tfidf_freq
    # normalize the freq
    updated_bag_tfidf_normalize = {}
    for shingle, freq in updated_bag_tfidf.items():
      normalized_freq = round((freq/normalize_factor)*100)
      updated_bag_tfidf_normalize[shingle] = normalized_freq
    # bag to set
    for shingle, freq in updated_bag_tfidf_normalize.items():
      for i in range(1, freq+1):
        this_set.add(shingle+' '+str(i))
        total_set.add(shingle+' '+str(i))
    id_bagoftps_dic[id] = this_set
    id+=1
  return id_bagoftps_dic, total_set, id_tps_dic

    
