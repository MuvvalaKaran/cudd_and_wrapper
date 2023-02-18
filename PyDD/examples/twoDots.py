"""Epistemic model checking example.  We model check another wise men puzzle.

   Each of three wise men has two colored dots on his forehead. The dots
   are either red or white.  There are at most four dots of each color.
   Each man only sees the dots on the foreheads of the other two.
   Each man is asked in turn which colors are the dots on his forehead.

   Asked which colors are his dots, no man can infer, until, on the
   second round, the second man can.  

   The conclusions of the wise men become public knowledge.  That is,
   the second and third wise men know the first could not infer on his
   first two attempts, and the third knows that the second couldn't
   infer on his first attempt.

   The second wise man always reaches the conclusion that his dots are
   one red and one white on the second round, regardless of the colors
   of other dots.

   The three men are assumed to be sound and complete reasoners as far as
   propositional logic goes.  This script is based on this assumption and
   extends the approach to any positive number of wise men.  In the case
   of n men, the number of dots of each color cannot exceed n+1.  The second
   man gets the solution for n > 2.
"""

from __future__ import print_function
from functools import reduce
import argparse

def check_number(value):
    """Check that the number of wise men is a positive integer."""
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError(
            "%s is not an integer greater than 0" % value)
    return ivalue

def conclusion(i):
    """Report the conclusion of wise man i."""
    print("Wise man", i, end=" ")
    if C == K0:
        print('knows he has no white dot.')
        return True
    elif C == K1:
        print('knows he has one white dot.')
        return True
    elif C == K2:
        print('knows he has two white dots.')
        return True
    elif C == K:
        print('always knows the color of his dots.')
        return True
    else:
        print('does not always know the color of his dots.')
        return False

def pre(TR, From):
    """Compute the predecessors of From."""
    fromY = From.swapVariables(w,u)
    return TR.andAbstract(fromY, ucube)

# Parse command line.
parser = argparse.ArgumentParser(
    description="Solve the wise man puzzle",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--number", help="number of wise men",
                    type=check_number, default=3)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)
args = parser.parse_args()

from cudd import Cudd
mgr = Cudd()

n = args.number # number of wise men
# The first dot of i is white
wf = [mgr.bddVar(4*i,   'wf' + str(i)) for i in range(n)]
# Next-world variables for first dot
uf = [mgr.bddVar(4*i+1, 'uf' + str(i)) for i in range(n)]
# The second dot of i is white
ws = [mgr.bddVar(4*i+2,   'ws' + str(i)) for i in range(n)]
# Next-world variables for second dot
us = [mgr.bddVar(4*i+3, 'us' + str(i)) for i in range(n)]
# Merge current and next-state variable lists.
w = [val for pair in zip(wf,ws) for val in pair]
u = [val for pair in zip(uf,us) for val in pair]
ucube = reduce(lambda x, y: x & y, u)

# World indistinguishability relations.  A wise man cannot distinguish two
# worlds if and only if they only differ in the colors of his dots.
T = [mgr.bddOne() for i in range(n)]
for i in range(n):
    for j in range(n):
        if j != i:
            T[i] &= wf[j].iff(uf[j]) & ws[j].iff(us[j])

# Initial common knowledge: at most n+1 dots of each color.
C = mgr.cardinality(w, n-1, n+1)
# If a wise man has only one white dot, it's the first.
for i in range(n):
    C &= ~ws[i] | wf[i]

for k in range(2*n):
    i = k % n
    K0 = C & ~pre(T[i], (wf[i] | ws[i]) & C)
    K1 = C & ~pre(T[i], wf[i].iff(ws[i]) & C)
    K2 = C & ~pre(T[i], ~(wf[i] & ws[i]) & C)
    K = K0 | K1 | K2
    if args.verbose > 0:
        print('C', end=''), C.summary(2*n), C.printCover()
        print('K'+str(i)+'_0_'+str(i)+' =', K0)
        print('K'+str(i)+'_1_'+str(i)+' =', K1)
        print('K'+str(i)+'_2_'+str(i)+' =', K2)
        print('C == K'+str(i)+str(i)+' :', C == K)
    if conclusion(i):
        break
    C &= ~K
