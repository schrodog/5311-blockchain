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
  def __init__(self, conn, peerID, conn_pair, seq_pair):
    # to avoid not calling thread.__init__() error
    super(HandleMsgThread, self).__init__()
    self.conn = conn
    self.peerID = peerID
    self.conn_pair = conn_pair
    self.seq_pair = seq_pair

  def run(self):
    i = 0
    while True:
      raw_data = self.conn.recv(1024)
      
      if not raw_data:
        i += 1
        if i > 3:
          break
          return
      
      data = json.loads(raw_data.decode())
      print('receive data:', data)
      # receive connection
      if data['type'] == 'REQUEST_PEERID':
        msg = json.dumps({'type': 'RECEIVE_PEERID', 'peerID': self.peerID})
        self.conn.send(bytes(msg, 'utf-8'))
        self.conn_pair[data['peerID']] = self.conn

      # init connection
      elif data['type'] == 'RECEIVE_PEERID':
        self.conn_pair[data['peerID']] = self.conn

      else:
        num = int(data['seq_no'])
        if not (data['source'] in self.seq_pair):
          self.seq_pair[data['source']] = 0

        # controlled flooding
        if num > self.seq_pair[data['source']]:
          print('broadcast to peers')
          self.seq_pair[data['source']] = num
          for _id, soc in self.conn_pair.items():
            soc.sendall(raw_data)


    
class ConnectionThread(Thread):
  def __init__(self, server_socket, peer_addr, peerID, conn_pair, seq_pair):
    super(ConnectionThread, self).__init__()
    self.server_socket = server_socket
    self.peer_addr = peer_addr
    self.peerID = peerID
    self.conn_pair = conn_pair
    self.seq_pair = seq_pair

  def run(self):
    # wait for new connection to server port
    conn, addr = self.server_socket.accept()
    self.peer_addr.append(addr)
    print('new conn', conn, addr)

    # args must be in format (xxx,) to make it iterable
    t2 = HandleMsgThread(conn, self.peerID, self.conn_pair, self.seq_pair)
    t2.start()

    print("connection from", addr)



class P2P_network:
  def __init__(self):
    self.peerID = uuid.uuid4().hex[:10]
    self.clientSocket_pool = []
    self.clientSocket_connecting = []
    self.serverSocket_pool = []
    self.serverPort_pool = []
    self.thread_pool = []
    self.peer_ports = []
    self.peer_connectTo = []
    self.conn_peerID_pair = {}
    self.seq_peerID_pair = {self.peerID: 0}
    for _ in range(5):
      self._addServerSocket()
      self._addClientSocket()

    print(self.serverPort_pool)

  def _createServerSocket(self):
    while True:
      try:
        port = random.randint(10000, 50000)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host_name, port))
        server_socket.listen()
        t = ConnectionThread(server_socket, self.peer_ports, self.peerID, self.conn_peerID_pair, self.seq_peerID_pair)
        t.start()
        return (server_socket, port, t)
      except OSError as e:
        logging.debug("OSError {} {}".format(e, self.port))
  
  def _addServerSocket(self):
    soc, port, t = self._createServerSocket()
    self.serverSocket_pool.append(soc)
    self.serverPort_pool.append(port)
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

    t = HandleMsgThread(soc, self.peerID, self.conn_peerID_pair, self.seq_peerID_pair)
    t.start()

    msg = json.dumps({'type': 'REQUEST_PEERID', 'peerID': self.peerID})
    soc.sendall(bytes(msg, 'utf-8'))
    
  def broadcast(self, txt):
    self.seq_peerID_pair[self.peerID] += 1
    msg = json.dumps({'type': 'txt', 'source': self.peerID, 'data': str(txt),
                      'seq_no': self.seq_peerID_pair[self.peerID]})

    for key,soc in self.conn_peerID_pair.items():
      soc.sendall(bytes(msg, 'utf-8'))

  def info(self):
    print({'peerID': self.peerID, 'peer_ports': self.peer_ports, 
    'server_port': self.serverPort_pool, 'peer_connectTo': self.peer_connectTo,
    'conn_peerID': self.conn_peerID_pair, 'seq_pair': self.seq_peerID_pair })






