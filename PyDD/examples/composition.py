"""Examples of composition and variable substitution."""

from __future__ import print_function
from cudd import Cudd
m = Cudd()

x0,x1,x2,x3 = (m.bddVar(i,   'x' + str(i)) for i in range(4))
y0,y1,y2,y3 = (m.bddVar(i+4, 'y' + str(i)) for i in range(4))

f = x0 | ~x1 & x3
print(f)
# x0 | ~(x1 | ~x3) 

print(f.swapVariables([x0,x1,x2,x3],[y0,y1,y2,y3]))
# y0 | ~(y1 | ~y3)
print(f.swapVariables([x0,x1,x2,x3],[y3,y2,y1,y0]))
# y0 & (y3 | ~y2) | ~y0 & y3

g = y1 | y3
print(f.compose(g,1))
# x0 | ~((y1 | y3) | ~x3)
