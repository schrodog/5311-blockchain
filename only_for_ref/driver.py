# import time
# from blockchain import Blockchain, Block, Transaction

#   # Set things up
# chain = Blockchain()
# t1 = Transaction({'timestamp': time.time(), 'source_address':'home', 'desc_address':'cityline', 'prev_hash':0xffffffff, 'current_hash':0xeeeeeeee, 'data':0x00010002})
# block = Block({'timestamp': time.time(), 'prev_hash': 0x0, 'current_hash': 0x000dc75a315c77a1f9c98fb6247d03dd18ac52632d7dc6a9920261d8109b37cf, 'nonce': 0, 'transaction':[t1], 'merkle_root': [], 'index': 0})

# # Call every functions
# # Will throw
# chain.add_block(block)
# chain.get()
# chain.latest_block()
# chain.is_valid_hash_difficulty('00001')

# #chain.mine(0x0000abcde)
# print(chain.get())

# %%
import json

data = {"type": "RECEIVE_BLOCKCHAIN", 
"source": "a090e6e934", "sender": "a090e6e934", "blockchain": 
  [{"index": 1, "prev_hash": "00000000315c77a1f9c98fb6247d03dd18ac52632d7dc6a9920261d8109b37cf", "timestamp": 15431454813211658, "current_hash": "0000c008a139e78663b45eb4a9c35db6255f0c115816f7f97e0f245bcfa03639", "nonce": 4578, "merkle_root": "0", "transaction": []}, 
  {"index": 2, "prev_hash": "0000c008a139e78663b45eb4a9c35db6255f0c115816f7f97e0f245bcfa03639", "timestamp": 15431478945712724, "current_hash": "0000f6639986eb9c8cb599e069c2cce13034f5570fc5f3195401c86d5143df2f", "nonce": 263212, "merkle_root": "0", "transaction": []}, 
  {"index": 3, "prev_hash": "0000f6639986eb9c8cb599e069c2cce13034f5570fc5f3195401c86d5143df2f", "timestamp": 15431546845940108, "current_hash": "0000f7b59376d0ce6bb1c82097536cfec282592f7ab965782dcd2c84e2d7a100", "nonce": 11580, "merkle_root": "0", "transaction": []}, 
  {"index": 4, "prev_hash": "0000f7b59376d0ce6bb1c82097536cfec282592f7ab965782dcd2c84e2d7a100", "timestamp": 154315468776846, "current_hash": "0000ca035cb6731606c3867a8c89de069f81ea9bce52ba8f70877273dbc2042b", "nonce": 16475, "merkle_root": "0", "transaction": []}
  ]
}
data

# %%
class JSONEncoder(json.JSONEncoder):
  def default(self, o):
    if isinstance(o, ObjectId):
      return str(o)
    return json.JSONEncoder.default(self, o)

# %%
res = JSONEncoder().encode(data)
b = bytes(res, 'utf-8')
b

# %%
json.loads(res.decode())



# '{"type": "RECEIVE_BLOCKCHAIN", "source": "a090e6e934", "sender": "a090e6e934", "blockchain": [{"index": 1, "prev_hash": "00000000315c77a1f9c98fb6247d03dd18ac52632d7dc6a9920261d8109b37cf", "timestamp": 15431454813211658, "current_hash": "0000c008a139e78663b45eb4a9c35db6255f0c115816f7f97e0f245bcfa03639", "nonce": 4578, "merkle_root": "0", "transaction": []}, {"index": 2, "prev_hash": "0000c008a139e78663b45eb4a9c35db6255f0c115816f7f97e0f245bcfa03639", "timestamp": 15431478945712724, "current_hash": "0000f6639986eb9c8cb599e069c2cce13034f5570fc5f3195401c86d5143df2f", "nonce": 263212, "merkle_root": "0", "transaction": []}, {"index": 3, "prev_hash": "0000f6639986eb9c8cb599e069c2cce13034f5570fc5f3195401c86d5143df2f", "timestamp": 15431546845940108, "current_hash": "0000f7b59376d0ce6bb1c82097536cfec282592f7ab965782dcd2c84e2d7a100", "nonce": 11580, "merkle_root": "0", "transaction": []}, {"index": 4, "prev_hash": "0000f7b59376d0ce6bb1c82097536cfec282592f7ab965782dcd2c84e2d7a100", "timestamp": 154315468776846, "current_hash": "0000ca035cb6731606c3867a8c89de069f81ea9bce52ba8f70877273dbc2042b", "nonce": 16475, "merkle_root": "0", "transaction": []}]}'






