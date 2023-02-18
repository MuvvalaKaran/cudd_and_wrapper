""" Example of logic encryption from Hai Zhou's paper. """

from __future__ import print_function
from cudd import Cudd

mgr = Cudd()

varnames = ['a', 'b', 'c', 'd', 'e', 'f', 'k1', 'k2'];

a,b,c,d,e,f,k1,k2 = [mgr.bddVar(None, name) for name in varnames]

# Function to be encrypted.
y = ((a & b) ^ (c | d)) ^ (e & f)

# One encryption.
ye = (((a & b) ^ (c | d)) ^ k1) ^ ((e & f) ^ ~k2)

# Another encryption.
yr = (((a & b) ^ (c | d)) | k2) ^ ((e & f) & k1)

print('ye and yr are', 'equivalent' if ye == yr else 'not equivalent')

# Find values of k1, k2 that make ye equivalent to y.
F = y ^ ye
(consistF, solutionsF) = F.solveEqn([k1,k2])

if consistF.isZero():
    print("F equation is unconditionally consistent")
else:
    print("F consistency condition:", consistF)
print("F solutions:")
for g in solutionsF:
    print(g)

# Find values of k1, k2 that make yr equivalent to y.
G = y ^ yr
(consistG, solutionsG) = G.solveEqn([k1,k2])

if consistG.isZero():
    print("G equation is unconditionally consistent")
else:
    print("G consistency condition:", consistG)
print("G solutions:")
for g in solutionsG:
    g.printCover()

# Compute a particular solution with all parameters set to constants.
print("G particular solution with constant parameters:")
for g in solutionsG:
    p = g.vectorCompose([k1,k2],[mgr.bddOne(), mgr.bddZero()])
    print(p)
