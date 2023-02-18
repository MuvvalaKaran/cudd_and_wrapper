"""Epistemic model checking example.  Dining cryptographers.

  n > 2 cryptographers are seated around a restaurant table

  It is announced that secret arrangements have been made to take care
  of the check.  It is known that either one of the cryptographers or
  the NSA is going to pay.

  The cryptographers execute this protocol.  Each tosses a coin and
  shows it to her right neighbor.  Then each cryptographer announces
  the parity of the two coins in her view.

  A cryptographer makes a truthful announcement if and only if she is
  not taking care of the bill.

  The parity of the parities is even if and only if the NSA is paying,
  since each coin is counted twice.

  Does the protocol leak confidential information?

  We want to show that after the protocol has been executed, every
  cryptographer knows whether the NSA paid, but in case it didn't, the
  cryptographers who didn't pay don't know who did.
"""

from __future__ import print_function
from functools import reduce
import argparse

def check_number(value):
    """Check that the number of cryptographers is an integer greater than 2."""
    ivalue = int(value)
    if ivalue < 3:
        raise argparse.ArgumentTypeError(
            "%s is not an integer greater than 2" % value)
    return ivalue

def pre(TR, From):
    """Compute the predecessors of From."""
    fromY = From.swapVariables(x,y)
    return TR.andAbstract(fromY, ycube)

def knows(i, fact):
    """Compute worlds where agent i knows fact."""
    return fact & C & ~pre(T[i], ~fact & C)

# Utility lambdas.
nxt = lambda k: (k+1) % n
conjoin = lambda u, v: u & v
disjoin = lambda u, v: u | v

# Parse command line.
parser = argparse.ArgumentParser(
    description="Solve the dining cryptographers puzzle",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--number", help="number of cryptographers",
                    type=check_number, default=3)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="count", default=0)
parser.add_argument("-r", "--reorder", help="dynamically reorder BDD variables",
                    action="store_true")
args = parser.parse_args()

# Start BDD manager.
from cudd import Cudd
mgr = Cudd()

if args.reorder:
    mgr.autodynEnable()
    if args.verbose > 0:
        mgr.enableReorderingReporting()

n = args.number # number of cryptographers

# State variables and "other-world" variables.
c  = [mgr.bddVar(6*i,   'c'  + str(i)) for i in range(n)] # the coins tossed
cn = [mgr.bddVar(6*i+1, 'cn' + str(i)) for i in range(n)] # other-world vars
b  = [mgr.bddVar(6*i+2, 'b'  + str(i)) for i in range(n)] # got the bill
bn = [mgr.bddVar(6*i+3, 'bn' + str(i)) for i in range(n)] # other-world vars
p  = [mgr.bddVar(6*i+4, 'p'  + str(i)) for i in range(n)] # announced parity
pn = [mgr.bddVar(6*i+5, 'pn' + str(i)) for i in range(n)] # other-world vars

x = c + b + p
y = cn + bn + pn
ycube = reduce(conjoin, y)

# World indistinguishability relations.  A cryptographer cannot
# distinguish two worlds if and only if they only differ in
#  1. the parity of coins she does not see, or
#  2. the identity of who paid the bill (as long as she did not pay herself)
T = [mgr.bddOne() for i in range(n)]
for i in range(n):
    T[i] &= c[i].iff(cn[i]) & c[nxt(i)].iff(cn[nxt(i)])
    T[i] &= b[i].iff(bn[i])
    T[i] &= reduce(conjoin, (p[j].iff(pn[j]) for j in range(n)))

# Initial common knowledge.
# Announced parity is truthful if and only if cryptographer didn't pay.
C = reduce(conjoin, (p[i].iff(b[i] ^ c[i] ^ c[nxt(i)]) for i in range(n)))
# At most one cryptographer paid.
C &= mgr.cardinality(b,0,1)

if args.verbose > 0:
    C.display(3*n,args.verbose,'C')

odd = reduce(lambda u, v: u ^ v, p)

# What the cryptographers know.
K = C # start with common knowledge

for i in range(n):
    # Worlds where cryptographer i knows that another cryptographer paid
    Ksp = knows(i, reduce(disjoin, (b[j] for j in range(n) if j != i)))
    # Worlds where cryptographer i doesn't know whether cryptographer j paid
    nKp = reduce(conjoin, (~knows(i, b[j]) for j in range(n) if j != i))
    K &= ~odd | b[i] | Ksp & nKp

# No secret leaked if no one learned anything beyond what was common knowledge.
print(('No' if C == K else 'Some') + ' secret was leaked.')

if args.reorder and args.verbose > 0:
    print(mgr.bddOrder())
