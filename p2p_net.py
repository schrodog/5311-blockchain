# %%

import random
import socket
import time
import logging
from threading import Thread

# %%

host_name = socket.gethostname()
localIP = socket.gethostbyname(host_name)

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)

class HandleMsgThread(Thread):
  def __init__(self, conn):
    # to avoid not calling thread.__init__() error
    super(HandleMsgThread, self).__init__()
    self.conn = conn

  def run(self):
    i = 0
    while True:
      data = self.conn.recv(1024).decode()
      if not data:
        i += 1
        if i > 3:
          break
          return
      print('receive data:', data)


    
class ConnectionThread(Thread):
  def __init__(self, server_socket, conn_pool, peer_addr):
    super(ConnectionThread, self).__init__()
    self.server_socket = server_socket
    self.conn = None
    self.addr = None
    self.conn_pool = conn_pool
    self.peer_addr = peer_addr

  def run(self):
    # wait for new connection to server port
    conn, addr = self.server_socket.accept()
    self.conn = conn
    self.addr = addr
    self.conn_pool.append(conn)
    self.peer_addr.append(addr)

    print('new conn', self.conn, self.addr)
    # args must be in format (xxx,) to make it iterable
    t2 = HandleMsgThread(conn)
    t2.start()

    print("connection from", addr)



class P2P_network:
  def __init__(self):
    self.clientSocket_pool = []
    self.serverSocket_pool = []
    self.port_pool = []
    self.thread_pool = []
    self.peer_ports = []
    self.peer_connectTo = []
    self.conn_pool = []
    for _ in range(5):
      self._addServerSocket()
      self._addClientSocket()
    print(self.port_pool)

  def _createServerSocket(self):
    while True:
      try:
        port = random.randint(10000, 50000)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host_name, port))
        server_socket.listen()
        t = ConnectionThread(server_socket, self.conn_pool, self.peer_ports)
        t.start()
        return (server_socket, port, t)
      except OSError as e:
        logging.debug("OSError {} {}".format(e, self.port))
  
  def _createClientSocket(self):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.clientSocket_pool(soc)
  
  def _addServerSocket(self):
    soc, port, t = self._createServerSocket()
    self.serverSocket_pool.append(soc)
    self.port_pool.append(port)
    self.thread_pool.append(t)

  def _addClientSocket(self):
    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  def connects(self, port):
    try:
      self.client_socket.connect((localIP, int(port)))
      self.peer_connectTo.append(port)
    except OSError as e:
      logging.debug("Cannot connect to port "+str(port)+ e)

  def broadcast(self, msg):
    self.client_socket.sendall(bytes(msg, 'utf-8'))

  def info(self):
    print('peers', self.peer_ports, 'server_port', self.port_pool)






