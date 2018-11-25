# %%

import json
import random
import socket
import time
import logging
import uuid
from threading import Thread
from blockchain import Blockchain
from bson import ObjectId
from pprint import pprint

# %%

class JSONEncoder(json.JSONEncoder):
  def default(self, o):
    if isinstance(o, ObjectId):
      return str(o)
    return json.JSONEncoder.default(self, o)


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
      if my_latest_block['current_hash'] == data['block']['prev_hash']:
        result = self.blockchain.add_block(block)
        if result:
          self.broadcast_latest_block(data['source'])
      elif block['index'] > my_latest_block['index']:
        msg = JSONEncoder().encode({'type': 'REQUEST_BLOCKCHAIN', 'sender': self.peerID, 
          'source': data['source']})
        self.conn_pair[data['sender']].send(bytes(msg, 'utf-8'))


  def receive_blockchain(self, data):
    block = data['blockchain']
    result = self.blockchain.replaceChain(block)
    if result:
      self.broadcast_latest_block(data['source'])

  def receive_block_hashes(self, data):
     
    seq_num = int(data['seq_no'])
    if not (data['source'] in self.seq_pair):
      self.seq_pair[data['source']] = 0

    # if not receive block hash from this peer before
    if seq_num > self.seq_pair[data['source']]:
      self.seq_pair[data['source']] = seq_num
      if data['dest'] == self.peerID:
        print(data['block_hashes'])

  def receive_data(self, data):
     
    seq_num = int(data['seq_no'])
    if not (data['source'] in self.seq_pair):
      self.seq_pair[data['source']] = 0

    # if not receive block hash from this peer before
    if seq_num > self.seq_pair[data['source']]:
      self.seq_pair[data['source']] = seq_num
      if data['dest'] == self.peerID:
        pprint(data['data_detail'])

  def run(self):
    i = 0
    while True:
      raw_data = self.conn.recv(8092)
      # connection interrupted
      if not raw_data:
        i += 1
        print('end')
        if i > 3:
          return
      
      # print('receive data:', raw_data)
      data = json.loads(raw_data.decode())
      print('receive data:')
      print(json.dumps(data, indent=2))

      # receive connection
      if data['type'] == 'REQUEST_PEERID':
        msg = json.dumps({'type': 'RECEIVE_PEERID', 'peerID': self.peerID})
        self.conn.send(bytes(msg, 'utf-8'))
        self.conn_pair[data['peerID']] = self.conn

      # init connection
      elif data['type'] == 'RECEIVE_PEERID':
        self.conn_pair[data['peerID']] = self.conn
        msg = json.dumps({'type': 'REQUEST_LATEST_BLOCK', 'source': self.peerID })
        self.conn_pair[data['peerID']].send(bytes(msg, 'utf-8'))


      elif data['type'] == 'REQUEST_LATEST_BLOCK':
        if not (data['source'] in self.conn_pair):
          pass
        else:
          self.seq_pair[self.peerID] += 1
          msg = JSONEncoder().encode({'type': 'RECEIVE_LATEST_BLOCK', 'source': self.peerID,
            'sender': self.peerID, 'block': self.blockchain.latest_block, 
            'seq_no': self.seq_pair[self.peerID]})
          self.conn_pair[data['source']].send(bytes(msg, 'utf-8'))

      elif data['type'] == 'RECEIVE_LATEST_BLOCK':
        self.receive_latest_block(data)

      elif data['type'] == 'REQUEST_BLOCKCHAIN':
        if not data['sender'] in self.conn_pair:
          pass
        else:
          msg = JSONEncoder().encode({'type': 'RECEIVE_BLOCKCHAIN', 'source': data['source'],
            'sender': self.peerID, 'blockchain': self.blockchain.block_chain })
          print('[152]',msg)
          self.conn_pair[data['sender']].send(bytes(msg, 'utf-8'))

      elif data['type'] == 'RECEIVE_BLOCKCHAIN':
        self.receive_blockchain(data)
      
      elif data['type'] == 'REQUEST_BLOCK_HASH':
        if data['dest'] == self.peerID:
          self.seq_pair[self.peerID] += 1
          msg = JSONEncoder().encode({'type': 'RECEIVE_BLOCK_HASH', 'source': self.peerID,
            'sender': self.peerID, 'block_hashes': self.blockchain.block_hashes,
            'dest': data['source'], 'seq_no': self.seq_pair[self.peerID] })
          self.conn_pair[data['sender']].send(bytes(msg, 'utf-8'))
        
      elif data['type'] ==  'RECEIVE_BLOCK_HASH':
        self.receive_block_hashes(data)

      elif data['type'] == 'REQUEST_DATA':
        if data['dest'] == self.peerID:
          self.seq_pair[self.peerID] += 1
          if data['data_type'] == 'block':
            block = (next(item for item in self.blockchain.block_chain if item["current_hash"] == data['hash']))
            if block is not None:
              msg = JSONEncoder().encode({'type': 'RECEIVE_DATA', 'source': self.peerID,
                'sender': self.peerID, 'data_detail': block,
                'dest': data['source'], 'seq_no': self.seq_pair[self.peerID],
                'data_type': data['data_type'] })
              self.conn_pair[data['sender']].send(bytes(msg, 'utf-8'))
            else:
              pass
          elif data['data_type'] == 'tx':
            #TODO get transaction by hash
            pass
          else:
            pass
      
      elif data['type'] ==  'RECEIVE_DATA':
        self.receive_data(data)
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
  def __init__(self, _id=""):
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
    if _id != "":
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

    t = HandleMsgThread(soc, self.peerID, self.conn_peerID_pair, self.seq_peerID_pair, self.blockchain)
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
    self.seq_peerID_pair[self.peerID] += 1
    msg = JSONEncoder().encode({'type': 'RECEIVE_LATEST_BLOCK', 'source': self.peerID, 
      'block': self.blockchain.latest_block,
      'seq_no': self.seq_peerID_pair[self.peerID], 'sender': self.peerID })
    for _id, soc in self.conn_peerID_pair.items():
      soc.send(bytes(msg, 'utf-8'))

  def getBlockHashFromDest(self, dest_peer_id):
    self.seq_peerID_pair[self.peerID] += 1
    msg = JSONEncoder().encode({'type': 'REQUEST_BLOCK_HASH', 'source': self.peerID, 
      'seq_no': self.seq_peerID_pair[self.peerID], 'sender': self.peerID, 'dest': dest_peer_id})
    for _id, soc in self.conn_peerID_pair.items():
      soc.send(bytes(msg, 'utf-8'))

  def getDataByHash(self, dest_peer_id, data_type, curr_hash):
    self.seq_peerID_pair[self.peerID] += 1
    msg = JSONEncoder().encode({'type': 'REQUEST_DATA', 'source': self.peerID, 
      'seq_no': self.seq_peerID_pair[self.peerID], 'sender': self.peerID, 'dest': dest_peer_id,
      'data_type': data_type, 'hash': curr_hash})
    for _id, soc in self.conn_peerID_pair.items():
      soc.send(bytes(msg, 'utf-8'))

  def info(self):
    pprint({'peerID': self.peerID, 'peer_ports': self.peer_ports, 
    'server_port': self.serverPort_pool, 'peer_connectTo': self.peer_connectTo,
    'conn_peerID': self.conn_peerID_pair, 'seq_pair': self.seq_peerID_pair })



