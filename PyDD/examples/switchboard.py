"""Count the number of tile colorings of an m x n board.
   The board is made of tiles that can be made light or dark.
   Eech row and column of the board has a switch that flips the colors
   of all tiles in that row or column when it is flipped.

   It can be proved by induction that the number of configurations
   reachable from any configuration is 2^{m+n-1}.  Here we simply
   compute the image of the function that describes the board: each
   tile is the exclusive OR of its row and column variables.
   We then compute the number of models of this function.
"""
from __future__ import print_function
from functools import reduce
from cudd import Cudd

mgr = Cudd()
mgr.enableReorderingReporting()
mgr.autodynEnable()

m = 14
n = 13

Z = [[mgr.bddVar(None, 'z%s_%s' % (i,j)) for j in range(m)] for i in range(n)]
X = [mgr.bddVar(None, 'x%s' % i) for i in range(n)]
Y = [mgr.bddVar(None, 'y%s' % j) for j in range(m)]
F = [[(Z[i][j]).iff(X[i] ^ Y[j]) for j in range(m)] for i in range(n)]

conjoin = lambda a, b: a & b
# Early quantification of the X variables.
T = reduce(conjoin,
           [reduce(conjoin, F[i]).existAbstract(X[i]) for i in range(n)])
C = reduce(conjoin, Y)
I = T.existAbstract(C)
print(' '.join(mgr.bddOrder()))
print('count =', I.count(m*n))
print('size  =', I.size())
