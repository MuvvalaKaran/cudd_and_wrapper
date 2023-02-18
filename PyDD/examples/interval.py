"""Example of use of interval and related functions."""

from __future__ import print_function

from cudd import Cudd
m = Cudd()
n = 3
x = [m.bddVar(i, 'x' + str(i)) for i in range(n)]

for i in range(2**n):
    m.interval(x,i,i).printCover()

print(m.interval(x,0,1))

y = [m.bddVar(i+n, 'y' + str(i)) for i in range(n)]

eq = m.xeqy(x,y)
eq.printCover()

eq.cofactor(y[0] & ~y[1] & y[2]).printCover()

