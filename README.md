# TODO
## P2P mechanism
how to convey message? how to discover other clients?

## Solution
**Sequence** number controlled flooding

## get peerID
each peer has unique peerID

Sender
-- REQUEST, PEERID  -->
Receiver
<-- RECEIVE, PEERID

# Problems
1. how to dynamically add server socket?
2. add transaction functions
3. check block by hash
4. auto mine
5. construct merkle tree
6. check merkle root
7. update seq number

# Transaction
1. sender want to init transaction
   - not broadcast tx, mine block and put insde
   - broadcast tx, not mine block
      > p2p_net/broadcastTransaction
2. receive transaction
   - put into pendingTx [handle_msg]
3. mining:
- find all prev_out for inputs to pay for value
- give warning if not enough unspent output 
- clear all pending tx
- update unspent
- calc hashes for transactions and calc merkle root

p2p_net/mine -> blockchain/addPendingTransaction <-> checkInOut
blockchain/mine -> create_new_blcok -> update_unspent
-> blockchain/add_block

4. add last block
   - check merkle root
   - update unspent
   - clear confirmed pendingTx
5. replace blockchain
   - check all merkle root
   - clear pendingTx
   - reinit unspent    
handle_msg/receive_blockchain -> blockchain/replaceChain -> check_chain
-> check_next_block -> check_transaction <-> update_tx_data

# format
unspent: [(addr, hash, value), ...]
pendingTx: [{dest_addr, seq_no, source, 
            source_addr, timestamp, value, type='RECEIVE_TRANSACTION}, ...]

blockchain: 
[{'current_hash': '00008f991666bb70a0286a49b48d7aa6a3a5cbc521b7bbac72b1b6881bad5b77',
  'index': 0,
  'merkle_root': 'b1d7c89f0fcecd0d8403a49ad0921918417228e0bb1ddb6c7b89350137624275',
  'nonce': 28435,
  'prev_hash': '0',
  'timestamp': 15432153057109854,
  'transaction': [{'hash': 'b1d7c89f0fcecd0d8403a49ad0921918417228e0bb1ddb6c7b89350137624275',
                   'in': [{'addr': 'coinbase'}],
                   'out': [{'addr': '7066edfd21d5b7dd9194', 'value': 100}],
                   'timestamp': 15432153057109854}]}, ...]



# Dependency library
## Python3
bjson
pymongo

## Others
MongoDB



# Demo
1. start 1 node (A)
2. mine without tx
3. start another node (B)
4. mine
5. connect A -> B
   - see data sync
6. A mine with 1 tx (to another)
   - see data sync
7. B mine with 1 tx
8. start node C
9. connect to B
   - see data sync
10. C broadcast tx
11. A mine 
12. A bye, login again with A's peer ID





