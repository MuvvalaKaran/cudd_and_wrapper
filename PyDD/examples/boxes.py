""" Play with cardinality constraints. """

from __future__ import print_function
from functools import reduce
from cudd import Cudd

def box(x,y,i):
    return x[i] & ~y[i]

def robot(x,y,i):
    return ~x[i] & y[i]

def valid(x,y,i):
    return ~(x[i] & y[i])

mgr = Cudd()

n = 5
m = (n+1) // 2

x = [mgr.bddVar(2*i,   'x' + str(i)) for i in range(n)]
y = [mgr.bddVar(2*i+1, 'y' + str(i)) for i in range(n)]

b = [box(x,y,i) for i in range(n)]
v = [valid(x,y,i) for i in range(n)]
r = [robot(x,y,i) for i in range(n)]

c = mgr.cardinality(b, m) & mgr.cardinality(r, 1) & mgr.cardinality(v, n)

c.summary(name='c')

for i in range(n):
    (c & ~box(x,y,i)).summary(name='cb'+str(i))
    (c & ~robot(x,y,i)).summary(name='cr'+str(i))

s0 = reduce(lambda a, b: a & b,
            [box(x,y,i) for i in [0, 3, 4]], mgr.bddOne()) & robot(x,y,2)

cs0 = c & ~s0
cs0.summary(name='cs0')

(cs0.restrict(c)).summary(name='cr0')

if n < 6:
    mgr.dumpDot([c, cs0],["c", "cs0"])
