"""Example from stackoverflow."""

from __future__ import print_function
from functools import reduce

def inspect(function, name, nvars):
    print(name, end='')
    function.summary(nvars) # correct minterm count needs number of variables
    function.printCover()

from cudd import Cudd
m = Cudd()

nx = 2
ny = 3
x = [m.bddVar() for i in range(nx)]
y = [m.bddVar() for i in range(ny)]

R = (~x[0] & x[1] & (~y[0] & y[1] | y[1] & y[2]) |
     x[0] & ~x[1] & (y[0] ^ y[1]) & y[2] |
     ~x[0] & ~x[1] & y[0] & ~y[1] & ~y[2])

# This approach is independent of variable order.  We are free to enable
# reordering or call it explicitly.
m.reduceHeap()

inspect(R, 'R', nx+ny)

# Create auxiliary variables and selector function.
z = [m.bddVar() for i in range(ny)]
zcube = reduce(lambda a, b: a & b, z)
S = ~m.xeqy(y,z)

# A pair is in L iff:
#   - it is in R
#   - there is no other pair in R with the same x and different y
L = R & ~(R.swapVariables(y, z).andAbstract(S, zcube))

inspect(L, 'L', nx+ny)
