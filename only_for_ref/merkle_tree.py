# %%
from collections import OrderedDict
from hashlib import sha256
import codecs
import binascii
from functools import reduce

# %%

# block #100,000, concern on transactions
# f3e94742aca4b5ef85488dc37c06c3282295ffec960994b2c0d5ac2a25a95766

msg1 = "8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87".encode()
msg2 = "fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4".encode()
msg3 = "6359f0868171b1d194cbee1af2f16ea598ae8fad666d9b012c8ed2b79a236ec4".encode()
msg4 = "e9a66845e05d5abc0ad04ec80f774a7e585c6e8db975962d069a522137b80c1d".encode()

# since same string can have different value under different encoding system, 
# to avoid conflit there must be explicit convertion
def create_hex(msg):
  return sha256(msg).digest()

def reverse_hex(inp):
  return reduce(lambda x, y: x+y, [inp[i: i+2] for i in range(len(inp), -1, -2)])

def calc_merkle(msg1, msg2):
  header = binascii.unhexlify(reverse_hex(msg1) + reverse_hex(msg2))
  res = sha256(sha256(header).digest()).hexdigest()
  return reverse_hex(res)


# %%

# d = OrderedDict()
# d['a'] = codecs.encode(create_hex(msg1), 'hex_codec')
# d['b'] = codecs.encode(create_hex(msg2), 'hex_codec')
# d['c'] = codecs.encode(create_hex(msg3), 'hex_codec')
# d['d'] = codecs.encode(create_hex(msg4), 'hex_codec')

# d['a'] = binascii.hexlify(create_hex(msg1).digest())
# d['a'] = codecs.encode(create_hex(msg1), 'hex_codec')

r1 = calc_merkle(msg1, msg2)
r2 = calc_merkle(msg3, msg4)
r3 = calc_merkle(r1,r2)
print(r3)

# %%

import merkle 

tree = merkle.MerkleTree([msg1])
tree.add_hash(msg2)
tree.add_hash(msg3)
tree.add_hash(msg4)
print(tree.get_all_hex_chains())



# %%


# %%

# n = 2
# for line in [msg1,msg2]:
#   orig_list = [line[i:i+n] for i in range(0, len(line), n)]
#   reversed_list = orig_list[::-1]
#   reverse = ''.join(reversed_list)
# print(orig_list)
# print(reverse)








