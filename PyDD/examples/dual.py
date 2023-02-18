""" Test duality-related functions. """
from __future__ import print_function
from functools import reduce
from cudd import Cudd

mgr = Cudd()

a,b,c,d = [mgr.bddVar(None,chr(ord('a') + i)) for i in range(4)]

f = a & ~b & c
assert(not f.isSelfDual())
print('f  =', f)
fd = f.dual()
print('fd =', fd)
assert(fd.isDual(f))

# This is a self-dual function.
g = (a & ~b) | (a & c) | (~b & c)
assert(g.isSelfDual())
print('g  =', g)
gd = g.dual()
assert(g == gd)

# Build a self-dual function using the property that a function is self-dual
# if the positive cofactor is the dual of the negative cofactor.
h = d.ite(f, fd)
assert(h.isSelfDual())
print('h  =', h)
hd = h.dual()
assert(h == hd)
