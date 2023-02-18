"""Test manager transfer."""

from __future__ import print_function

from cudd import Cudd

m1 = Cudd()

x,y,z = (m1.bddVar(i, chr(ord('x') + i)) for i in range(3))

f = (~x & ~y & ~z) | (x & y)
print(f)

m2 = Cudd()
a,b,c = (m2.bddVar(i, chr(ord('a') + i)) for i in range(3))

g = f.transfer(m2)
print(g)

h = g.transfer(m1)
print("f and h are identical:", f == h)
