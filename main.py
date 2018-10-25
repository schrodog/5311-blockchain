# %%

# bitcoin: hash written in hex

from hashlib import sha256

# %%

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

# prev = "000000006a625f06636b8bb6ac7b960a8d03705d1ace08b1a19da3fdcc99ddbd"
# time = 1231470173
# b = bytes(prev)[::-1]
# print(struct.pack("<s", a))
# h = hex(time)

def dec_hex(inp):
  st = struct.pack("<i", inp)
  return hex(int("0x"+str(binascii.b2a_hex(st))[2:-1], 16))
  

# tmp = int('0x'+prev,16)
# print(dec_hex(time))
# print(bytes(prev, "utf-8"))
# print(struct.pack("<p", bytes(prev, "utf-8")))
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
  return reduce(lambda x, y: x+y, [inp[i: i+2] for i in range(len(inp), -1, -2)])

version = reverse_hex(hex(data['version'])[2:].zfill(8))
prev = reverse_hex(data['previousblockhash'])
merkle = reverse_hex(data['merkleroot'])
time = reverse_hex(hex(data['time'])[2:])
bits = reverse_hex(data['bits'])
nonce = reverse_hex(str(hex(data['nonce']))[2:])

together = version + prev + merkle + time + bits + nonce

header = binascii.unhexlify(together)
res = hashlib.sha256(hashlib.sha256(header).digest()).hexdigest()
reverse_hex(res)

# %%

# target = max target / difficulty

# hex(0x00ffff * 2**(8*(0x1d - 3)))[2:].zfill(64)

import math

hex(math.ceil(0x00000000FFFF0000000000000000000000000000000000000000000000000000 / 0x00000000000404CB000000000000000000000000000000000000000000000000))


# %%

import decimal
import math
l = math.log
e = math.e

print (0x00ffff * 2**(8*(0x1d - 3)) / float(0x0404cb * 2**(8*(0x1b - 3))))
print (l(0x00ffff * 2**(8*(0x1d - 3)) / float(0x0404cb * 2**(8*(0x1b - 3)))))
print (l(0x00ffff * 2**(8*(0x1d - 3))) - l(0x0404cb * 2**(8*(0x1b - 3))))
print (l(0x00ffff) + l(2**(8*(0x1d - 3))) - l(0x0404cb) - l(2**(8*(0x1b - 3))))
print (l(0x00ffff) + (8*(0x1d - 3))*l(2) - l(0x0404cb) - (8*(0x1b - 3))*l(2))
print (l(0x00ffff / float(0x0404cb)) + (8*(0x1d - 3))*l(2) - (8*(0x1b - 3))*l(2))
print (l(0x00ffff / float(0x0404cb)) + (0x1d - 0x1b)*l(2**8))


# %%
import codecs
from binascii import b2a_hex

decode_hex = codecs.getdecoder("hex_codec")
target = "00000000000000000000000000000000000000000000006e8102000000000000"
target = decode_hex(target)[0]
target = target[::-1]
target = b2a_hex(target)
print(target)



maxtarget = "00000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
# difficulty = int(maxtarget, 16) / int(target, 16)
difficulty = 1

current_target = int(maxtarget,16) / difficulty

print(hex(math.ceil(current_target)))

# %%
import struct

def read_file():
  with open("/home/lkit/tmp/blockchain_headers", "rb") as f:
    while True:
      chunk = f.read(8192)
      if chunk:
        for b in chunk:
          yield b
      else:
        break

a = ''
for b in read_file():
  a += str(struct.pack("i", b))

print(a)

# %%







