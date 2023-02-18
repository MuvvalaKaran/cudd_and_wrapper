""" Test variable group tree. """

from __future__ import print_function, unicode_literals, division
from cudd import Cudd, MTR_DEFAULT, MTR_FIXED

mgr = Cudd()

n = 8
X = [mgr.bddVar(i, 'x%i' % i) for i in range(n)]

f = (X[0] & X[2]) | (X[5] & X[7]) | (X[1] & X[3]) | (X[4] & X[6])

mgr.makeTreeNode(0, n, MTR_FIXED)
mgr.makeTreeNode(0, n//2, MTR_DEFAULT)
mgr.makeTreeNode(n//2, n//2, MTR_DEFAULT)
print('before reordering')
mgr.printBddOrder()

mgr.enableReorderingReporting()
mgr.reduceHeap()
print('after reordering')
mgr.printBddOrder()
