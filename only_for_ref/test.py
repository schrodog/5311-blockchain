# %%
from hashlib import sha256
t = 'coinbase7066edfd21d5b7dd919410015432153057109854'

s = sha256()
s.update(t.encode())
s.hexdigest()

# %%
a = [(1,0),(2,1)]
b = [(1,0,30),(1,1,60), (1,2,20), (2,1,25)]


[j for j in b if all([i != j[:2] for i in a])]

# %%

import json

# a = json.dumps({'a': 1, 'b': 2}{'c':3,'d':4})
a = "[{'a': 1, 'b': 2},{'c':3,'d':4}]"

json.loads(a)










