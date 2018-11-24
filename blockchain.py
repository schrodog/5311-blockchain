from hashlib import sha256
import time

class Transaction:
  def __init__(self, t):
    self.timestamp = t['timestamp']
    self.source_address = t['source_address']
    self.desc_address = t['desc_address']
    self.prev_hash = t['prev_hash']
    self.current_hash = t['current_hash']
    self.data = t['data']

class Block:
  def __init__(self, b):
    self.timestamp = b['timestamp']
    self.prev_hash = b['prev_hash']
    self.current_hash = b['current_hash']
    self.nonce = b['nonce']
    self.transaction = b['transaction']
    self.merkle_root = b['merkle_root']
    self.index = b['index']
  
  def genesis(self):
    self.timestamp = time.time()
    self.prev_hash = 0
    self.current_hash = '000dc75a315c77a1f9c98fb6247d03dd18ac52632d7dc6a9920261d8109b37cf'
    self.nonce = 0
    self.transaction = []
    self.merkle_root = 0,
    self.index = 0

class Blockchain:    
  def __init__(self):
    #genesis = Block({'timestamp': time.time(), 'prev_hash': 0x0, 
    # 'current_hash': 0x000dc75a315c77a1f9c98fb6247d03dd18ac52632d7dc6a9920261d8109b37cf, 
    # 'nonce': 0, 'transaction':[], 'merkle_root': [], 'index': 0})
    self.blocks = [Block.genesis()]
    self.diffculty = 1

  def get(self):
    return self.blocks

  def latest_block(self):
    return self.blocks[-1]
  
  def is_valid_hash_difficulty(self, hash):
    return hash[:self.difficulty] == '0'*self.diffculty

  def calculate_hash_for_block(self, block):
    # TODO join block's transactions as data
    return self.calculate_hash(block.index, block.prev_hash, block.timestamp, data, block.nonce)

  def calculate_hash(self, previousHash, timestamp, nonce):
    text = previousHash + str(timestamp) + str(nonce)
    s = sha256()
    s.update(text.encode())
    return s.hexdigest()
  
  def mine(self):
    new_block = self.generate_next_block()
    self.add_block(new_block)
  
  def generate_next_block(self):
    next_index = self.latest_block().index + 1
    previous_hash = self.latest_block().current_hash
    timestamp = time.time()
    nonce = 0
    next_hash = self.calculate_hash(previous_hash, timestamp, nonce)
    while not self.is_valid_hash_difficulty(next_hash):
      nonce += 1
      timestamp = time.time()
      next_hash = self.calculate_hash(previous_hash, timestamp, nonce)
    
    # What is correct value for merkle root and transaction?
    next_block = Block({'index': next_index, 'prev_hash': previous_hash, 'timestamp': timestamp, 'transaction': data, 'current_hash': next_hash, 'nonce': nonce, 'merkle_root':[]})
    return next_block
  
  def add_block(self, new_block):
    if self.is_valid_next_block(new_block, self.latest_block()):
      self.blocks.append(new_block)
    else:
      raise Exception('invalid block') 
  
  def is_valid_next_block(self, nextBlock, previousBlock):
    nextBlockHash = self.calculate_hash_for_block(nextBlock)
    if (previousBlock.index + 1) != nextBlock.index:
      return False
    elif previousBlock.current_hash != nextBlock.prev_hash:
      return False
    elif nextBlockHash != nextBlock.current_hash:
      return False
    elif not self.is_valid_hash_difficulty(nextBlockHash):
      return False
    else:
      return True

  def isValidChain(self, chain):
    if chain[0] != Block.genesis():
      return False
    
    tempChain = [chain[0]]
    for i in range(1, len(chain)):
      if (self.isValidNextBlock(chain[i], tempChain[i - 1])) :
        tempChain.append(chain[i])
      else :
        return False
    
    return True

# isChainLonger(self, chain)
# replaceChain(self, newChain)

  

