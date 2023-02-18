"""
Count the ways of choosing n distinct nonempty subsets of a set of size m
such that every pair of consecutive subsets are disjoint and their union is not
the entire set. 
"""
from __future__ import print_function
from cudd import Cudd

mgr = Cudd()

n = 10
m = 5
print('n =', n, 'm =', m)
x = [[mgr.bddVar() for j in range(m)] for i in range(n)]
bycol = [[x[i][j] for i in range(n)] for j in range(m)]

f = mgr.bddOne()

# Lexicographic constraints on columns.
for i in range(1,m):
    f &= mgr.inequality(0, bycol[i-1], bycol[i])

# No subset is empty.
for i in range(n):
    g = mgr.bddZero()
    for j in range(m):
        g |= x[i][j]
    f &= g

# Adjacent subsets are disjoint and their union is not S.
for i in range(1,n):
    g = mgr.bddOne()
    h = mgr.bddZero()
    for j in range(m):
        g &= ~(x[i-1][j] & x[i][j])
        h |= ~(x[i-1][j] | x[i][j])
    f &= g & h

# All subsets are distinct.
for i in range(1,n):
    for k in range(i):
        g = mgr.bddZero()
        for j in range(m):
            g |= x[k][j] ^ x[i][j]
        f &= g

#f.printCover()
f.summary()
