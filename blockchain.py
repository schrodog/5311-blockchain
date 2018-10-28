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

class Blockchain:    
  def __init__(self):
    self.blocks = []


  

