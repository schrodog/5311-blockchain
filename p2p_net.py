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
from handle_msg import JSONEncoder, HandleMsgThread

host_name = socket.gethostname()
localIP = socket.gethostbyname(host_name)

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)


class ConnectionThread(Thread):
  def __init__(self, server_socket, peer_addr, peerID, conn_pair, seq_pair, blockchain, serverPort_pool, serverPort, pendingTx):
    super(ConnectionThread, self).__init__()
    self.server_socket = server_socket
    self.peer_addr = peer_addr
    self.peerID = peerID
    self.conn_pair = conn_pair
    self.seq_pair = seq_pair
    self.th = None
    self.blockchain = blockchain
    self.serverPort_pool = serverPort_pool
    self.serverPort = serverPort
    self.pendingTx = pendingTx

  def run(self):
    # wait for new connection to server port
    while True:
      if not self.serverPort in self.serverPort_pool:
        self.serverPort_pool.append(self.serverPort)
  
      conn, addr = self.server_socket.accept()
      # after accept connection
      print('new conn', conn, addr)
      self.serverPort_pool.remove(self.serverPort)

      # args must be in format (xxx,) to make it iterable
      self.th = HandleMsgThread(conn, self.peerID, self.conn_pair, self.seq_pair, self.blockchain, self.pendingTx)
      self.th.setDaemon(True)
      print("connection from", addr, self.th)

      while True:
        try:
          self.th.start()
        except Exception as e:
          print('terminate', str(self.th), 'by', str(e))
          pass
        finally:
          print('terminate', str(self.th))
          self.th.join()
          break

  def stop(self):
    self.th.join()
    return



