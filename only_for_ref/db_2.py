# from pymongo import MongoClient

# client = MongoClient('localhost', 27017)
# db = client.test_database


# # %%

# rec = {"a": 1, "b": 2}

# from pymongo import DeleteMany, InsertOne
# # request = [DeleteMany(filter={}), InsertOne(rec)]
# request = [InsertOne(rec)]

# db.bcs.bulk_write(request)


# data = [i for i in db.bcs.find()]
# print(data)


# start mongod server
# from multiprocessing import Process















