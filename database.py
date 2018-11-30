import subprocess
from pymongo import MongoClient

class Database:
  def __init__(self, peerID):
    self.port = 27017
    self.peerID = peerID
    self._start()
    self._initDB(peerID)

  def _start(self):
    print('start database')
    self.main = subprocess.Popen(["mongod", "--dbpath", "./db/", "--port", str(self.port)], stdout=subprocess.PIPE)
    # print(a.stdout.decode())

  def _initDB(self, peerID):
    client = MongoClient('localhost', self.port)
    self.db = client.blockchain_db
    self.blockchain = self.db[peerID].blockchain
    self.seq = self.db[peerID].seq
    if len([i for i in self.seq.find()]) == 0:
      self.seq.insert_one({self.peerID: 0})

  def insert(self, data):
    self.blockchain.insert_many(data)
  
  def overwrite(self, data):
    # request = [DeleteMany(filter={}), InsertMany(data)]
    self.blockchain.delete_many(filter={})
    self.blockchain.insert_many(data)

  def updateSeq(self, seq):
    self.seq.replace_one({}, seq)
  
  def load(self):
    seq = [i for i in self.seq.find({}, {'_id': False})]
    return seq[0], [i for i in self.blockchain.find({}, {'_id': False})]


  def close(self):
    self.main.terminate()

# a = Database('abc')
# a.overwrite([{'a': 1, 'b': 2}])
# print(a.load())
# # a.close()

# b = Database('def')
# b.overwrite([{'f':3}])
# b.insert([{'c': 1, 'd': 2}])
# print(b.load())

# d5b7dd9194       7066edfd21





