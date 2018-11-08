# %%

import random
import socket
import time
import logging

# %%

host_name = socket.gethostname()
localIP = socket.gethostbyname(host_name)

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)

class P2P_network:
  def __init__(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
      try:
        self.port = random.randint(10000, 50000)
        self.socket.bind((host_name, self.port))
        self.socket.listen()
        break
      except OSError as e:
        logging.debug("OSError {} {}".format(e, self.port))
    # self.receive_msg()

  def connect(self, port):
    try:
      self.socket.connect(localIP, port)
    except OSError as e:
      logging.debug("Cannot connect to port "+str(port))

  def receive_msg(self):
    while True:
      print("my port", self.port)
      conn, addr = self.socket.accept()
      print("connection from", addr)

  @staticmethod
  def welcome():
    print('well')






