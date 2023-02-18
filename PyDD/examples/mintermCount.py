"""Test minterm counting functions."""

from __future__ import print_function

from cudd import Cudd

nB = 1000
nZ = 100
m = Cudd(nB,nZ)

# Test BDDs.
x = [m.bddVar(i, 'x'+str(i)) for i in range(nB)]

f = x[0] | x[1]

print(f.count_as_double())
f.summary(name='f')
print(f.count())
f.summary(2, name='f')
print(f.count(2))

# Test ADDs.
y = [m.addVar(i, 'y'+str(i)) for i in range(nB)]

g = y[0] | y[-1]
print(g.count_as_double())
g.summary(name='g')
print(g.count())
g.summary(2, name='g')
print(g.count(2))

# Test ZDDs.
z = [m.zddVar(i, 'z'+str(i)) for i in range(nZ)]
h = m.zddBase().change(0).change(1)
h.display(name='h')
print(h.count_as_double())
