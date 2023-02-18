"""Example of use of several BDD operations.

list comprehension, map, reduce, interpolate, overloaded relational operators.
"""

from __future__ import print_function
from functools import reduce

import cudd
m = cudd.Cudd()
v = [m.bddVar(i) for i in range(10)]
vn = [~x for x in v]
lb = reduce(cudd.BDD.conjoin, vn[:6])
print(lb)
ub = reduce(cudd.BDD.disjoin, vn[5:])
print(ub)
f = lb.interpolate(ub)
print(f)
print((lb <= f) & (f <= ub))
