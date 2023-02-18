"""Example of computation of INV for MUX-SEM."""

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

x = m.bddVar(0,'x')
z = [m.bddVar(1 + j + 2 * i, 'z' + str(i) + '_' + str(j)) for i in range(N) for j in range(2)]
v = [x] + z

reach = (x & ~z[1] & ~z[3] & ~z[5] |
         ~x & z[1] & ~z[3] & ~z[5] |
         ~x & ~z[1] & z[3] & ~z[5] |
         ~x & ~z[1] & ~z[3] & z[5])
print(reach)
reach.printCover()

analyze(m, reach, v)

# This prototype assertion can be used instead of reach
# in the compositions with the abstraction relations.
prototype = reach.existAbstract(z[4]&z[5])
print("Prototype:", prototype)
prototype.printCover()

# Primed variables.  These could be interleaved with the original variables,
# but here they are not.
xp = m.bddVar(2*N+1, 'xp')
zp = [m.bddVar(2*N+2 + j + 2 * i, 'zp' + str(i) + '_' + str(j)) for i in range(N) for j in range(2)]
vp = [xp] + zp

abscube = reduce(lambda a, b: a & b, v)
invariant = m.bddOne()

for h in range(0,2*(N-1),2):
    for t in range(h+2,2*N,2):
        print("psi", h, t)
        alpha = (~xp ^ x) & (~zp[h] ^ z[0]) & (~zp[h+1] ^ z[1]) & (~zp[t] ^ z[2]) & (~zp[t+1] ^ z[3])
        psi = prototype.andAbstract(alpha,abscube).swapVariables(vp,v)
        psi.printCover()
        invariant &= psi

print("The candidate invariant is:")
invariant.printCover()
