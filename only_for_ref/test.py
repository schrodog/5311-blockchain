# %%

class BadInitClass:
  def __init__(self, name):
    self.name = name

  def name_foo(self, arg):
    print(self)
    print(arg)
    print("name is", self.name)

class MyNewClass:
  def __init__(self):
    self.bad = BadInitClass(name="test bad")
    
  def conn(self, msg):
    print('conn')
    self.bad.name_foo(msg)
  def new_foo(self, arg):
    print(self)
    print(arg)

new_obj = MyNewClass()
new_obj.conn("my msg")
new_obj.new_foo("NewFoo")

# %%
from threading import Thread
import time

class T1(Thread):
  def __init__(self):
    super(T1,self).__init__()

  def run(self):
    i = 0
    while True:
      i += 1
      print('a')
      if i>4:
        return
    print('end')

for _ in range(1):
  t = T1()
  t.start()
  # t.join()





# %%
from hashlib import sha256
t = 'coinbase7066edfd21d5b7dd919410015432153057109854'

s = sha256()
s.update(t.encode())
s.hexdigest()

# %%
a = [(1,0),(2,1)]
b = [(1,0,30),(1,1,60), (1,2,20), (2,1,25)]


[j for j in b if all([i != j[:2] for i in a])]

