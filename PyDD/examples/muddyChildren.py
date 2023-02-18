"""Epistemic model checking of the muddy children puzzle.
   
   The children are assumed to be sound and complete reasoners as far as
   propositional logic goes.  This script is based on this assumption.

   This problem features an assumption about the possible worlds that is
   not common knowledge.  Specifically, we can assume the maximum number
   of muddy foreheads.  This allows us to check whether the muddy children
   would know they have mud on their foreheads in the expected number
   of rounds.

   If a child knows her forehead is muddy in all worlds that satisfy the
   assumption where indeed her forehead is muddy, then this child will 
   answer whenever the assumption is satisfied.
"""

from __future__ import print_function, division, unicode_literals
from functools import reduce
import argparse

def check_number(value):
    """Check that a number is a positive integer."""
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError(
            "%s is not an integer greater than 0" % value)
    return ivalue

def conclusion(i):
    """Report the conclusion of child i."""
    if C.leqUnless(K[i],~A):
        print('Child', i, 'would always know whether her forehead was muddy.')
        return True
    elif (C&w[i]).leqUnless(Km[i],~A):
        print('If her forehead is muddy, Child', i, 'knows.')
        return True
    elif (C&~w[i]).leqUnless(Kc[i],~A):
        print('If her forehead is clean, Child', i, 'knows.')
        return True
    else:
        print('Child', i, 'would not always know whether her forehead was muddy.')
        return False

def print_solutions(solutions):
    """Convert common-knowledge BDD to list of solutions."""
    converter = lambda x : "-" if x == 2 else str(x)
    for cube in solutions.generate_primes():
        print(' '.join(map(converter, cube[0::2])))

def pre(TR, From):
    """Compute the predecessors of From."""
    fromY = From.swapVariables(w,u)
    return TR.andAbstract(fromY, ucube)

def knowsFact(TR, fact):
    """Find plausible worlds where agent knows fact."""
    return fact & C & ~pre(TR, ~fact & C)

# Parse command line.
parser = argparse.ArgumentParser(
    description="Solve the muddy children puzzle",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--number", help="number of children",
                    type=check_number, default=3)
parser.add_argument("-r", "--rounds", help="number of rounds",
                    type=check_number, default=2)
parser.add_argument("-f", "--foreheads", help="maximum number of muddy foreheads",
                    type=check_number, default=3)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)
args = parser.parse_args()

from cudd import Cudd
mgr = Cudd()

n = args.number # number of children
w = [mgr.bddVar(2*i,   'w' + str(i)) for i in range(n)] # the forehead of i is muddy
u = [mgr.bddVar(2*i+1, 'u' + str(i)) for i in range(n)] # next-world variables
ucube = reduce(lambda x, y: x & y, u)

# World indistinguishability relations.  A child cannot distinguish two
# worlds if and only if they only differ in the muddiness of her forehead.
T = [mgr.bddOne() for i in range(n)]
for i in range(n):
    for j in range(n):
        if j != i:
            T[i] &= w[j].iff(u[j])

# Initial common knowledge: at least one forehead is muddy.
C = reduce(lambda x, y: x | y, w)

# Assumption
A = mgr.cardinality(w, 1, args.foreheads)

for round in range(args.rounds):
    print('Possible worlds before round', round, '=', C.count(numVars=n))
    if args.verbose > 1:
        C.display(numVars=n, name='C')
    Km = [None for i in range(n)]
    Kc = [None for i in range(n)]
    K  = [None for i in range(n)]
    done = False
    for i in range(n):
        Km[i] = knowsFact(T[i], w[i])
        Kc[i] = knowsFact(T[i], ~w[i])
        K[i]  = Km[i] | Kc[i]
        if args.verbose > 1:
            Km[i].display(numVars=n, name='K'+str(i)+'m'+str(i))
            Kc[i].display(numVars=n, name='K'+str(i)+'c'+str(i))
            print('C&w[i] -> K'+str(i)+str(i)+' when A :', (C&w[i]).leqUnless(K[i],~A))
        if conclusion(i):
            done = True
    if done:
        break
    # All children remain silent.
    for i in range(n):
        C &= ~K[i]

C.summary(numVars=n, name='Final common knowledge')
print('Solutions under given assumption:')
print_solutions(C & A)
