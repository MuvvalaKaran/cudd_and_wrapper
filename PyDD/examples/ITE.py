"""Test of BDD ITE."""

from __future__ import print_function
from cudd import Cudd

mgr = Cudd()
a, c, b, d = (mgr.bddVar(None, nm) for nm in ['a', 'c', 'b', 'd'])

f = a | c.ite(b,~d)
print(f)
