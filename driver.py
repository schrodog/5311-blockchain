import time
from blockchain import Blockchain, Block, Transaction

  # Set things up
chain = Blockchain()
t1 = Transaction({'timestamp': time.time(), 'source_address':'home', 'desc_address':'cityline', 'prev_hash':0xffffffff, 'current_hash':0xeeeeeeee, 'data':0x00010002})
block = Block({'timestamp': time.time(), 'prev_hash': 0x0, 'current_hash': 0x000dc75a315c77a1f9c98fb6247d03dd18ac52632d7dc6a9920261d8109b37cf, 'nonce': 0, 'transaction':[t1], 'merkle_root': [], 'index': 0})

# Call every functions
# Will throw
chain.add_block(block)
chain.get()
chain.latest_block()
chain.is_valid_hash_difficulty('00001')

#chain.mine(0x0000abcde)
print(chain.get())

