# %%
import pprint

def prints(msg):
  pp = pprint.PrettyPrinter(width=30)
  return pp.pprint(msg)
  
# %%

from pymongo import MongoClient

client = MongoClient('localhost', 27020)
db = client.test_database


# %%

# from bson.objectid import ObjectId

# def get(post_id):
#   document = client.db.collection.find_one({'_id': ObjectId(post_id)})


# # %%
# fruits = db.fruits

# datum = [{"apple": 1, "banana": 2, "task": [3,4]},
#       {"author": "Eliot", "title": "fun"}]
# fruits.insert_many(datum)
# # %%

# b = [i for i in fruits.find()]
# print(b)

# %%

class Block:
  def __init__(self, b):
    self.timestamp = b['timestamp']
    self.prev_hash = b['prev_hash']
    self.current_hash = b['current_hash']
    self.nonce = b['nonce']
    self.transaction = b['transaction']
    self.merkle_root = b['merkle_root']

b1 = {
  'timestamp': 432143,
  'prev_hash': '0',
  'current_hash': '1',
  'nonce': 11,
  'transaction': '7788y77',
  'merkle_root': 'h984nfn87v'
}
b2 = {
  'timestamp': 432144,
  'prev_hash': '1',
  'current_hash': '2',
  'nonce': 11,
  'transaction': '7788y77',
  'merkle_root': 'h984nfn87v'
}
b3 = {
  'timestamp': 432145,
  'prev_hash': '2',
  'current_hash': '3',
  'nonce': 11,
  'transaction': '7788y77',
  'merkle_root': 'h984nfn87v'
}

blockchain = [Block(b1), Block(b2), Block(b3)]

# %%

records = [i.__dict__ for i in blockchain]
bcs = db.bcs

bcs.insert_many(records)

# %%
print([bc for bc in bcs.find()])


# client2 = MongoClient('localhost', 27021)
# db2 = client2.bcs
# blockchain2 = [Block(b1)]
# db2.docu.insert_many([i.__dict__ for i in blockchain2])
# print([bc for bc in db2.docu.find()])


