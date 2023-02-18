"""Epistemic model checking example.

   Three wise men, A, B, and C, draw a card from a deck of twenty-one cards,
   each showing a distinct two-digit prime.  Each man only sees the cards
   drawn by the other two.  Each man is asked in turn two questions:

     1. Is your number the smallest of the three?
     2. Is your number the largest of the three?

   The answers of the wise men become public knowledge.  The three men
   are sound and complete reasoners as far as propositional logic goes.

   For three rounds all three men answer "I don't know" to both questions.
   On the fourth round, A answers "I don't know" to the first question.

   How does A answer the second question, and what numbers are on B's 
   and C's cards?
"""

from __future__ import print_function, division, unicode_literals
from functools import reduce
import argparse
# Ugliness to ensure Python 2/3 compatibility.
try:
    from math import log2, ceil
except ImportError:
    from math import log
    from math import ceil as fceil
    def log2(x):
        return log(x,2)
    def ceil(x):
        return int(fceil(x))

# List of two-digit primes.
primes = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
          53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

def print_solutions(solutions):
    """Convert common-knowledge BDD to list of solutions."""
    while not solutions.isZero():
        soln = solutions.pickOneMinterm(P) # ignore next-state variables
        solutions &= ~soln
        cube = soln.pickOneCube()          # convert to list of 0s and 1s
        a = int(''.join(map(str, cube[0:2*m:2])),2)
        b = int(''.join(map(str, cube[2*m:4*m:2])),2)
        c = int(''.join(map(str, cube[4*m::2])),2)
        print('A:', primes[a], 'B:', primes[b], 'C:', primes[c])

def pre(TR, From):
    """Compute the predecessors of From."""
    fromY = From.swapVariables(P,Q)
    return TR.andAbstract(fromY, qcube)

def knowsFact(TR, fact):
    """Find plausible worlds where agent knows fact."""
    return fact & C & ~pre(TR, ~fact & C)

# Parse command line.
parser = argparse.ArgumentParser(
    description="Solve the two-digit prime puzzle",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)
args = parser.parse_args()

from cudd import Cudd
mgr = Cudd()

n = 3                       # number of wise men
m = ceil(log2(len(primes))) # number of bits in each rank
largest = len(primes)-1     # largest rank
rounds = 4                  # 3 complete rounds + 1 incomplete round

# Each world is identified by three numbers between 0 and 20 (included).
# These numbers are the ranks of the two-digit primes: 0 corresponds to 11
# and 20 corresponds to 97.
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

# World indistinguishability relations.  A wise man cannot distinguish two
# worlds if and only if they only differ in the card he has drawn.
T = [mgr.bddOne() for i in range(n)]
for i in range(n):
    for j in range(n):
        if j != i:
            T[i] &= mgr.xeqy(p[j], q[j])

# Initial common knowledge: in all possible worlds each card carries one of
# the twentyone two-digit primes and no two cards carry the same number.
# As the computation evolves, C describes the set of worlds that do not
# contradict the answers of the wise men.
C = mgr.bddOne()
for i in range(n):
    C &= mgr.interval(p[i], 0, largest)
    for j in range(i+1,n):
        C &= ~mgr.xeqy(p[i], p[j])

# L[i] is true of all worlds in which wise man i has the least number.
# G[i] is true of all worlds in which wise man i has the greatest number.
L = [mgr.bddOne() for i in range(n)]
G = [mgr.bddOne() for i in range(n)]
for i in range(n):
    for j in range(n):
        if j != i:
            L[i] &= mgr.inequality(1, p[j], p[i])
            G[i] &= mgr.inequality(1, p[i], p[j])

for round in range(rounds):
    if args.verbose > 0:
        print('Possible worlds before round', round, '=', C.count(numVars=n*m))
    for i in range(n):
        # Worlds where wise man i knows he has the least number.
        Kl = knowsFact(T[i], L[i])
        # Worlds where wise man i knows he doens't have the least number.
        Knl = knowsFact(T[i], ~L[i])
        # Since the answer is "I don't know," the worlds in which wise
        # man i would know the answer are now deemed impossible.
        C &= ~(Kl | Knl)
        if round == rounds-1 and i == 0:
            break
        # Worlds where wise man i knows he has the greatest number.
        Kg = knowsFact(T[i], G[i])
        # Worlds where wise man i knows he doens't have the greatest number.
        Kng = knowsFact(T[i], ~G[i])
        # Update common knowledge based on "I don't know" answer.
        C &= ~(Kg | Kng)

# Final common knowledge shows that the number of B and C are known and that
# A knows he doesn't have the largest number.  He doesn't know whether he
# has the smallest number, because there are still two possible worlds.

print_solutions(C)
