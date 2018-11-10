# %%

import json
import random
import socket
import time
import logging
import uuid
from threading import Thread

# %%

host_name = socket.gethostname()
localIP = socket.gethostbyname(host_name)

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)

class HandleMsgThread(Thread):
  def __init__(self, conn, peerID, senderPort, pair):
    # to avoid not calling thread.__init__() error
    super(HandleMsgThread, self).__init__()
    self.conn = conn
    self.peerID = peerID
    self.senderPort = senderPort
    self.pair = pair

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
      data = json.loads(data)
      # receive connection
      if data['type'] == 'REQUEST_PEERID':
        self.conn.send(json.dumps({'type': 'RECEIVE_PEERID', 'receiverID': self.peerID, 'receiverPort': data['receiverPort']}))
        self.pair.append({data['peerID']: self.conn})
      # init connection
      elif data['type'] == 'RECEIVE_PEERID':
        conn = self.pair.pop(data['receiverID'])
        self.pair[data['peerID']] = conn

    
class ConnectionThread(Thread):
  def __init__(self, server_socket, conn_pool, peer_addr, peerID, pair):
    super(ConnectionThread, self).__init__()
    self.server_socket = server_socket
    self.conn_pool = conn_pool
    self.peer_addr = peer_addr
    self.peerID = peerID
    self.pair = pair

  def run(self):
    # wait for new connection to server port
    conn, addr = self.server_socket.accept()
    self.conn_pool.append(conn)
    self.peer_addr.append(addr)

    print('new conn', conn, addr)

    # args must be in format (xxx,) to make it iterable
    t2 = HandleMsgThread(conn, self.peerID, addr[1], self.pair)
    t2.start()

    print("connection from", addr)



class P2P_network:
  def __init__(self):
    self.peerID = uuid.uuid4().hex[:10]
    self.clientSocket_pool = []
    self.clientSocket_connecting = []
    self.serverSocket_pool = []
    self.port_pool = []
    self.thread_pool = []
    self.peer_ports = []
    self.peer_connectTo = []
    self.conn_pool = []
    self.port_peerID_pair = {}
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
        t = ConnectionThread(server_socket, self.conn_pool, self.peer_ports,
          port, self.peerID, self.port_peerID_pair)
        t.start()
        return (server_socket, port, t)
      except OSError as e:
        logging.debug("OSError {} {}".format(e, self.port))
  
  def _addServerSocket(self):
    soc, port, t = self._createServerSocket()
    self.serverSocket_pool.append(soc)
    self.port_pool.append(port)
    self.thread_pool.append(t)

  def _addClientSocket(self):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.clientSocket_pool.append(soc)

  def connects(self, port):
    if len(self.clientSocket_pool) == 0:
      for _ in range(5):
        self._addClientSocket()

    soc = self.clientSocket_pool.pop(0)
    try:
      soc.connect((localIP, int(port)))
      self.peer_connectTo.append(port)
      self.clientSocket_connecting.append(soc)
    except OSError as e:
      self.clientSocket_pool.append(soc)
      logging.debug("Cannot connect to port "+str(port)+ e)
      return

    soc.sendall(json.dump({'type': 'REQUEST_PEERID', 'receiverID': self.peerID, 'receiverPort': port}))
    self.port_peerID_pair[str(port)] = conn
    
  def broadcast(self, msg):
    for soc in self.clientSocket_connecting:
      soc.sendall(bytes(msg, 'utf-8'))

  def info(self):
    print({'peerID': self.peerID, 'peer_ports': self.peer_ports, 
    'server_port': self.port_pool, 'peer_connectTo': self.peer_connectTo,
    'client_socketPool': self.clientSocket_pool, 
    'client_connecting': self.clientSocket_connecting })






