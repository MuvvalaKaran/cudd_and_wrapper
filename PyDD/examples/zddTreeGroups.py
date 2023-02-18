""" Test ZDD variable group tree. """

from __future__ import print_function, unicode_literals, division
from cudd import Cudd, MTR_DEFAULT, MTR_FIXED

mgr = Cudd()

n = 8
Z = [mgr.zddVar(i, 'z%i' % i) for i in range(n)]

f = (Z[0] & Z[2]) | (Z[5] & Z[7]) | (Z[1] & Z[3]) | (Z[4] & Z[6])

mgr.makeZddTreeNode(0, n, MTR_FIXED)
mgr.makeZddTreeNode(0, n//2, MTR_DEFAULT)
mgr.makeZddTreeNode(n//2, n//2, MTR_DEFAULT)
print('before reordering')
mgr.printZddOrder()

mgr.enableReorderingReporting()
mgr.zddReduceHeap()
print('after reordering')
mgr.printZddOrder()
