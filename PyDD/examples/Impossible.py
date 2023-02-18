"""Epistemic model checking applied to the "impossible puzzle."

   Matt picks two integers X and Y such that:
     1 < X < Y
     X + Y <= 100.

   Matt then communicates X+Y to Sam and X*Y to Pam.
   Sam and Pam have the following conversation:
     Pam: I don't know X and Y.
     Sam: I knew you didn't.
     Pam: Now I do know X and Y!
     Sam: And so do I!
   What are X and Y?
"""

from __future__ import print_function, division, unicode_literals
from functools import reduce
import argparse

def print_solutions(solutions):
    """Convert common-knowledge BDD to list of solutions."""
    while not solutions.isZero():
        soln = solutions.pickOneMinterm(P) # ignore next-state variables
        solutions &= ~soln
        cube = soln.pickOneCube()          # convert to list of 0s and 1s
        X = int(''.join(map(str, cube[0:2*m:2])),2)
        Y = int(''.join(map(str, cube[2*m:4*m:2])),2)
        print('X:', X, 'Y:', Y)

def reportC(title):
    """Print summary of common knowledge."""
    if args.verbose > 2:
        C.display(numVars=2*m, name=title)
    elif args.verbose > 0:
        C.summary(numVars=2*m, name=title)

def pre(TR, Dest):
    """Compute the predecessors of Dest."""
    destY = Dest.swapVariables(P,Q)
    return TR.andAbstract(destY, qcube)

def knowsFact(TR, fact):
    """Find plausible worlds where agent knows fact."""
    return fact & C & ~pre(TR, ~fact & C)

def knowsWorld(TR):
    """Find plausible worlds that agent discerns from all other worlds."""
    return C & ~pre(TR & ~mgr.xeqy(P,Q), C)

# Parse command line.
parser = argparse.ArgumentParser(
    description='Solve the "impossible" puzzle',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-v', '--verbose', help='increase output verbosity',
                    action='count', default=0)
args = parser.parse_args()

from cudd import Cudd
mgr = Cudd()

n = 2 # number of agents (2: Pam and Sam)
m = 7 # number of bits in each number

# Each world is identified by two numbers between 2 and 98 (included).
p = [[mgr.bddVar(2*m*i+2*j,   'p_' + str(i) + '_' + str(j)) for j in range(m)]
     for i in range(n)]
q = [[mgr.bddVar(2*m*i+2*j+1, 'q_' + str(i) + '_' + str(j)) for j in range(m)]
     for i in range(n)] # next-world variables

# These are used in predecessor computation.
# Flat lists of present and next state variables.
P = [x for r in p for x in r]
Q = [y for r in q for y in r]
# Cube for quantification.
qcube = reduce(lambda x, y: x & y, Q)

# Initial common knowledge: 1 < p[0] < p[1] and p[0] + p[1] <= 100.

# Phase 1: from 1 < p[0] < p[1] and p[0] + p[1] <= 100 extract upper and
# lower bounds for p[0] and p[1].
C = mgr.xgty(p[1],p[0]) & mgr.interval(p[0],2,49) & mgr.interval(p[1],3,98)

# Phase 2: remove worlds such that p[0] + p[1] > 100.
cworlds = C
while not cworlds.isZero():
    soln = cworlds.pickOneMinterm(P)
    cworlds &= ~soln
    cube = soln.pickOneCube()
    p0 = int(''.join(map(str, cube[0:2*m:2])),2)
    p1 = int(''.join(map(str, cube[2*m::2])),2)
    sum = p0+p1
    if sum > 100:
        C &= ~soln

reportC('Initial C')

# World indistinguishability relations.  Sam cannot distinguish worlds with
# the same X+Y, while Pam cannot distinguish worlds with the same X*Y.

# Cluster worlds according to both their sum and their product.
prddict = {}    # map from integers to BDDs
sumdict = {}    # map from integers to BDDs
worlds = C
while not worlds.isZero():
    psoln = worlds.pickOneMinterm(P)
    worlds &= ~psoln
    pcube = psoln.pickOneCube()
    p0 = int(''.join(map(str, pcube[0:2*m:2])),2)
    p1 = int(''.join(map(str, pcube[2*m::2])),2)
    pprd = p0*p1
    if pprd not in prddict:
        prddict[pprd] = psoln
    else:
        prddict[pprd] |= psoln
    psum = p0+p1
    if psum not in sumdict:
        sumdict[psum] = psoln
    else:
        sumdict[psum] |= psoln

Tpam = mgr.bddZero()
for pv in prddict.values():
    Tpam |= pv & pv.swapVariables(P,Q)
Tsam = mgr.bddZero()
for sv in sumdict.values():
    Tsam |= sv & sv.swapVariables(P,Q)

if args.verbose > 1:
    Tpam.summary(numVars=4*m, name='Tpam')
    Tsam.summary(numVars=4*m, name='Tsam')

# Find worlds in which Pam knows X and Y.
Kp1 = knowsWorld(Tpam)
if args.verbose > 1:
    Kp1.summary(numVars=2*m,name='Kp1')

# Find the worlds where Sam knows that Pam doesn't know X and Y.
Ks1 = knowsFact(Tsam, ~Kp1)

# The fact that Pam does not know X and Y becomes common knowledge.
C &= ~Kp1
reportC('C after Pam says that she doesn\'t know')

# The fact that Sam knew Pam didn't know X and Y becomes common knowledge.
C &= Ks1
reportC('C after Sam says he knew she didn\'t')

# Find worlds where Pam now knows X and Y.
Kp2 = knowsWorld(Tpam)

# The fact that Pam knows becomes common knowledge. 
C &= Kp2
reportC('C after Pam says that now she knows')

# Find worlds where Sam knows X and Y.
Ks2 = knowsWorld(Tsam)

# The fact that Sam knows too becomes common knowledge.
C &= Ks2
reportC('C after Sam says that he knows too')

print_solutions(C)
