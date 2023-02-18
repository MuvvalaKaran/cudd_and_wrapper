"""Test for the eval function."""

from __future__ import print_function
from functools import reduce

from cudd import Cudd
m = Cudd()
n = 4
v = [m.bddVar(i, 'v' + str(i)) for i in range(n)]

conjoin = lambda x, y: x & y
disjoin = lambda x, y: x | y
negate  = lambda x: ~x

f = reduce(conjoin, v)

print(f.eval([0, 1, 0, 1]))
print(f.eval([1 for i in range(n)]))

g = reduce(conjoin, map(negate, v))

print((f | g).eval([0 for i in range(n)]))
print((f | g).eval([0, 0, 1, 0]))

try:
    print(f.eval([1, 1, 1]))
except TypeError as e:
    print("Type error: {0}".format(e.args[0]))

try:
    print(f.eval([1, 0, 3, 1]))
except TypeError as e:
    print("Type error: {0}".format(e.args[0]))
