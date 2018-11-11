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

class T1(Thread):
  def __init__(self):
    

def aaa(a):
  print(a)
  def bbb(b):
    print(a+b)

  bbb(3)

aaa(4)

# %%
a = 3
if not (a>5 and
  a>7):
  print('yes')
else:
  print('no')


# %%
