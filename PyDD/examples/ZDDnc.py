""" Test conversion from BDDs to ZDDs with zero cofactoring of variables. """

from __future__ import print_function
from functools import reduce

from cudd import Cudd

mgr = Cudd()
mgr.enableOrderingMonitoring()

# Current- and next-state variables.
n = 6
x = [mgr.bddVar(2*i,   'x' + str(i)) for i in range(n)]
y = [mgr.bddVar(2*i+1, 'y' + str(i)) for i in range(n)]
mgr.zddVarsFromBddVars()

ycube = reduce(lambda a, b: a & b, y)

f1 = (~x[0] ^ x[1]) & x[2] & ~x[3]
f1.display(n, name='f1')

mgr.zddRealignEnable()
mgr.reduceHeap()
mgr.printZddOrder()

g1 = f1.toZDD(ycube)
g1.display(2*n, detail=4, name='g1')
h1 = g1.toBDD().existAbstract(ycube)
print('back and forth preserves equivalence:', f1 == h1)

f2 = x[0].ite(x[2], x[3])
f2.display(n, name='f2')

g2 = f2.toZDD(ycube)
g2.display(2*n, detail=4, name='g2')
h2 = g2.toBDD().existAbstract(ycube)
print('back and forth preserves equivalence:', f2 == h2)

f3 = ~x[0] & x[1] & x[2] & ~x[3] & ~x[4] & ~x[5]
f3.display(n, name='f3')
g3 = f3.toZDD(ycube)
g3.display(2*n, detail=4, name='g3')
h3 = g3.toBDD().existAbstract(ycube)
print('back and forth preserves equivalence:', f2 == h2)
