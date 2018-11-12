# %%

from pymongo import MongoClient
import datetime

client = MongoClient('localhost', 27017)
db = client.test_database

post = {
  "author": "Mike",
  "text": "my first blog",
  "tags": ["mongodb", "python", "pymon"],
  "date": datetime.datetime.utcnow()
}

# %%
posts = db.posts
post_id = posts.insert_one(post).inserted_id

print(post_id)


# %%

db.collection_name.database
db.client

# %%




