"""Epistemic model checking example.

   How old are your kids?

   The following conversation takes place between Bob and Alice:

   A: Do you have kids?
   B: I have three.
   A: How old are they?
   B: The product of their ages is 36.
   A: How interesting... Tell me more!
   B: The sum of their ages equals the number of the house across the street.
   A: ... What else?
   B: The oldest just got a haircut.
   A: Got it!  Their ages are...
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
        c0 = int(''.join(map(str, cube[0:2*m:2])),2)
        c1 = int(''.join(map(str, cube[2*m:4*m:2])),2)
        c2 = int(''.join(map(str, cube[4*m::2])),2)
        print('C0:', c0, 'C1:', c1, 'C2:', c2)

def reportC(title):
    """Print summary of common knowledge."""
    if args.verbose > 0:
        C.display(numVars=3*m, name=title)

def pre(TR, From):
    """Compute the predecessors of From."""
    fromY = From.swapVariables(P,Q)
    return TR.andAbstract(fromY, qcube)

def knowsFact(TR, fact):
    """Find plausible worlds where agent knows fact."""
    return fact & C & ~pre(TR, ~fact & C)

def knowsWorld(TR):
    """Find plausible worlds that agent discerns from all other worlds."""
    return C & ~pre(TR & ~mgr.xeqy(P,Q), C)

# Parse command line.
parser = argparse.ArgumentParser(
    description='Solve the three-children ages puzzle',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-v', '--verbose', help='increase output verbosity',
                    action='count', default=0)
args = parser.parse_args()

from cudd import Cudd
mgr = Cudd()

n = 3        # number of Bob's children
m = 6        # number of bits in each age
product = 36 # product possible age
rounds = 4   # 3 complete rounds + 1 incomplete round

# Each world is identified by three numbers between 0 and 36 (included).
# These numbers are the ages of the children.
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

# Initial common knowledge: p[0] <= p[1] <= p[2].  This is an assumption,
# rather than actual common knowledge.
C = ~(mgr.xgty(p[0],p[1]) | mgr.xgty(p[1],p[2]))

# World indistinguishability relations.  Alice initially cannot distinguish
# any pair of plausible worlds.
T = mgr.bddOne()

# First (public) announcement: the product of the three ages is 36.
A1 = mgr.bddZero()
for i in range(1, 1 + product):
    for j in range(i,1 + product // i):
        for k in range(j, 1 + product // (i*j)):
            if i*j*k == product:
                A1 |= ~(mgr.disequality(i, p[0], [mgr.bddZero()]*m) |
                        mgr.disequality(j, p[1], [mgr.bddZero()]*m) |
                        mgr.disequality(k, p[2], [mgr.bddZero()]*m))

C &= A1
reportC('C after A1')

# The worlds where Alice knows the three ages are those that are only
# in accessibility relation with themselves.  After the first announcement
# there are no such worlds.
K1 = knowsWorld(T)

if args.verbose > 1:
    K1.display(numVars=3*m,name='K after A1')

# After the second announcement, Alice distinguishes worlds such that the
# sum of the three ages is different.  Restrict her accessibility relation
# to pairs of worlds with the same age sum.
sumdict = {} # map from integers to BDDs
cworlds = C
while not cworlds.isZero():
    soln = cworlds.pickOneMinterm(P)
    cworlds &= ~soln
    cube = soln.pickOneCube()
    c0 = int(''.join(map(str, cube[0:2*m:2])),2)
    c1 = int(''.join(map(str, cube[2*m:4*m:2])),2)
    c2 = int(''.join(map(str, cube[4*m::2])),2)
    csum = c0+c1+c2
    if csum not in sumdict:
        sumdict[csum] = soln
    else:
        sumdict[csum] |= soln

T2 = mgr.bddZero()
for sv in sumdict.values():
    T2 |= sv & sv.swapVariables(P,Q)

T &= T2

if args.verbose > 1:
    T.display(numVars=6*m,name='T after A2')

K2 = knowsWorld(T)

if args.verbose > 1:
    K2.display(numVars=3*m,name='K after A2')

# Since Alice still doesn't know the ages after the second announcement,
# the actual world is not one in which she would know.
C &= ~K2
reportC('C after A2')

# Third announcement: there is a unique oldest child.
# G[i] is true of all worlds in which child i is the oldest.
G = [mgr.bddOne() for i in range(n)]
for i in range(n):
    for j in range(n):
        if j != i:
            G[i] &= mgr.inequality(1, p[i], p[j])

A3 = G[0] | G[1] | G[2]

# The third announcement removes all ambiguity.
C &= A3
reportC('C after A3')

print_solutions(C)
