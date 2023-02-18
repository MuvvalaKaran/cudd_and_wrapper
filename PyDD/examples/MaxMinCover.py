""" Find minimal vertex covers of maximum cardinality for a given graph. 

    The graph for this example is:

    v0 --- v1 --- v2 --- v3 --- v4.
"""

from __future__ import print_function
from cudd import Cudd

mgr = Cudd()

n = 5
v = [mgr.bddVar(i, 'v' + str(i)) for i in range(n)]

# Start with covering constraints.
f = (v[0] | v[1]) & (v[1] | v[2]) & (v[2] | v[3]) & (v[3] | v[4])

# Add minimality constraints.  Note that two of these constraints are
# subsumed by two others.
f &= ((~v[0] | ~v[1]) & (~v[1] | ~v[0] | ~v[2]) & (~v[2] | ~v[1] | ~v[3]) &
      (~v[3] | ~v[2] | ~v[4]) & (~v[4] | ~v[3]))

# Print all minimal covers.  Note that all prime implicants are minterms.
f.printCover()

# Replace x with ~x in f to obtain h, so that minimum number of 1s
# in h corresponds to minimum number of 0s in f.
h = f.vectorCompose(v, [~x for x in v])
h.printCover()

# Find minimum number of 1s in a satisfying assignment of h.
mlen = h.shortestLength()
# Build constraint to select the minterms of f with the maximum number of 1s.
card = mgr.cardinality(v, n-mlen)
(f&card).printCover()
