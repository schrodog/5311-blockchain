# %%

# bitcoin: hash written in hex

import hashlib

difficulty = 3
target_str = '0'*difficulty

m = hashlib.sha256()
for i in range(2508741199, 2508741199+3):
  m.update(bytes(i))
  result = m.hexdigest()
  # if result[:difficulty] == target_str:
  print(result)


print('end')

# %%

import struct
import binascii

prev = "000000006a625f06636b8bb6ac7b960a8d03705d1ace08b1a19da3fdcc99ddbd"
time = 1231470173
# b = bytes(prev)[::-1]
# print(struct.pack("<s", a))
# h = hex(time)

def dec_hex(inp):
  st = struct.pack("<i", inp)
  return hex(int("0x"+str(binascii.b2a_hex(st))[2:-1], 16))
  

tmp = int('0x'+prev,16)
print(dec_hex(time))
print(bytes(prev, "utf-8"))
print(struct.pack("<p", bytes(prev, "utf-8")))
# print(dec_hex(tmp))


# %%
from functools import reduce

data = {
  "hash": "0000000082b5015589a3fdf2d4baff403e6f0be035a5d9742c1cae6295464449",
  "confirmations": 470914,
  "height": 3,
  "version": 1,
  "merkleroot": "999e1c837c76a1b7fbb7e57baf87b309960f5ffefbf2a9b95dd890602272f644",
  "time": 1231470173,
  "mediantime": 1231469744,
  "nonce": 1844305925,
  "bits": "1d00ffff",
  "difficulty": 1,
  "chainwork": "0000000000000000000000000000000000000000000000000000000400040004",
  "previousblockhash": "000000006a625f06636b8bb6ac7b960a8d03705d1ace08b1a19da3fdcc99ddbd",
  "nextblockhash": "000000004ebadb55ee9096c9a2f8880e09da59c0d68b1c228da88e48844a1485"
}

def reverse_hex(inp):
  return '0x'+reduce(lambda x, y: x+y, [inp[i: i+2] for i in range(len(inp), -1, -2)])

print(reverse_hex(data['previousblockhash']))
print(reverse_hex(data['merkleroot']))
nonce = str(hex(data['nonce']))[2:]
print(reverse_hex(nonce))


# %%
together = "01000000bddd99ccfda39da1b108ce1a5d70038d0a967bacb68b6b63065f626a0000000044f672226090d85db9a9f2fbfe5f0f9609b387af7be5b7fbb7a1767c831c9e995dbe6649ffff001d05e0ed6d"

header = binascii.unhexlify(together)
res = hashlib.sha256(hashlib.sha256(header).digest()).hexdigest()
reverse_hex(res)




