""" Find set of solution to a set of pseudoboolean constraints. """
from __future__ import print_function
from cudd import Cudd

def linearInequality(x, w, l, u):
    """ Compute the characteristic function of l < w'x < c """
    if not x:
        return m.bddOne() if u > 0 and l < 0 else m.bddZero()
    return x[0].ite(linearInequality(x[1:], w[1:], l - w[0], u - w[0]),
                    linearInequality(x[1:], w[1:], l, u))

m = Cudd()
x = [m.bddVar(i, 'x_%s' % (i+1)) for i in range(10)]

f = linearInequality(x, [3] * 4 + [2] * 6, 4, 13)
print('without incompatibility', end=''); f.summary()

f &= ~x[4] | (~x[0] & ~x[1])
f &= ~x[5] | (~x[0] & ~x[2])
f &= ~x[6] | (~x[1] & ~x[2])
f &= ~x[7] | (~x[0] & ~x[3])
f &= ~x[8] | (~x[1] & ~x[3])
f &= ~x[9] | (~x[2] & ~x[3])
print('f', end=''); f.summary()
f.printCover()
