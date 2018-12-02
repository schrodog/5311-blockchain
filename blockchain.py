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
    self.peerID = peerID
    self.unspent = unspent
    self.unspent += self._analyse_unspent()
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
        # print('[56]', i)
        for j in i:
          strs += str(i[j])
    strs += str(tx['timestamp'])
    return _calc_hash(strs)
  
  def mine(self, tx=''):
    new_block = self.create_next_block(tx)
    # print('blockchain.py[62]', new_block)
    self.add_block(new_block)
  
  def create_next_block(self, tx=''):
    next_index = self.latest_block['index'] + 1
    previous_hash = self.latest_block['current_hash']
    timestamp = _getTime()
    nonce = 0
    next_hash = _calc_hash(previous_hash + str(timestamp) + str(nonce))
    while not self.check_difficulty(next_hash):
      nonce += 1
      timestamp = _getTime()
      next_hash = _calc_hash(previous_hash + str(timestamp) + str(nonce))
    
    next_block = {
      'index': next_index, 'prev_hash': previous_hash, 'timestamp': timestamp, 
      'current_hash': next_hash, 'nonce': nonce, 
      'transaction': [{'in': [{'addr': 'coinbase'}], 
                       'out': [{'addr': self.peerID, 'value': 100}],
      'timestamp': timestamp, 'hash': '' }] }
    # if other tx besides coinbase, then add to transaction
    if tx:
      next_block['transaction'] += tx

    # concat all values in in,out,timestamp, calc hash
    res = []
    for tx2 in next_block['transaction']:
      # print('[91]', tx2)
      tx2['hash'] = self._calc_hash_by_tx(tx2)
      res.append(tx2['hash'])
    next_block['merkle_root'] = _calc_merkle_root(res)
    # add outs to unspent
    self.update_unspent(next_block)

    return next_block
    
  def update_unspent(self, next_block):
    for i in next_block['transaction']:
      for j in i['out']:
        self.unspent.append((j['addr'], i['hash'], j['value']))
  
  def add_block(self, new_block):
    if self.check_next_block(new_block, self.latest_block):
      self.blocks.append(new_block)
      # print('blockchain.py[99]', self.blocks)
      self.db.insert([new_block.copy()])
      return True
    else:
      return False
  
  def check_next_block(self, nextBlock, previousBlock, replaceBC=False):
    nextBlockHash = _calc_hash(nextBlock['prev_hash'] + str(nextBlock['timestamp']) + str( nextBlock['nonce']) )
    print('blockchain.py[108]', nextBlockHash)
    if (previousBlock['index'] + 1) != nextBlock['index']:
      # print('[110]')
      return False
    elif previousBlock['current_hash'] != nextBlock['prev_hash']:
      # print('[113]')
      return False
    elif nextBlockHash != nextBlock['current_hash']:
      # print('[116]')
      return False
    elif not self.check_difficulty(nextBlockHash):
      # print('[119]')
      return False
    elif not self.check_transaction(nextBlock, replaceBC):
      # print('[115] failed tx')
      return False
    else:
      # print('[125]')
      return True

  
  def _analyse_unspent(self):
    all_tx = [i['transaction'] for i in self.block_chain]
    # print('bc[133]', all_tx)
    res = []
    for t in all_tx:
      # print('bc[136]', t)
      for i in t:
        prev_outs = [(j['addr'], j['prev_out']) for j in i['in'] if j['addr'] != 'coinbase']
        outs = [(j['addr'], i['hash'], j['value']) for j in i['out']]
        res += [j for j in outs if all([i != j[:2] for i in prev_outs])]
        # print('bc[141]', prev_outs, outs, res)
    # print('bc[142]', res)
    return res

  def check_transaction(self, nextBlock, replaceBC):
    # check individual tx
    transaction = nextBlock['transaction']
    if not all([self._calc_hash_by_tx(tx) == tx['hash'] for tx in transaction]):
      return False
    # check merkle root
    print('[146]', transaction)
    if _calc_merkle_root([i['hash'] for i in transaction]) != nextBlock['merkle_root']:
      return False
    if not replaceBC:
      self.update_tx_data(transaction)

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
      # update transaction in bulk
      self.pendingTx.clear()
      res = self._analyse_unspent()
      self.unspent.clear()
      self.unspent += res
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
          # check if any 'pendingTx' already exist in 'out'
          for j in self.pendingTx:
            print('bc[199]', i,j)
            if (i['addr'], i['value']) == (j['dest_addr'], j['value']) and tx['in'][0]['addr'] == j['source_addr']:
              self.pendingTx.remove(j)
              break
      for i in tx['in']:
        if 'prev_out' in i:
          for j in self.unspent:
            if (i['addr'], i['prev_out']) == j[:2]:
              # print('bc[206]', self.unspent)
              self.unspent.remove(j)
              # print('bc[208]', self.unspent)
              break
  
  def checkInOut(self, value, source_addr, dest_addr, query=False):
    # search for single output satisfied
    value = int(value)
    for i in self.unspent: 
      # print('bc[214]', i)
      if source_addr == i[0] and value <= i[2]:
        # print('bc[215]', self.unspent)
        if not query:
          self.unspent.remove(i)
        # print('bc[217]', self.unspent)
        return [i]
    # search for multiple source of output, del used unspent
    balance = 0
    ins = []
    for i in self.unspent:
      # print('bc[223]', i)
      if source_addr == i[0]:
        balance += int(i[2])
        ins.append(i)
      if balance >= value:
        if not query:
          for j in ins:
            self.unspent.remove(j)
        return ins
    print('Transaction from '+source_addr+' to '+dest_addr+' for '+str(value)+' is invalid.')
    return False

  # find corresponding unspent outs to carry out transaction
  def addPendingTransaction(self):
    result = []
    while self.pendingTx:
      tx = self.pendingTx.pop(0)
      total_out = int(tx['value'])
      ins = self.checkInOut(total_out, tx['source_addr'], tx['dest_addr'])
      # print('[234]', ins)
      if ins:
        total_in = sum([i[2] for i in ins])
        d = {'in': [{'addr': tx['source_addr'], 'value': i[2], 'prev_out': i[1]} for i in ins],
          'out': [{'addr': tx['dest_addr'], 'value': total_out}], 'timestamp': tx['timestamp']}
        if total_in > total_out:
          d['out'].append({'addr': tx['source_addr'], 'value': total_in-total_out})
        result.append(d)
    return result