class P2P_network:
  def __init__(self, _id=""):
    self.peerID = self._getPeerID(_id)    # my peer ID        
    self.clientSocket_pool = []       
    self.serverSocket_pool = []      # available port to receive connection 
    self.serverPort_pool = []       
    self.thread_pool = []
    self.peer_ports = []
    self.conn_peerID_pair = {}    # existing socket-peerID pair
    self.blockchain = Blockchain(self.peerID)
    self.seq_peerID_pair = self.blockchain.seq_pair   # existing seq numbexr-peerID pair
    # self.unspent = self.blockchain.unspent
    self.unspent = self._analyse_unspent()
    self._addServerSocket()
    self._addClientSocket()
    self.pendingTx = []

    print(self.serverPort_pool)
  
  def _getPeerID(self, _id):
    if _id != "":
      return str(_id)
    return uuid.uuid4().hex[:20]

  def _analyse_unspent(self):
    all_tx = [i['transaction'] for i in self.blockchain]
    prev_outs = [(j['addr'], j['prev_out']) for j in [i['in'] \
      for i in all_tx] if j['addr'] != 'coinbase']
    outs = [(j['addr'], i['hash'], j['value']) for j in i['out'] for i in tx]
    return [j for j in outs if all([i != j[:2] for i in prev_outs])]

  def _createServerSocket(self):
    while True:
      try:
        port = random.randint(10000, 50000)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host_name, port))
        server_socket.listen()
        t = ConnectionThread(server_socket, self.peer_ports, self.peerID, self.conn_peerID_pair, self.seq_peerID_pair, self.blockchain, self.serverPort_pool, port, self.pendingTx)
        t.setDaemon(True)
        t.start()
        return (server_socket, port, t)
      except OSError as e:
        logging.debug("OSError {} {}".format(e, self.port))
  
  def _addServerSocket(self):
    for _ in range(5):
      soc, port, t = self._createServerSocket()
      self.serverSocket_pool.append(soc)
      # self.serverPort_pool.append(port)
      self.thread_pool.append(t)

  def _addClientSocket(self):
    for _ in range(5):
      soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.clientSocket_pool.append(soc)

  def connects(self, port):
    if len(self.clientSocket_pool) == 0:
      for _ in range(5):
        self._addClientSocket()

    soc = self.clientSocket_pool.pop(0)
    try:
      soc.connect((localIP, int(port)))
      # self.peer_connectTo.append(port)
      # self.clientSocket_connecting.append(soc)
    except Exception as e:
      self.clientSocket_pool.append(soc)
      logging.debug("Cannot connect to port "+str(port)+':'+ str(e))
      return

    t = HandleMsgThread(soc, self.peerID, self.conn_peerID_pair, self.seq_peerID_pair, self.blockchain)
    t.setDaemon(True)
    t.start()

    msg = json.dumps({'type': 'REQUEST_PEERID', 'peerID': self.peerID})
    soc.sendall(bytes(msg, 'utf-8'))

  def updateSeqNum(self):
    self.seq_peerID_pair[self.peerID] += 1
    self.blockchain.updateSeq(self.seq_peerID_pair)
    
  def broadcast(self, txt):
    self.updateSeqNum()
    msg = json.dumps({'type': 'txt', 'source': self.peerID, 'data': str(txt),
                      'seq_no': self.seq_peerID_pair[self.peerID]})
    for key,soc in self.conn_peerID_pair.items():
      soc.sendall(bytes(msg, 'utf-8'))

  def checkInOut(self, value):
    # search for single output satisfied
    for i in self.unspent: 
      if self.peerID == i[0] and value <= i[2]:
        return i
    # search for multiple source of output
    balance = 0
    ins = [] 
    for i in self.unspent:
      if self.peerID == i[0]:
        balance += i[2]
        ins.append(i)
      if balance >= value:
        return ins
    return False

  def addPendingTransaction(self):
    result = []
    for tx in self.pendingTx:
      total_out = tx['value']
      ins = self.checkInOut(total_out)
      if ins:
        total_in = sum([i[2] for i in ins])
        d = {'in': [{'addr': tx['source_addr'], 'value': i[2], 'prev_out': i[1]} for i in ins],
          'out': [{'addr': tx['dest_addr'], 'value': total_out}]}
        if total_in > total_out:
          d['out'].append({'addr': tx['source_addr'], 'value': total_in-total_out})
        result.append(d)
    return result

  # assume only owner of coin can be sender of transaction
  def broadcastTransaction(self, dest_addr, value):
    if self.checkInOut(value):
      self.updateSeqNum()
      msg = json.dumps({'type': 'RECEIVE_TRANSACTION', 'source': self.peerID, 'value': value,
                        'seq_no': self.seq_peerID_pair[self.peerID], 'source_addr': self.peerID,
                        'dest_addr': dest_addr})
      for key,soc in self.conn_peerID_pair.items():
        soc.sendall(bytes(msg, 'utf-8'))
    else:
      print('You do not have enough value to do transaction')



  def mine(self):
    tx = self.addPendingTransaction()
    self.blockchain.mine(tx)
    self.updateSeqNum()
    msg = JSONEncoder().encode({'type': 'RECEIVE_LATEST_BLOCK', 'source': self.peerID, 
      'block': self.blockchain.latest_block,
      'seq_no': self.seq_peerID_pair[self.peerID], 'sender': self.peerID })
    for _id, soc in self.conn_peerID_pair.items():
      soc.send(bytes(msg, 'utf-8'))

  # def getBlockHashFromDest(self, dest_peer_id):
  #   self.updateSeqNum()
  #   msg = JSONEncoder().encode({'type': 'REQUEST_BLOCK_HASH', 'source': self.peerID, 
  #     'seq_no': self.seq_peerID_pair[self.peerID], 'sender': self.peerID, 'dest': dest_peer_id})
  #   for _id, soc in self.conn_peerID_pair.items():
  #     soc.send(bytes(msg, 'utf-8'))

  # def getDataByHash(self, data_type, curr_hash):
  #   self.updateSeqNum()
  #   msg = JSONEncoder().encode({'type': 'REQUEST_DATA', 'source': self.peerID, 
  #     'seq_no': self.seq_peerID_pair[self.peerID], 'sender': self.peerID, 'dest': dest_peer_id,
  #     'data_type': data_type, 'hash': curr_hash})
  #   for _id, soc in self.conn_peerID_pair.items():
  #     soc.send(bytes(msg, 'utf-8'))

  def info(self):
    pprint({'peerID': self.peerID,       
    'server_port': self.serverPort_pool, 
    'conn_peerID': self.conn_peerID_pair,
    'seq_pair': self.seq_peerID_pair     
    })



