import sys
import threading
import time
import logging

class T2(threading.Thread):
  def __init__(self, num):
    super(T2, self).__init__()
    print('num is',num)

  def run(self):
    i = 0
    while i<3:
      print("hello world")
      if i>1:
        return
      print("unreachable")
      i += 1

class T1(threading.Thread):
  def __init__(self):
    super(T1, self).__init__()
    self.n = 1

  def run(self):
    while True:
      t2 = T2(self.n)
      t2.setDaemon(True)
      t2.start()
      # while True:
      print("next")
      t2.join()
      self.n += 1
      if self.n > 5:
        return
      # break


t1 = T1()
t1.start()
t1.join()



