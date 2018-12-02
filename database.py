import subprocess
from pymongo import MongoClient
import os

class Database:
  def __init__(self, peerID):
    self.port = 27017
    self.peerID = peerID
    self._start()
    self._initDB(peerID)

  def _start(self):
    # print('start database')
    if not os.path.exists("db"):
      os.makedirs("db")
    self.main = subprocess.Popen(["mongod", "--dbpath", "./db/", "--port", str(self.port)], stdout=subprocess.PIPE)
    # print(a.stdout.decode())

  def _initDB(self, peerID):
    client = MongoClient('localhost', self.port)
    self.db = client.blockchain_db
    self.blockchain = self.db[peerID].blockchain
    self.seq = self.db[peerID].seq
    self.unspent = self.db[peerID].unspent
    if len([i for i in self.seq.find()]) == 0:
      self.seq.insert_one({self.peerID: 0})
    if not [i for i in self.unspent.find()]:
      self.unspent.insert_one({})

  def insert(self, data):
    b = data.copy()
    self.blockchain.insert_many(b)
  
  def overwrite(self, data):
    # request = [DeleteMany(filter={}), InsertMany(data)]
    self.blockchain.delete_many(filter={})
    self.blockchain.insert_many(data.copy())

  def updateSeq(self, seq):
    self.seq.replace_one({}, seq)
  
  def load(self):
    seq = [i for i in self.seq.find({}, {'_id': False})]
    unspent = [i for i in self.unspent.find({}, {'_id': False})]
    return seq[0], unspent, [i for i in self.blockchain.find({}, {'_id': False})]


  def close(self):
    self.main.terminate()


