"""Epistemic model checking example.  We model check the wise men puzzle.

   Three wise men wear hats that are either white or red.  There are at most
   two white hats.  Each man only sees the hats worn by the other two.
   Each man is asked in turn which color is the hat he wears.

   Asked which color is his hat, the first can't infer, the second neither,
   but the third can.  The conclusions of the wise men become public knowledge.
   That is, the second and third wise men know the first could
   not infer, and the third knows that the second couldn't either.

   The third wise man always reaches the conclusion that his hat is red when
   the first two men give up, regardless of the colors of their hats.

   The three men are assumed to be sound and complete reasoners as far as
   propositional logic goes.  This script is based on this assumption and
   extends the approach to any positive number of wise men.
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
    if C == Kw:
        print('knows his hat is white.')
        return True
    elif C == Kr:
        print('knows his hat is red.')
        return True
    elif C == K:
        print('always knows the color of his hat.')
        return True
    else:
        print('does not always know the color of his hat.')
        return False

def pre(TR, From):
    """Compute the predecessors of From."""
    fromY = From.swapVariables(w,u)
    return TR.andAbstract(fromY, ucube)

def knowsFact(TR, fact):
    """Find plausible worlds where agent knows fact."""
    return fact & C & ~pre(TR, ~fact & C)

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
w = [mgr.bddVar(2*i,   'w' + str(i)) for i in range(n)] # the hat of i is white
u = [mgr.bddVar(2*i+1, 'u' + str(i)) for i in range(n)] # next-world variables
ucube = reduce(lambda x, y: x & y, u)

# World indistinguishability relations.  A wise man cannot distinguish two
# worlds if and only if they only differ in the color of his hat.
T = [mgr.bddOne() for i in range(n)]
for i in range(n):
    for j in range(n):
        if j != i:
            T[i] &= w[j].iff(u[j])

# Initial common knowledge: at least one hat is red.
C = ~reduce(lambda x, y: x & y, w)

for i in range(n):
    Kw = knowsFact(T[i], w[i])
    Kr = knowsFact(T[i], ~w[i])
    K = Kw | Kr
    if args.verbose > 0:
        print('C =', C)
        print('K'+str(i)+'w'+str(i)+' =', Kw)
        print('K'+str(i)+'r'+str(i)+' =', Kr)
        print('C == K'+str(i)+str(i)+' :', C == K)
    if conclusion(i):
        break
    C &= ~K
