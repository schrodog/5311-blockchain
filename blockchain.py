from utility import _getTime, _calc_hash, _calc_merkle_root
from database import Database
from pprint import pprint

def genesis():
  return {
    'timestamp': 15432153057109854,
    'prev_hash': '0',
    'current_hash': '00008f991666bb70a0286a49b48d7aa6a3a5cbc521b7bbac72b1b6881bad5b77',
    'nonce': 28435,
    'transaction': [{
      'in': [{'addr': 'coinbase'}],  # addr, prev_out, value
      'out': [{'addr': '7066edfd21d5b7dd9194', 'value': 100 }], 
      'timestamp': 15432153057109854, 
      'hash': 'b1d7c89f0fcecd0d8403a49ad0921918417228e0bb1ddb6c7b89350137624275'}],
    'merkle_root': 'b1d7c89f0fcecd0d8403a49ad0921918417228e0bb1ddb6c7b89350137624275',
    'index': 0
  }


class Blockchain:    
  def __init__(self, peerID, unspent, pendingTx):
    self.db = Database(peerID)
    seq, u, bks = self.db.load()
    self.seq_pair = seq
    if bks:
      self.blocks = bks
    else:
      self.blocks = [genesis()]
      self.db.insert([genesis()])
    self.difficulty = 4
    self.unspent = self._analyse_unspent()
    self.pendingTx = pendingTx

  @property
  def block_chain(self):
    return [i for i in self.blocks]

  @property
  def latest_block(self):
    return self.blocks[-1]
  
  @property
  def block_hashes(self):
    return [i['current_hash'] for i in self.blocks]

  def check_difficulty(self, h):
    return h[:self.difficulty] == '0'*self.difficulty

  def _calc_hash_by_tx(self, tx):
    strs = ""
    for s in ['in', 'out']:
      for i in tx[s]:
        for j in i:
          strs += str(i[j])
    strs += str(tx['timestamp'])
    return _calc_hash(strs)
  
  def mine(self, tx=''):
    new_block = self.create_next_block(tx)
    self.add_block(new_block)
  
  def create_next_block(self, tx=''):
    next_index = self.latest_block['index'] + 1
    previous_hash = self.latest_block['current_hash']
    timestamp = _getTime()
    nonce = 0
    next_hash = _calc_hash(previous_hash + str(timestamp) + str(nonce))
    while not self.check_difficulty(next_hash):
      nonce += 1
      next_hash = _calc_hash(previous_hash + str(_getTime()) + str(nonce))
    
    next_block = {
      'index': next_index, 'prev_hash': previous_hash, 'timestamp': timestamp, 
      'current_hash': next_hash, 'nonce': nonce, 
      'transaction': [{'in': [{'addr': 'coinbase'}], 
                       'out': [{'addr': self.peerID, 'value': 100}],
      'timestamp': '','hash': '' }] }

    if tx:
      ins = self.checkInOut(tx['value'])
      next_block['transaction'].append({
        'in': [{'addr':tx['source_addr'],'prev_out':i['hash'], 'value':i['value']} for i in ins], 
        'out': [{'addr': tx['dest_addr'], 'value': tx['value']}] })

    # concat all values in in,out,timestamp, calc hash
    res = []
    for tx2 in next_block['transaction']:
      tx2['hash'] = self._calc_hash_by_tx(tx2)
      res.append(tx2['hash'])
    next_block['merkle_root'] = _calc_merkle_root(res)

    return next_block
  
  def add_block(self, new_block):
    if self.check_next_block(new_block, self.latest_block):
      self.blocks.append(new_block)
      self.db.insert([new_block.copy()])
      return True
    else:
      return False
  
  def check_next_block(self, nextBlock, previousBlock, replaceBC=False):
    nextBlockHash = _calc_hash(nextBlock['prev_hash'] + str(nextBlock['timestamp']) + str( nextBlock['nonce']) )
    if (previousBlock['index'] + 1) != nextBlock['index']:
      return False
    elif previousBlock['current_hash'] != nextBlock['prev_hash']:
      return False
    elif nextBlockHash != nextBlock['current_hash']:
      return False
    elif not self.check_difficulty(nextBlockHash):
      return False
    elif not self.check_transaction(nextBlock['transaction'], replaceBC):
      return False
    else:
      return True

  
  def _analyse_unspent(self):
    all_tx = [i['transaction'] for i in self.block_chain]
    res = []
    for t in all_tx:
      for i in t:
        prev_outs = [(j['addr'], j['prev_out']) for j in i['in'] if j['addr'] != 'coinbase']
        outs = [(j['addr'], i['hash'], j['value']) for j in i['out']]
        res += [j for j in outs if all([i != j[:2] for i in prev_outs])]
    return res

  def check_transaction(self, transaction, replaceBC):
    # check individual tx
    if not all([self._calc_hash_by_tx(tx) == tx['hash'] for tx in transaction]):
      return False
    # check merkle root
    if _calc_merkle_root([i['hash'] for i in transaction]) != transaction['merkle_root']:
      return False
    if not replaceBC:
      self.update_tx_data(transaction)
    else:
      self.pendingTx.clear()
      res = self._analyse_unspent()
      self.unspent.clear()
      self.unspent += res

    return True

  def check_chain(self, chain, replaceBC=False):
    if not chain:
      # print('104')
      return False
    elif chain[0] != genesis():
      # print('107')
      return False

    return all(self.check_next_block(chain[i+1], chain[i], replaceBC) \
      for i in range(len(chain)-1))

  def replaceChain(self, newChain):
    if self.check_chain(newChain, True) and (len(newChain) > len(self.blocks)):
      self.blocks = newChain
      # print('[113]',newChain)
      self.db.overwrite(newChain.copy())
      return True
    else:
      return False    

  def updateSeq(self, seq):
    self.db.updateSeq(seq)

  # remove confirmed tx in pendingTx & unspent update
  def update_tx_data(self, transaction):
    for tx in transaction:
      if self.pendingTx:
        for i in tx['out']:
          for j in self.pendingTx:
            if i[:2] == (j['dest_addr'], j['value']) and tx['in'][0]['addr'] == j['source_addr']:
              self.pendingTx.remove(j)
              break
      for i in tx['in']:
        if 'prev_out' in i:
          for j in self.unspent:
            if (i['addr'], i['prev_out']) == j[:2]:
              self.unspent.remove(j)
              break
  
  def checkInOut(self, value):
    # search for single output satisfied
    for i in self.unspent: 
      if self.peerID == i[0] and value <= i[2]:
        return i
    # search for multiple source of output, del used unspent
    balance = 0
    ins = []
    for i in self.unspent:
      if self.peerID == i[0]:
        balance += i[2]
        ins.append(i)
        self.unspent.remove(i)
      if balance >= value:
        return ins
    return False

  def addPendingTransaction(self):
    result = []
    while self.pendingTx:
      tx = self.pendingTx.pop(0)
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



