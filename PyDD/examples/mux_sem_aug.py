"""Example of computation of INV for Augmented MUX-SEM."""

from __future__ import print_function
from functools import reduce

def analyze(m, f, v):
    """Analyze variable dependence and symmetry."""
    print("Dependent variables:")
    for index in range(len(v)):
        if f.varIsDependent(v[index]):
            print(m.getVariableName(index), "is dependent")
    print("Symmetric variables:",
          [(m.getVariableName(i), m.getVariableName(j))
           for i in range(len(v)) for j in range(len(v))
           if i < j and f.varsAreSymmetric(i,j)])

from cudd import Cudd
m = Cudd()

N = 3 # number of agents

# Variables: x is the semaphore.  Each agent's state is encoded as follows:
#
# I : 00 (~zi_1 & ~zi_0)
# T : 01 (~zi_1 &  zi_0)
# C : 11 ( zi_1 &  zi_0)
# E : 10 ( zi_1 & ~zi_0)
#
# so that the invariant of interest only depends on zi_1 (and x).
# The encoding of last_entered uses y1 as MSB and y0 as LSB.

x = m.bddVar(0,'x')
z = [m.bddVar(1 + j + 2 * i, 'z' + str(i) + '_' + str(j)) for i in range(N) for j in range(2)]
y = [m.bddVar(2*N+1 + i, 'y' + str(i)) for i in range(2)]
v = [x] + z + y

reach = (x & ~z[1] & ~z[3] & ~z[5] & ~y[0] |
         x & ~z[1] & ~z[3] & ~z[5] & ~y[1] |
         ~x & z[1] & ~z[3] & ~z[5] & ~y[0] & ~y[1] |
         ~x & ~z[1] & z[3] & ~z[5] &  y[0] & ~y[1] |
         ~x & ~z[1] & ~z[3] & z[5] & ~y[0] &  y[1])
print(reach)
reach.printCover()

analyze(m, reach, v)

# This prototype assertion can be used instead of reach
# in the compositions with the abstraction relations.
prototype = reach.existAbstract(reduce(lambda a,b: a&b, z[2:]))
print("Prototype:", prototype)
prototype.printCover()

# Primed variables.  These could be interleaved with the original variables,
# but here they are not.
xp = m.bddVar(2*N+3, 'xp')
zp = [m.bddVar(2*N+4 + j + 2 * i, 'zp' + str(i) + '_' + str(j)) for i in range(N) for j in range(2)]
yp = [m.bddVar(4*N+4 + i, 'yp' + str(i)) for i in range(2)]

vp = [xp] + zp + yp

abscube = reduce(lambda a, b: a & b, v)
invariant = m.bddOne()

for j in range(N):
    binj = bin(j)[2:]
    if binj[-1] == '1':
        yp_equals_j = yp[0]
    else:
        yp_equals_j = ~yp[0]
    if len(binj) > 1 and binj[-2] == '1':
        yp_equals_j &= yp[1]
    else:
        yp_equals_j &= ~yp[1]
    yp_equals_j ^= (y[1] | y[0])
    # The following correction is needed because y' != j does not mean
    # that y' can take a value outside the domain of y.
    yp_equals_j &= ~(yp[1] & yp[0])
    print("yp == ", binj)
    yp_equals_j.printCover()
    alpha = (~xp ^ x) & (~zp[2*j] ^ z[0]) & (~zp[2*j+1] ^ z[1]) & yp_equals_j
    psi = prototype.andAbstract(alpha,abscube).swapVariables(vp,v)
    print("psi", j)
    psi.printCover()
    invariant &= psi

print("The candidate invariant is:")
invariant.printCover()

# In this case the candidate invariant is the set of reachable states,
# which is already known to be inductive.
print("invariant == reach is", invariant == reach)
