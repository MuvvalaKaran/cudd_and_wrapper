""" Find smallest MUX-based implementation. """

from __future__ import print_function
from cudd import Cudd, REORDER_GENETIC, REORDER_EXACT

def oneBit(x0, x1, x2):
    return x0 ^ (~x1 & x2);

mgr = Cudd()

n = 5
names = ['a', 'b', 'c', 'd', 'e', 'R']
a,b,c,d,e,R = [mgr.bddVar(None, name) for name in names]

u = oneBit(a,b,c)
v = oneBit(b,c,d)
x = oneBit(c,d,e) ^ R
y = oneBit(d,e,a)
z = oneBit(e,a,b)

vec = [u,v,x,y,z]

print(mgr.sharingSize(vec))
mgr.enableOrderingMonitoring()

mgr.reduceHeap(REORDER_GENETIC)
print(mgr.sharingSize(vec))
mgr.reduceHeap(REORDER_EXACT)
print(mgr.sharingSize(vec))
mgr.dumpDot(vec, ['u', 'v', 'x', 'y', 'z'])
