"""Example of reachability analysis."""

from __future__ import print_function
from functools import reduce

def image(TR, From, xcube, x, y):
    ImgY = TR.andAbstract(From, xcube)
    return ImgY.swapVariables(y,x)

from cudd import Cudd
m = Cudd()

# Current- and next-state variables.
n = 2
x = [m.bddVar(i,   'x' + str(i)) for i in range(n)]
y = [m.bddVar(n+i, 'y' + str(i)) for i in range(n)]

# Our model.
TR = ((~x[1] & ~x[0] & ~y[1] & y[0]) |
      (~x[1] & x[0] & ~y[0]) |
      (x[1] & ~x[0] & ~y[0]))
Init = ~x[1] & ~x[0]

print("TR = ", TR)
print("Init = ", Init)

# Fixpoint computation.
xcube = reduce(lambda x, y: x & y, x)
Reached = New = Init
while New:
    print(Reached)
    Img = image(TR, New, xcube, x, y)
    New = Img & ~Reached
    Reached |= New
