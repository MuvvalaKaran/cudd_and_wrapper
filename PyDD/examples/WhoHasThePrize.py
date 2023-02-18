"""A knights and knaves puzzle by Smullyan.

   Who has the prize among A, B, and C?
"""

from __future__ import print_function

from cudd import Cudd
mgr = Cudd()

n = 3
# tx: x is truthful (x is a knight)
ta,tb,tc = (mgr.bddVar(2*i,   't' + chr(ord('a') + i)) for i in range(n))
# px: x has the prize
pa,pb,pc = (mgr.bddVar(2*i+1, 'p' + chr(ord('a') + i)) for i in range(n))

# A: B doesn't have the prize.
f = ta ^ pb
# B: I don't have the prize.
f &= tb ^ pb
# C: I have the prize.
f &= tc.iff(pc)
# Exactly one of A, B, C has the prize.
f &= mgr.cardinality([pa,pb,pc], 1)
# At least one is a knight and at least one is a knave.
f &= mgr.cardinality([ta,tb,tc], 1,2)

if f <= pa:
    print("A has the prize.")
elif f <= pb:
    print("B has the prize.")
elif f <= pc:
    print("C has the prize.")
else:
    print("Ambiguous constraints.")

print("tptptp")
print("aabbcc")
f.printCover()
