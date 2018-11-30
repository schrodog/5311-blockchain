# %%
from hashlib import sha256
import time
from database import Database
from pprint import pprint

def genesis():
  return {
    'timestamp': 15432153057109854,
    'prev_hash': '0',
    'current_hash': '00008f991666bb70a0286a49b48d7aa6a3a5cbc521b7bbac72b1b6881bad5b77',
    'nonce': 28435,
    'transaction': [{
      'in': [{'addr': 'coinbase'}]
      'out': [{'addr': '7066edfd21d5b7dd9194', 'value': 100 }], 
      'timestamp': 15432153057109854, 
      'hash': 'b1d7c89f0fcecd0d8403a49ad0921918417228e0bb1ddb6c7b89350137624275'}],
    'merkle_root': 'b1d7c89f0fcecd0d8403a49ad0921918417228e0bb1ddb6c7b89350137624275',
    'index': 0
  }


class Blockchain:    
  def __init__(self, peerID):
    self.db = Database(peerID)
    seq, unspent, bks = self.db.load()
    self.seq_pair = seq
    self.unspent = unspent

    if bks:
      self.blocks = bks
    else:
      self.blocks = [genesis()]
      self.db.insert([genesis()])
    self.difficulty = 4

  @property
  def block_chain(self):
    return list(self.blocks)

  @property
  def latest_block(self):
    return self.blocks[-1]
  
  @property
  def block_hashes(self):
    return [i['current_hash'] for i in self.blocks]

  def check_difficulty(self, hash):
    return hash[:self.difficulty] == '0'*self.difficulty

  def calculate_hash(self, previousHash, timestamp, nonce):
    text = previousHash + str(timestamp) + str(nonce)
    s = sha256()
    s.update(text.encode())
    return s.hexdigest()
  
  def mine(self, tx=''):
    new_block = self.create_next_block(tx)
    self.add_block(new_block)
  
  def create_next_block(self, tx=''):
    next_index = self.latest_block['index'] + 1
    previous_hash = self.latest_block['current_hash']
    timestamp = int(str(time.time()).replace('.',''))
    nonce = 0
    next_hash = self.calculate_hash(previous_hash, timestamp, nonce)
    while not self.check_difficulty(next_hash):
      nonce += 1
      timestamp = int(str(time.time()).replace('.',''))
      next_hash = self.calculate_hash(previous_hash, timestamp, nonce)
    
    # What is correct value for merkle root and transaction?
    next_block = {'index': next_index, 'prev_hash': previous_hash, 'timestamp': timestamp, 'current_hash': next_hash, 'nonce': nonce, 
    'transaction': [{'in': [], 'out': [], 'timestamp': ,'hash': }]}
    # TODO calculate merkle_root
    if tx:
      next_block['transaction'].concat(tx)
    
    next_block['merkle_root'] = 

    return next_block
  
  def add_block(self, new_block):
    if self.check_next_block(new_block, self.latest_block):
      self.blocks.append(new_block)
      self.db.insert([new_block.copy()])
      return True
    else:
      return False
  
  def check_next_block(self, nextBlock, previousBlock):
    nextBlockHash = self.calculate_hash(nextBlock['prev_hash'], nextBlock['timestamp'], nextBlock['nonce'])
    if (previousBlock['index'] + 1) != nextBlock['index']:
      return False
    elif previousBlock['current_hash'] != nextBlock['prev_hash']:
      return False
    elif nextBlockHash != nextBlock['current_hash']:
      return False
    elif not self.check_difficulty(nextBlockHash):
      return False
    else:
      return True

  def check_chain(self, chain):
    if not chain:
      print('104')
      return False
    elif chain[0] != genesis():
      print('107')
      return False

    return all(self.check_next_block(chain[i+1], chain[i]) for i in range(len(chain)-1))

  def replaceChain(self, newChain):
    if self.check_chain(newChain) and (len(newChain) > len(self.blocks)):
      self.blocks = newChain
      print('[113]',newChain)
      self.db.overwrite(newChain.copy())
      return True
    else:
      return False    

  def updateSeq(self, seq):
    self.db.updateSeq(seq)

# # %%
# a090e6e934, 9cf1e32b6f
# bc1 = Blockchain('fd')
# bc2 = Blockchain('ds')

# for i in range(2):
#   bc1.mine()

# for i in range(3):
#   bc2.mine()

# # %%
# [i.block for i in bc1.blocks]

# # %%
# bc1.latest_block.block

# # %%
# [i.block for i in bc2.blocks]


# # %%
# bc2.replaceChain(bc1.blocks)




# class Block:
#   def __init__(self, b):
#     self.timestamp = b['timestamp']
#     self.prev_hash = b['prev_hash']
#     self.current_hash = b['current_hash']
#     self.nonce = b['nonce']
#     self.transaction = b['transaction']
#     self.merkle_root = b['merkle_root']
#     self.index = b['index']

#   def __eq__(self, other):
#     return self.block == other.block  
  
#   @staticmethod
#   def genesis(self):
#     return Block({
#       'timestamp': 15080396630448296,
#       'prev_hash': '0',
#       'current_hash': '00000000315c77a1f9c98fb6247d03dd18ac52632d7dc6a9920261d8109b37cf',
#       'nonce': 0,
#       'transaction': [],
#       'merkle_root': '0',
#       'index': 0
#     })
  
#   @property
#   def block(self):
#     return {
#       'timestamp': self.timestamp,
#       'prev_hash': self.prev_hash,
#       'current_hash': self.current_hash,
#       'nonce': self.nonce,
#       'transaction': self.transaction,
#       'merkle_root': self.merkle_root,
#       'index': self.index
#     }



