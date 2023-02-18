"""A knights and knaves puzzle by Smullyan.

   In which of the five rooms is the lady?
"""

from __future__ import print_function

from cudd import Cudd
mgr = Cudd()

n = 5
# tx: sign on the door of room x is truthful
t = [mgr.bddVar(2*i,   't' + str(i)) for i in range(n)]
# rx: the woman is in room x
r = [mgr.bddVar(2*i+1, 'r' + str(i)) for i in range(n)]

# Sign 1: The lady is not in Room2.
f = t[0] ^ r[1]
# Sign 2: The lady is not in this room.
f &= t[1] ^ r[1]
# Sign 3: The lady is not in Room 1.
f &= t[2] ^ r[0]
# Sign 4: At least one of these five signs is false.
f &= t[3] ^ (t[0] & t[1] & t[2] & t[3] & t[4])
# Sign 5: Either this sign is false, or the sign on the room with the lady is true.
g = mgr.bddOne()
for i in range(n):
    g &= ~r[i] | t[i]
f &= t[4].iff(~t[4] | g)
# The lady is in one of the rooms.
f &= mgr.cardinality(r, 1)

for var in r:
    if f <= var:
        print("The lady is in room", var.index() // 2 + 1)

print("trtrtrtrtr")
print("1122334455")
f.printCover()
