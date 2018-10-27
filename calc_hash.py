# %%

# bitcoin: hash written in hex

import struct
import binascii
from hashlib import sha256
from functools import reduce
import urllib.request, json
import codecs

# %%

def get_block(block_height):
  with urllib.request.urlopen("https://blockchain.info/block-height/"+str(block_height)+"?format=json") as url:
    data = json.loads(url.read().decode())
    print('hash', data['blocks'][0]['hash'])
    return data['blocks'][0]

data = get_block(540156)
print(data['hash'])

# %%

def reverse_hex(inp):
  return reduce(lambda x, y: x+y, [inp[i: i+2] for i in range(len(inp), -1, -2)])

version = reverse_hex(hex(data['ver'])[2:].zfill(8))
prev = reverse_hex(data['prev_block'])
merkle = reverse_hex(data['mrkl_root'])
time = reverse_hex(hex(data['time'])[2:])
bits = reverse_hex(hex(data['bits'])[2:])
nonce = reverse_hex(str(hex(data['nonce']))[2:])

together = version + prev + merkle + time + bits + nonce

print(together)
header = binascii.unhexlify(together)
res = sha256(sha256(header).digest()).hexdigest()
# res = codecs.encode(sha256(together.encode()).digest(), 'hex_codec')
print(res)
print(reverse_hex(res))



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

difficulty = 3
target_str = '0'*difficulty

m = sha256()
for i in range(2508741199, 2508741199+3):
  m.update(bytes(i))
  result = m.hexdigest()
  print(result)


print('end')


# %%

def dec_hex(inp):
  st = struct.pack("<i", inp)
  return hex(int("0x"+str(binascii.b2a_hex(st))[2:-1], 16))



