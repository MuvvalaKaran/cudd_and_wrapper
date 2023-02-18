"""A knights and knaves puzzle by Smullyan.

   Which of A, B, C is certainly not the witch doctor?
"""

from __future__ import print_function

from cudd import Cudd
mgr = Cudd()

n = 3
# tx: the x is truthful
ta,tb,tc = (mgr.bddVar(2*i,   't' + chr(ord('a') + i)) for i in range(n))
# wx: x is the witch doctor
wa,wb,wc = (mgr.bddVar(2*i+1, 'w' + chr(ord('a') + i)) for i in range(n))

# A : I am the witch doctor.
f = ta.iff(wa)
# B : I am not the witch doctor.
f &= tb.iff(~wb)
# C : At most one of us is a knight.
f &= tc.iff(mgr.cardinality([ta,tb,tc],0,1))
# Exactly one of A, B, and C is the witch doctor.
f &= mgr.cardinality([wa,wb,wc], 1)

if f.isEssential(~wa):
    print("A is not the witch doctor.")
elif f.isEssential(~wb):
    print("B is not the witch doctor.")
elif f.isEssential(~wc):
    print("C is not the witch doctor.")
else:
    print("Ambiguous constraints.")

print("twtwtw")
print("aabbcc")
f.printCover()
