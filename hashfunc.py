# write the hash function for generating min hashes
import sys
from random import randrange
from helper import nextPrime
# m: number of permutations you defined e.g. 245
# bag: ex. bag with id 7038: {'IP_FLOWSHEET_ACCEPTED 1', 'MR_COMM_MGT_ACCESS 1', 'MR_COMM_MGT_EXIT 1', 'UCNNOTE_PEND 1'}
def getMH(m, bag, bagId, dic_bagId_MH):
  b=5
  #b = randrange(15)
  # p: a prime number larger than length of unique shingles
  #p = 26141
  mh_list = []
  p = sys.maxsize+30
  for i in range(0, m):
    min_hash = sys.maxsize + 1
    a = nextPrime(b)
    b = nextPrime(a+1)
    for action in bag:
      hash_val = (a*hash(action)+b)%p
      #hash_val = hash(action)
      if hash_val<min_hash:
        min_hash = hash_val
    mh_list.append(min_hash)
  dic_bagId_MH[bagId] = mh_list
  return dic_bagId_MH
  
def get_mh_list(m, bag, bagId, p):
  b = 5
  # p: a prime number larger than length of unique shingles
  #p = 26141
  mh_list = []
  p = sys.maxsize+30
  for i in range(0, m):
    min_hash = sys.maxsize + 1
    a = nextPrime(b)
    b = nextPrime(a+1)
    for action in bag:
      hash_val = (a*hash(action)+b)%p
      #hash_val = hash(action)
      if hash_val<min_hash:
        min_hash = hash_val
    mh_list.append(min_hash)
  return mh_list
  

  
