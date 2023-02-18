"""Computation of INV for busy_ring with two-place strengthening."""

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

from cudd import Cudd, REORDER_SIFT_CONVERGE
m = Cudd()

N = 4
u_ack = [m.bddVar(i,     'u_ack_' + str(i)) for i in range(N)]
u_req = [m.bddVar(N+i,   'u_req_' + str(i)) for i in range(N)]
ack_1 = [m.bddVar(2*N+i, 'ack_1_' + str(i)) for i in range(N)]
token = [m.bddVar(3*N+i, 'token_' + str(i)) for i in range(N+1)]
v = u_ack + u_req + ack_1 + token

reach = (
    (~ack_1[0] | ~token[0]) &
    (~ack_1[1] | ~token[1]) &
    (~ack_1[2] | ~token[2]) &
    (~ack_1[3] | ~token[3]) &
    (u_ack[0] | ~ack_1[0] | u_req[0]) &
    (u_ack[1] | ~ack_1[1] | u_req[1]) &
    (u_ack[2] | ~ack_1[2] | u_req[2]) &
    (u_ack[3] | ~ack_1[3] | u_req[3]) &
    (~u_ack[0] | ack_1[0] | ~u_req[0]) &
    (~u_ack[1] | ack_1[1] | ~u_req[1]) &
    (~u_ack[2] | ack_1[2] | ~u_req[2]) &
    (~u_ack[3] | ack_1[3] | ~u_req[3]) &
    (token[0] | ~u_ack[1] | ~ack_1[1]) &
    (token[1] | ~u_ack[2] | ~ack_1[2]) &
    (token[2] | ~u_ack[3] | ~ack_1[3]) &
    (~u_ack[0] | ~ack_1[0] | token[4]) &
    (~token[2] | token[3] | token[4]) &
    (token[2] | ~token[3] | ~token[4]) &
    (token[0] | ~token[2] | ~token[4]) &
    (~token[0] | token[2] | token[4]) &
    (~token[0] | token[1] | ~token[2]) &
    (token[0] | ~token[1] | token[2])
    )

reach3 = (
    (~ack_1[0] | ~token[0]) &
    (~ack_1[1] | ~token[1]) &
    (~ack_1[2] | ~token[2]) &
    (~ack_1[0] | token[3] | ~u_ack[0]) &
    (~ack_1[1] | token[0] | ~u_ack[1]) &
    (~ack_1[2] | token[1] | ~u_ack[2]) &
    (~ack_1[0] | u_ack[0] | u_req[0]) &
    (~ack_1[1] | u_ack[1] | u_req[1]) &
    (~ack_1[2] | u_ack[2] | u_req[2]) &
    (ack_1[0] | ~u_ack[0] | ~u_req[0]) &
    (ack_1[1] | ~u_ack[1] | ~u_req[1]) &
    (ack_1[2] | ~u_ack[2] | ~u_req[2]) &
    (token[0] | ~token[1] | ~token[3]) &
    (~token[0] | token[1] | token[3]) &
    (~token[1] | token[2] | token[3]) &
    (~token[3] | token[1] | ~token[2])
    )

m.enableReorderingReporting()
m.reduceHeap(REORDER_SIFT_CONVERGE)
#print(reach)
#reach.printCover()
reach.summary()

analyze(m, reach, v)

pcube = u_req[-2] & u_req[-1] & u_ack[-2] & u_ack[-1] & token[-3] & token[-2] \
        & ack_1[-2] & ack_1[-1]
prototype = reach.existAbstract(pcube)
prototype.printCover()
prototype.summary(4*(N-1)+1)

u_ackp = [m.bddVar(4*N+1+i, 'u_ackp_' + str(i)) for i in range(N)]
u_reqp = [m.bddVar(5*N+1+i, 'u_reqp_' + str(i)) for i in range(N)]
ack_1p = [m.bddVar(6*N+1+i, 'ack_1p_' + str(i)) for i in range(N)]
tokenp = [m.bddVar(7*N+1+i, 'tokenp_' + str(i)) for i in range(N+1)]
vp = u_ackp + u_reqp + ack_1p + tokenp

abscube = reduce(lambda a, b: a & b, v)
invariant = m.bddOne()

for i in range(0,N-1):
    for j in range(i+1,N):
        print("psi", i, j)
        alpha = ((~u_ackp[i] ^ u_ack[0]) &
                 (~u_reqp[i] ^ u_req[0]) &
                 (~ack_1p[i] ^ ack_1[0]) &
                 (~tokenp[i] ^ token[0]) &
                 (~u_ackp[j] ^ u_ack[1]) &
                 (~u_reqp[j] ^ u_req[1]) &
                 (~ack_1p[j] ^ ack_1[1]) &
                 (~tokenp[j] ^ token[1]) &
                 (~tokenp[N] ^ token[N]))
        psi = prototype.andAbstract(alpha,abscube).swapVariables(vp,v)
        psi.summary(4*(N-1)+1)
        invariant &= psi

print("The candidate invariant:")
#invariant.printCover()
invariant.summary(4*N+1)

# In this case the candidate invariant is the set of reachable states,
# which is already known to be inductive.
print("invariant == reach is", invariant == reach)
