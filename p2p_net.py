# %%

import json
import random
import socket
import time
import logging
import uuid
from threading import Thread
from blockchain import Blockchain

# %%

host_name = socket.gethostname()
localIP = socket.gethostbyname(host_name)

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)

class HandleMsgThread(Thread):
  def __init__(self, conn, peerID, conn_pair, seq_pair, blockchain):
    # to avoid not calling thread.__init__() error
    super(HandleMsgThread, self).__init__()
    self.conn = conn
    self.peerID = peerID
    self.conn_pair = conn_pair
    self.seq_pair = seq_pair
    self.blockchain = blockchain

  # after checking confirm latest block valid, redirect latest block
  def broadcast_latest_block(self, source):
    # self.seq_peerID_pair[self.peerID] += 1
    msg = json.dumps({'type': 'RECEIVE_LATEST_BLOCK', 'source': source, 
      'block': self.blockchain.latest_block, 'seq_no': self.seq_pair[source],
      'sender': self.peerID })
    
    # controlled flooding
    print('broadcast latest block to peers')
    for _id, soc in self.conn_pair.items():
      soc.send(bytes(msg, 'utf-8'))


  def receive_latest_block(self, data):
    block = data['block']
    seq_num = int(data['seq_no'])
    if not (data['source'] in self.seq_pair):
      self.seq_pair[data['source']] = 0

    # if not receive latest block from this peer before
    if seq_num > self.seq_pair[data['source']]:
      self.seq_pair[data['source']] = seq_num

      my_latest_block = self.blockchain.latest_block
      if my_latest_block.hash == data.prev_hash:
        result = self.blockchain.add_block(block)
        if result:
          self.broadcast_latest_block(data['source'])
      elif block.index > my_latest_block.index:
        msg = json.dumps({'type': 'REQUEST_BLOCKCHAIN', 'sender': self.peerID, 
          'source': data['source']})
        self.conn_pair[data['sender']].send(bytes(msg, 'utf-8'))


  def receive_blockchain(self, data):
    block = data['blockchain']
    result = self.blockchain.replaceChain(block)
    if result:
      self.broadcast_latest_block(data['source'])

  def run(self):
    i = 0
    while True:
      raw_data = self.conn.recv(1024)
      # connection interrupted
      if not raw_data:
        i += 1
        print('end')
        if i > 3:
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

      elif data['type'] == 'REQUEST_LATEST_BLOCK':
        if not (data['source'] in self.conn_pair):
          pass
        else:
          self.seq_peerID_pair[self.peerID] += 1
          msg = json.dumps({'type': 'RECEIVE_LATEST_BLOCK', 'source': self.peerID, 
            'block': self.blockchain.latest_block, 'seq_no': self.seq_peerID_pair[self.peerID]})
          self.conn_pair[data['source']].send(bytes(msg, 'utf-8'))

      elif data['type'] == 'RECEIVE_LATEST_BLOCK':
        self.receive_latest_block(data)

      elif data['type'] == 'REQUEST_BLOCKCHAIN':
        if not data['sender'] in self.conn_pair:
          pass
        else:
          msg = json.dumps({'type': 'RECEIVE_BLOCKCHAIN', 'source': data['source'],
            'sender': self.peerID, 'blockchain': self.blockchain.block_chain })
          self.conn_pair[data['sender']].send(bytes(msg, 'utf-8'))

      elif data['type'] == 'RECEIVE_BLOCKCHAIN':
        self.receive_blockchain(data)
          
      # else:
      #   num = int(data['seq_no'])
      #   if not (data['source'] in self.seq_pair):
      #     self.seq_pair[data['source']] = 0

      #   # controlled flooding
      #   if num > self.seq_pair[data['source']]:
      #     print('broadcast to peers')
      #     self.seq_pair[data['source']] = num
      #     for _id, soc in self.conn_pair.items():
      #       soc.sendall(raw_data)


    
class ConnectionThread(Thread):
  def __init__(self, server_socket, peer_addr, peerID, conn_pair, seq_pair, blockchain):
    super(ConnectionThread, self).__init__()
    self.server_socket = server_socket
    self.peer_addr = peer_addr
    self.peerID = peerID
    self.conn_pair = conn_pair
    self.seq_pair = seq_pair
    self.thread_pool = []
    self.blockchain = blockchain

  def run(self):
    # wait for new connection to server port
    conn, addr = self.server_socket.accept()
    self.peer_addr.append(addr)
    print('new conn', conn, addr)

    # args must be in format (xxx,) to make it iterable
    t2 = HandleMsgThread(conn, self.peerID, self.conn_pair, self.seq_pair, self.blockchain)
    t2.setDaemon(True)
    t2.start()
    self.thread_pool.append(t2)

    print("connection from", addr)

  def stop(self):
    for t in self.thread_pool:
      print('1')
      t.join()
    return



class P2P_network:
  def __init__(self, _id=-1):
    self.peerID = self._getPeerID(_id)
    self.clientSocket_pool = []
    self.clientSocket_connecting = []
    self.serverSocket_pool = []
    self.serverPort_pool = []
    self.thread_pool = []
    self.peer_ports = []
    self.peer_connectTo = []
    self.conn_peerID_pair = {}
    self.seq_peerID_pair = {self.peerID: 0}
    self.blockchain = Blockchain(self.peerID)
    for _ in range(5):
      self._addServerSocket()
      self._addClientSocket()

    print(self.serverPort_pool)
  
  def _getPeerID(self, _id):
    if _id != -1:
      return str(_id)
    return uuid.uuid4().hex[:10]

  def _createServerSocket(self):
    while True:
      try:
        port = random.randint(10000, 50000)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host_name, port))
        server_socket.listen()
        t = ConnectionThread(server_socket, self.peer_ports, self.peerID, self.conn_peerID_pair, self.seq_peerID_pair, self.blockchain)
        t.setDaemon(True)
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
    t.setDaemon(True)
    t.start()

    msg = json.dumps({'type': 'REQUEST_PEERID', 'peerID': self.peerID})
    soc.sendall(bytes(msg, 'utf-8'))
    
  def broadcast(self, txt):
    self.seq_peerID_pair[self.peerID] += 1
    msg = json.dumps({'type': 'txt', 'source': self.peerID, 'data': str(txt),
                      'seq_no': self.seq_peerID_pair[self.peerID]})

    for key,soc in self.conn_peerID_pair.items():
      soc.sendall(bytes(msg, 'utf-8'))

  def mine(self):
    self.blockchain.mine()

  def info(self):
    print({'peerID': self.peerID, 'peer_ports': self.peer_ports, 
    'server_port': self.serverPort_pool, 'peer_connectTo': self.peer_connectTo,
    'conn_peerID': self.conn_peerID_pair, 'seq_pair': self.seq_peerID_pair })

  # def receive_latest_block(self, receive_latest_block):
  #   latest_block = self.db.blockchain[-1]
  #   if latest_block.hash == received_latest_block.prev_hash)[-1]:
  #     self.db.insert(latest_block)
  #   elif receive_latest_block.index > latest_block.index:
  #     msg = json.dumps({'type': 'REQUEST_LATEST_BLOCK'})
  #     self.broadcast(msg)
  #   else:
  #     pass




