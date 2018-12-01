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
2. receive transaction
   - put into pendingTx
   - before mining:
      > find all prev_out for inputs to pay for value
      > give warning if not enough unspent output 
      > clear all pending tx
      > update unspent
      > calc hashes for transactions and calc merkle root
3. add last block
   - check merkle root
   - update unspent
   - clear confirmed pendingTx
4. replace blockchain
   - check all merkle root
   - clear pendingTx
   - reinit unspent    

# format
unspent: [(addr, hash, value), ...]






