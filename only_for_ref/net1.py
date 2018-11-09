# import socket 

# host_name = socket.gethostname()
# localIP = socket.gethostbyname(host_name)

# s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# s1.bind((localIP, 7001))
# s1.listen()
# s2.bind((localIP, 7001))
# s2.listen()

import threading

class ABC():
  def __init__(self):
    self.threads = []
    self.results = []

  def adder(self, x, res, i):
    res[i] += x*i

  def creator(self, a, threads, results):
    print(a,threads, results)


    for i in range(a):
      results.append(0)
      t = threading.Thread(target=self.adder, args=(a, results, i))
      threads.append(t)
      t.start()
      # print(threads)
    for t in threads:
      t.join()
  
  def run(self):
    mainThread = threading.Thread(target=self.creator, args=(5, self.threads, self.results))
    mainThread.start()
    mainThread.join()
    for i in range(len(self.results)):
      print(self.results[i])
      print(self.threads[i])


abc = ABC()
abc.run()
