"""Variations on the function in Marcel Wild's manuscript."""

from __future__ import print_function
from cudd import Cudd

mgr = Cudd()

n = 5
names = ['x1', 'x3', 'x4', 'x7', 'x8']
x = [mgr.bddVar(None, nm) for nm in names]
x1, x3, x4, x7, x8 = x

#n = 10
#x = [mgr.bddVar(i, 'x' + str(i+1)) for i in range(n)]
#x1, x3, x4, x7, x8 = (x[i-1] for i in [1,3,4,7,8])

F = x1.ite(x7 & x8 | ~x4, x3.ite(x8, ~x7))
print('F', end='')
F.display()
print(F)
print('|F| =', F.count())

#G = F.vectorCompose([x1,x4,x3,x7,x8],[~x1,~x4,~x3,~x7,~x8])
#print('|G| =', G.count())

for k in range(n+1):
    c = mgr.cardinality(x, k)
    fc = F & c
    print('models with ', k, 'ones:', fc.count())
    #fc.printCover()
