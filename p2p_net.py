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
  def __init__(self, server_socket, peer_addr, peerID, conn_pair, seq_pair, blockchain, serverPort_pool, serverPort):
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
      self.th = HandleMsgThread(conn, self.peerID, self.conn_pair, self.seq_pair, self.blockchain)
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
    self.seq_peerID_pair = {self.peerID: 0}   # existing seq number-peerID pair
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
        t = ConnectionThread(server_socket, self.peer_ports, self.peerID, self.conn_peerID_pair, self.seq_peerID_pair, self.blockchain, self.serverPort_pool, port)
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
    pprint({'peerID': self.peerID,       
    'server_port': self.serverPort_pool, 
    'conn_peerID': self.conn_peerID_pair,
    'seq_pair': self.seq_peerID_pair     
    })



