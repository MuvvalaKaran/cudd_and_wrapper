"""A knights and knaves puzzle by Smullyan.

   At a trial, A, B, C make statements.  Who is guilty?

   This example illustrates two points:
   (1) The statement of X is not always best translated into X.iff(S);
   (2) The constraints may have multiple solutions as long as the
       answer is the same.
"""

from __future__ import print_function

from cudd import Cudd
mgr = Cudd()

n = 3
# tx: x is truthful (x is a knight)
ta,tb,tc = (mgr.bddVar(2*i,   't' + chr(ord('a') + i)) for i in range(n))
# gx: x is guilty
ga,gb,gc = (mgr.bddVar(2*i+1, 'g' + chr(ord('a') + i)) for i in range(n))

# A: I am guilty.
f = ta.iff(ga)
# B: I am the same type as at least one of the others.
f &= tb.ite(ta | tc, ta & tc)
# C: We are all of the same type.
f &= tc.ite(ta & tb, ta | tb)
# Exactly one of A, B, C is guilty.
f &= mgr.cardinality([ga,gb,gc], 1)

if f.isEssential(ga):
    print("A is guilty.")
elif f.isEssential(gb):
    print("B is guilty.")
elif f.isEssential(gc):
    print("C is guilty.")
else:
    print("Ambiguous constraints.")

# The type of C remains unknown, but A is guilty regardless.
print("tgtgtg")
print("aabbcc")
f.printCover()

