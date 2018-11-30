# %%
import pprint
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.test_database


# %%

db.products.delete_many({})
db.products.insert_one( {} )
db.products.replace_one({}, {"a": 3})
# db.products.replace_one({}, {"item": "book", "qty": 40})
[i for i in db.products.find()]

# %%

class B:
  def __init__(self, bk):
    bk = 5

class A:
  def __init__(self):
    self.a = 1
    self.b = B(self.a)


a = A()
a.a, a.b.a










