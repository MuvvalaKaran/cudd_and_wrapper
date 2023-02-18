"""A knights and knaves puzzle by Smullyan.

   Who is the magician and which type is each?
"""

from __future__ import print_function

from cudd import Cudd
mgr = Cudd()

n = 3
# tx: x is truthful (x is a knight)
ta,tb,tc = (mgr.bddVar(2*i,   't' + chr(ord('a') + i)) for i in range(n))
# mx: x is a magician
ma,mb,mc = (mgr.bddVar(2*i+1, 'm' + chr(ord('a') + i)) for i in range(n))

# A: B is not both a knave and a magician.
f = ta.iff(tb | ~mb)
# B: Either A is a knave or I'm not a magician.
f &= tb.iff(~ta | ~mb)
# C: The magician is a knave.
f &= tc.iff(~(ma & ta) & ~(mb & tb) & ~(mc & tc))
# Exactly one of A, B, C is a magician.
f &= mgr.cardinality([ma,mb,mc], 1)

if f <= ma:
    print("A is the magician.")
elif f <= mb:
    print("B is the magician.")
elif f <= mc:
    print("C is the magician.")
else:
    print("Ambiguous constraints.")

print("tmtmtm")
print("aabbcc")
f.printCover()
