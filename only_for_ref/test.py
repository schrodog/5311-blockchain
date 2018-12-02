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

# %%

tx = {'in': [{'addr': 'coinbase'}, 
      {'addr': '12', 'prev_out': 'fjldks', 'value':135 }],
  'out': [{'addr': '7066edfd21d5b7dd9194', 'value': 100 }, 
          {'addr': '76', 'value': 234 }], 
  'timestamp': 15432153057109854}

strs = ""
for s in ['in', 'out']:
  for i in tx[s]:
    for j in i:
      strs += str(i[j])
strs += str(tx['timestamp'])
print(strs)

# %%
class B():
  def __init__(self, a):
    self.ok = a

  def get(self, a):
    self.k = a

  def go(self,a):
    self.k.clear()
    self.k.append(a)

class A():
  def __init__(self):
    self.a = [1,3,5]
    self.b = B(3)
    self.b.get(self.a)


a = A()
print(a.a)
a.b.go(3)
print(a.a, a.b.k)

# %%
for i in range(2):
  for j in range(8):
    print(i,j)
    if j == 1:
      break

# %%
a = [('a',1),('a',3),('b',7),('a',12)]

sum([i[1] for i in a if i[0] == 'a'])


