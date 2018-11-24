import subprocess
from pymongo import MongoClient

class Database:
  def __init__(self, peerID):
    self.port = 27017
    self.peerID = peerID
    self._start()
    self._initDB(peerID)

  def _start(self):
    print('start')
    self.main = subprocess.Popen(["mongod", "--dbpath", "./db/", "--port", str(self.port)], stdout=subprocess.PIPE)
    # print(a.stdout.decode())

  def _initDB(self, peerID):
    client = MongoClient('localhost', self.port)
    self.db = client.blockchain_db
    self.blockchain = self.db[peerID]

  def insert(self, data):
    self.blockchain.insert_many(data)
  
  def overwrite(self, data):
    # request = [DeleteMany(filter={}), InsertMany(data)]
    self.blockchain.delete_many(filter={})
    self.blockchain.insert_many(data)
  
  def load(self):
    return [i for i in self.blockchain.find()]

  def close(self):
    self.main.terminate()

a = Database('abc')
a.overwrite([{'a': 1, 'b': 2}])
print(a.load())
# a.close()

b = Database('def')
b.overwrite([{'f':3}])
b.insert([{'c': 1, 'd': 2}])
print(b.load())

