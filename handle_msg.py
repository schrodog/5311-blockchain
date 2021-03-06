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
  def __init__(self, conn, peerID, conn_pair, seq_pair, blockchain, pendingTx):
    # to avoid not calling thread.__init__() error
    super(HandleMsgThread, self).__init__()
    self.conn = conn
    self.peerID = peerID
    self.paired_peerID = ''
    self.conn_pair = conn_pair
    self.seq_pair = seq_pair
    self.blockchain = blockchain
    self.pendingTx = pendingTx

  def updateSeq(self, update=True):
    if update:
      self.seq_pair[self.peerID] += 1
    self.blockchain.updateSeq(self.seq_pair)

  # after checking confirm latest block valid, redirect latest block
  def broadcast_latest_block(self, source):
    # self.seq_peerID_pair[self.peerID] += 1
    msg = JSONEncoder().encode({'type': 'RECEIVE_LATEST_BLOCK', 'source': source, 
      'block': self.blockchain.latest_block, 'seq_no': self.seq_pair[source],
      'sender': self.peerID })
    
    # controlled flooding
    # print('broadcast latest block to peers')
    for _id, soc in self.conn_pair.items():
      soc.send(bytes(msg, 'utf-8'))

  def receive_latest_block(self, data):
    block = data['block']
    seq_num = int(data['seq_no'])
    if not (data['source'] in self.seq_pair):
      self.seq_pair[data['source']] = 0
      self.updateSeq(False)

    # if not receive latest block from this peer before
    if seq_num > self.seq_pair[data['source']]:
      self.seq_pair[data['source']] = seq_num
      self.updateSeq(False)

      my_latest_block = self.blockchain.latest_block
      if my_latest_block['current_hash'] == data['block']['prev_hash']:
        result = self.blockchain.add_block(block)
        if result:
          self.blockchain.update_unspent(block)
          self.blockchain.update_tx_data(block['transaction'])
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

  def request_latest_block(self, data):
    msg = json.dumps({'type': 'REQUEST_LATEST_BLOCK', 'source': self.peerID })
    if data['peerID'] in self.conn_pair:
      self.conn_pair[data['peerID']].send(bytes(msg, 'utf-8'))        


  def run(self):
    while True:
      raw_data = self.conn.recv(8092)

      # connection interrupted
      if not raw_data:
        print('end of connection')
        self.conn_pair.pop(self.paired_peerID)
        return
      
      # print('receive data:', raw_data)
      data = json.loads(raw_data.decode())
      # print('receive data:')
      # print(json.dumps(data, indent=2))

      # receive connection
      if data['type'] == 'REQUEST_PEERID':
        msg = json.dumps({'type': 'RECEIVE_PEERID', 'peerID': self.peerID})
        self.conn.send(bytes(msg, 'utf-8'))
        self.conn_pair[data['peerID']] = self.conn
        self.paired_peerID = data['peerID']
        time.sleep(0.1)
        self.request_latest_block(data)

      # init connection
      elif data['type'] == 'RECEIVE_PEERID':
        self.conn_pair[data['peerID']] = self.conn
        self.paired_peerID = data['peerID']
        time.sleep(0.1)
        self.request_latest_block(data)


      elif data['type'] == 'REQUEST_LATEST_BLOCK':
        if not (data['source'] in self.conn_pair):
          pass
        else:
          self.updateSeq()
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
          # print('[152]',msg)
          self.conn_pair[data['sender']].send(bytes(msg, 'utf-8'))

      elif data['type'] == 'RECEIVE_BLOCKCHAIN':
        self.receive_blockchain(data)

      elif data['type'] == 'RECEIVE_TRANSACTION':
        if not data['source'] in self.seq_pair:
          self.seq_pair[data['source']] = 0
        if data['seq_no'] > self.seq_pair[data['source']]:
          self.seq_pair[data['source']] = data['seq_no']
          self.pendingTx.append(data)
          print('Transaction added to pending list')
          for _id, soc in self.conn_pair.items():
            soc.send(raw_data)

      