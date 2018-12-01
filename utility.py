from hashlib import sha256
import uuid
import time

def _getTime():
  return int(str(time.time()).replace('.',''))
 
def _getPeerID(_id):
  if _id != "":
    return str(_id)
  return uuid.uuid4().hex[:20]  

def _calc_hash(a):
  s = sha256()
  s.update(a.encode())
  return s.hexdigest()

def _calc_merkle_root(tx):
  def itera(ls):
    print(ls)
    if len(ls) <= 1:
      return ls
    res = []
    for i in range(0,len(ls), 2):
      res.append(_calc_hash( ls[i] + ls[min(i+1, len(ls)-1)] )) 
    return itera(res)
  return itera(tx)[0]

  
  
  
  
