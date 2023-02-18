"""Computation of INV for dining philosophers for pairs."""

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

N = 4
s0 = []
s1 = []
for i in range(N):
    s1.append(m.bddVar(2*i,   's1_' + str(i)))
    s0.append(m.bddVar(2*i+1, 's0_' + str(i)))
v = s0 + s1

reach = m.bddOne()
for i in range(N):
    reach &= (~s0[i] | ~s1[i]) & (~s1[i] | ~s1[(i+1) % N])

#print(reach)
reach.printCover()
reach.summary()

analyze(m, reach, v)

conjoin = lambda a,b: a&b

pcube = reduce(conjoin, s0[2:]) & reduce(conjoin, s1[2:])
prototype = reach.existAbstract(pcube)
print("prototype", end="")
prototype.summary(2*(N-1))
prototype.printCover()

s0p = []
s1p = []
for i in range(N):
    s1p.append(m.bddVar(2*N+2*i,   's1p_' + str(i)))
    s0p.append(m.bddVar(2*N+2*i+1, 's0p_' + str(i)))
vp = s0p + s1p

abscube = reduce(conjoin, v)
invariant = m.bddOne()

for i in range(0,N-1):
    for j in range(i+1,N):
        print("psi", i, j, end="")
        alpha = ((~s0p[i] ^ s0[0]) &
                 (~s1p[i] ^ s1[0]) &
                 (~s0p[j] ^ s0[1]) &
                 (~s1p[j] ^ s1[1]))
        psi = prototype.andAbstract(alpha,abscube).swapVariables(vp,v)
        psi.summary(2*(N-1))
        invariant &= psi

print("The candidate invariant:")
invariant.printCover()
invariant.summary(2*N)

# In this case the candidate invariant is a proper subset of reachable states;
# hence it is too strong to be inductive.
print("invariant < reach is", invariant < reach)
